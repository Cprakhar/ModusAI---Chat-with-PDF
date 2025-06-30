"use client"

import { useState, useEffect, useRef } from "react"
import { Send, Bot, User, FileText, ToggleLeft, ToggleRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { CitationPanel } from "@/components/citation-panel"

interface ChatInterfaceProps {
  selectedConversation: string | null
  selectedPDF?: string | null // Optional prop for selected PDF
}

interface Message {
  id: string
  type: "user" | "ai"
  content: string
  timestamp?: string
  citations?: Citation[]
}

interface Citation {
  id: string
  page: number
  snippet: string
  relevance: number
}

export function ChatInterface({ selectedConversation, selectedPDF }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isDeepDive, setIsDeepDive] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCitations, setSelectedCitations] = useState<Citation[]>([])
  const [showCitations, setShowCitations] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch conversation history when selectedConversation changes
  useEffect(() => {
    if (!selectedConversation) {
      setMessages([])
      return
    }
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("token")
        const res = await fetch(`/api/conversations/${selectedConversation}`, {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        })
        if (!res.ok) {
          setMessages([])
          return
        }
        const data = await res.json()
        // Map backend messages to UI format
        const mapped = (data.history || []).map((msg: any, idx: number) => ({
          id: msg.id || idx.toString(),
          type: msg.role === "user" ? "user" : "ai",
          content: msg.content,
          timestamp: msg.timestamp || "",
          citations: msg.citations || [],
        }))
        // If no messages, show a starter message
        if (mapped.length === 0) {
          setMessages([
            {
              id: "starter",
              type: "ai",
              content: "Welcome! Ask any question about your PDF to get started.",
            },
          ])
        } else {
          setMessages(mapped)
        }
      } catch (e) {
        setMessages([])
      }
    }
    fetchHistory()
  }, [selectedConversation])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !selectedConversation) return

    const newMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, newMessage])
    setInputValue("")
    setIsLoading(true)

    if (isDeepDive) {
      // Deep-dive mode: stream via WebSocket (send JSON payload)
      const documentId = selectedPDF || selectedConversation;
      if (!documentId) {
        setIsLoading(false)
        alert("Please select a PDF or conversation for deep-dive mode.")
        return
      }
      try {
        const token = localStorage.getItem("token")
        console.log("[DeepDive] JWT token sent:", token)
        const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws"
        // Use backend port for WebSocket in dev (bypass Next.js proxy)
        let wsUrl = '';
        if (window.location.hostname === "localhost" && window.location.port === "3000") {
          wsUrl = `${wsProtocol}://localhost:8000/api/v1/chat/deep_query/stream`;
        } else {
          wsUrl = `${wsProtocol}://${window.location.host}/api/chat/deep_query/stream`;
        }
        const ws = new WebSocket(wsUrl)
        const aiMessageId = (Date.now() + 1).toString()
        let aiMessage: Message = {
          id: aiMessageId,
          type: "ai",
          content: "",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          citations: [],
        }
        setMessages((prev) => [...prev, aiMessage])
        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              document_id: documentId, // Use selectedPDF or fallback to selectedConversation
              query: newMessage.content,
              token,
            })
          )
        }
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.token) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === aiMessageId
                  ? { ...msg, content: msg.content + data.token }
                  : msg
              )
            )
          }
          if (data.citations) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === aiMessageId
                  ? { ...msg, citations: data.citations }
                  : msg
              )
            )
            setSelectedCitations(data.citations)
          }
          if (data.done) {
            setIsLoading(false)
            ws.close()
          }
          if (data.error) {
            setIsLoading(false)
            setMessages((prev) => prev.filter((msg) => msg.id !== aiMessageId))
            alert(data.error)
            ws.close()
          }
        }
        ws.onerror = () => {
          setIsLoading(false)
          setMessages((prev) => prev.filter((msg) => msg.id !== aiMessageId))
          alert("WebSocket error during deep-dive.")
          ws.close()
        }
        ws.onclose = () => {
          setIsLoading(false)
        }
      } catch (err) {
        setIsLoading(false)
        setMessages((prev) => prev.filter((msg) => msg.id !== newMessage.id))
        alert("Deep-dive failed. Please try again.")
      }
      return
    }

    // Streaming AI response via WebSocket (multi-turn)
    let aiMessageId = (Date.now() + 1).toString()
    let aiMessage: Message = {
      id: aiMessageId,
      type: "ai",
      content: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      citations: [],
    }
    setMessages((prev) => [...prev, aiMessage])

    try {
      const token = localStorage.getItem("token")
      console.log("[MultiTurn] JWT token sent:", token)
      const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws"
      // FIX: Use /api/chat/stream (no /v1)
      const wsUrl = `${wsProtocol}://${window.location.host}/api/chat/stream?conversation_id=${selectedConversation}&message=${encodeURIComponent(inputValue)}&token=${token}`
      const ws = new WebSocket(wsUrl)

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.token) {
          // Append streamed token to the last AI message
          setMessages((prev) => {
            return prev.map((msg) =>
              msg.id === aiMessageId
                ? { ...msg, content: msg.content + data.token }
                : msg
            )
          })
        }
        if (data.citations) {
          setMessages((prev) => {
            return prev.map((msg) =>
              msg.id === aiMessageId
                ? { ...msg, citations: data.citations }
                : msg
            )
          })
          setSelectedCitations(data.citations)
        }
        if (data.done) {
          setIsLoading(false)
          ws.close()
        }
        if (data.error) {
          setIsLoading(false)
          setMessages((prev) => prev.filter((msg) => msg.id !== aiMessageId))
          alert(data.error)
          ws.close()
        }
      }
      ws.onerror = () => {
        setIsLoading(false)
        setMessages((prev) => prev.filter((msg) => msg.id !== aiMessageId))
        alert("WebSocket error. Please try again.")
        ws.close()
      }
      ws.onclose = () => {
        setIsLoading(false)
      }
    } catch (err) {
      setIsLoading(false)
      alert("Failed to connect to chat stream.")
    }
  }

  const handleCitationClick = (citation: Citation) => {
    console.log("Navigate to citation:", citation)
  }

  return (
    <div className="h-screen flex">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Header - Fixed */}
        {selectedConversation && (
          <div className="flex-shrink-0 p-4 border-b border-gray-700 bg-[#232326]">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <h1 className="text-xl font-bold text-white truncate">
                  Research Paper Analysis
                </h1>
                <p className="text-gray-400 text-sm">Chat with your PDF documents</p>
              </div>

              {/* Mode Toggle */}
              <div className="flex items-center space-x-3 flex-shrink-0 ml-4">
                <span className="text-sm text-gray-400">Multi-turn</span>
                <Button variant="ghost" size="sm" className="p-1" onClick={() => setIsDeepDive(!isDeepDive)}>
                  {isDeepDive ? (
                    <ToggleRight className="h-6 w-6 text-[#FFB020]" />
                  ) : (
                    <ToggleLeft className="h-6 w-6 text-gray-400" />
                  )}
                </Button>
                <span className="text-sm text-gray-400">Deep-dive</span>

                {/* Citations Toggle */}
                {selectedCitations.length > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-gray-600 text-white hover:bg-gray-700 bg-transparent ml-2"
                    onClick={() => setShowCitations(!showCitations)}
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    Citations ({selectedCitations.length})
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Messages - Scrollable */}
        <div className="flex-1 overflow-y-auto min-h-0">
          <div className="p-4 pb-6">
            <div className="space-y-4 max-w-4xl mx-auto">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`flex max-w-[80%] ${message.type === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    {/* Avatar */}
                    <div className={`flex-shrink-0 ${message.type === "user" ? "ml-3" : "mr-3"}`}>
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.type === "user" ? "bg-[#FFB020]" : "bg-[#2C2C2E]"
                        }`}
                      >
                        {message.type === "user" ? (
                          <User className="h-4 w-4 text-black" />
                        ) : (
                          <Bot className="h-4 w-4 text-[#FFB020]" />
                        )}
                      </div>
                    </div>

                    {/* Message Content */}
                    <div
                      className={`rounded-2xl px-4 py-3 ${
                        message.type === "user"
                          ? "bg-[#FFB020] text-black"
                          : "bg-[#232326] text-white border border-gray-700"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>

                      {/* Citations */}
                      {message.citations && message.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-600">
                          <div className="flex flex-wrap gap-2">
                            {message.citations.map((citation, idx) => (
                              <Badge
                                key={citation.id ?? idx}
                                variant="secondary"
                                className="bg-[#FFB020]/20 text-[#FFB020] hover:bg-[#FFB020]/30 cursor-pointer text-xs"
                                onClick={() => {
                                  setSelectedCitations(message.citations || [])
                                  setShowCitations(true)
                                }}
                              >
                                <FileText className="h-3 w-3 mr-1" />
                                Page {citation.page}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex mr-3">
                    <div className="w-8 h-8 rounded-full bg-[#2C2C2E] flex items-center justify-center">
                      <Bot className="h-4 w-4 text-[#FFB020]" />
                    </div>
                  </div>
                  <div className="bg-[#232326] rounded-2xl px-4 py-3 border border-gray-700">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-[#FFB020] rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-[#FFB020] rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-[#FFB020] rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="flex-shrink-0 p-4 border-t border-gray-700 bg-[#232326]">
          <div className="max-w-4xl mx-auto">
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={`Ask a question about your PDF... (${isDeepDive ? "Deep-dive" : "Multi-turn"} mode)`}
                  className="bg-[#1C1C1E] border-gray-600 text-white placeholder-gray-400 pr-12 rounded-xl"
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                />
              </div>
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="bg-[#FFB020] hover:bg-[#FFD700] text-black rounded-xl px-6"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>

            {isDeepDive && (
              <p className="text-xs text-gray-400 mt-2 text-center">
                Deep-dive mode provides comprehensive, single-turn responses with extensive citations
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Citation Panel - Only show when toggled */}
      {showCitations && selectedCitations.length > 0 && (
        <div className="flex-shrink-0 w-80 border-l border-gray-700 h-screen">
          <CitationPanel
            citations={selectedCitations}
            onCitationClick={(citation) => console.log("Navigate to citation:", citation)}
            onClose={() => setShowCitations(false)}
          />
        </div>
      )}
    </div>
  )
}
