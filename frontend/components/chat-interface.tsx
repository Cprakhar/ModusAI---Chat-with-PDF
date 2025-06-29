"use client"

import { useState, useEffect, useRef } from "react"
import { Send, Bot, User, FileText, ToggleLeft, ToggleRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { CitationPanel } from "@/components/citation-panel"
import { FloatingActionButton } from "@/components/floating-action-button"

interface ChatInterfaceProps {
  selectedConversation: string | null
}

interface Message {
  id: string
  type: "user" | "ai"
  content: string
  timestamp: string
  citations?: Citation[]
}

interface Citation {
  id: string
  page: number
  snippet: string
  relevance: number
}

const mockMessages: Message[] = [
  {
    id: "1",
    type: "user",
    content: "What are the main findings of this research paper?",
    timestamp: "10:30 AM",
  },
  {
    id: "2",
    type: "ai",
    content:
      "Based on the research paper, there are several key findings:\n\n1. **Machine Learning Efficacy**: The study demonstrates that ML algorithms can improve diagnostic accuracy by 23% compared to traditional methods.\n\n2. **Cost Reduction**: Implementation of AI-driven healthcare solutions resulted in a 15% reduction in operational costs.\n\n3. **Patient Outcomes**: Patient satisfaction scores increased by 18% when AI-assisted diagnosis was used.\n\nThese findings suggest significant potential for AI integration in healthcare systems.",
    timestamp: "10:31 AM",
    citations: [
      { id: "1", page: 12, snippet: "ML algorithms showed 23% improvement in diagnostic accuracy...", relevance: 0.95 },
      {
        id: "2",
        page: 18,
        snippet: "Cost analysis revealed 15% reduction in operational expenses...",
        relevance: 0.87,
      },
      { id: "3", page: 24, snippet: "Patient satisfaction metrics improved by 18%...", relevance: 0.82 },
    ],
  },
  {
    id: "3",
    type: "user",
    content: "Can you provide more details about the cost reduction analysis?",
    timestamp: "10:32 AM",
  },
  {
    id: "4",
    type: "ai",
    content:
      "The cost reduction analysis in the study reveals several key areas where AI implementation led to significant savings:\n\n**Operational Efficiency**: AI-driven automation reduced manual processing time by 40%, leading to substantial labor cost savings.\n\n**Diagnostic Accuracy**: Improved accuracy reduced the need for repeat tests and procedures, saving approximately $2.3M annually across the study hospitals.\n\n**Resource Optimization**: AI-powered scheduling and resource allocation improved utilization rates by 25%, reducing waste and overhead costs.\n\nThe study tracked these metrics over 18 months across 12 healthcare facilities.",
    timestamp: "10:33 AM",
    citations: [
      { id: "4", page: 19, snippet: "Operational efficiency improvements through AI automation...", relevance: 0.93 },
      { id: "5", page: 21, snippet: "Cost savings analysis across multiple healthcare facilities...", relevance: 0.89 },
    ],
  },
]

export function ChatInterface({ selectedConversation }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(mockMessages)
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

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, newMessage])
    setInputValue("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: `This is a ${isDeepDive ? "deep-dive" : "multi-turn"} response to: "${inputValue}"\n\nI would analyze the PDF content and provide a comprehensive answer based on the document context. This response demonstrates how the chat interface handles longer conversations and maintains proper scrolling behavior.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        citations: [
          { id: "1", page: 5, snippet: "Relevant excerpt from page 5...", relevance: 0.92 },
          { id: "2", page: 12, snippet: "Supporting information from page 12...", relevance: 0.85 },
        ],
      }
      setMessages((prev) => [...prev, aiResponse])
      setSelectedCitations(aiResponse.citations || [])
      setIsLoading(false)
    }, 2000)
  }

  const handleCitationClick = (citation: Citation) => {
    console.log("Navigate to citation:", citation)
  }

  return (
    <div className="h-screen flex">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Header - Fixed */}
        <div className="flex-shrink-0 p-4 border-b border-gray-700 bg-[#232326]">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <h1 className="text-xl font-bold text-white truncate">
                {selectedConversation ? "Research Paper Analysis" : "New Conversation"}
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
                            {message.citations.map((citation) => (
                              <Badge
                                key={citation.id}
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

                      <div className={`text-xs mt-2 ${message.type === "user" ? "text-black/70" : "text-gray-400"}`}>
                        {message.timestamp}
                      </div>
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

      {/* Floating Action Button - Fixed within chat interface */}
      <FloatingActionButton
        onNewChat={() => {
          // Handle new chat creation
          console.log("Starting new chat")
        }}
      />
    </div>
  )
}
