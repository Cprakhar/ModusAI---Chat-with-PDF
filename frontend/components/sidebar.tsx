"use client"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { FileText, MessageSquare, Settings, Upload, User, LogOut, Loader2, Trash2, Plus } from "lucide-react"

interface ConversationItem {
  id: string
  title: string
  lastMessage: string
  date: string
}

interface DocumentItem {
  document_id: string;
  name: string;
  upload_time: string;
}

interface SidebarProps {
  activeView: "documents" | "chat"
  setActiveView: (view: "documents" | "chat") => void
  selectedPDF: string | null
  setSelectedPDF: (id: string | null) => void
  selectedConversation: string | null
  setSelectedConversation: (id: string | null) => void
  onLogout: () => void
  onPDFUpload?: (file: File) => void
  refreshDocs?: number
  fetchDocuments: () => void
  documents: DocumentItem[]
  uploading: boolean
}

export function Sidebar({
  activeView,
  setActiveView,
  selectedPDF,
  setSelectedPDF,
  selectedConversation,
  setSelectedConversation,
  onLogout,
  onPDFUpload,
  refreshDocs,
  fetchDocuments,
  documents,
  uploading,
}: SidebarProps) {
  const [conversations, setConversations] = useState<ConversationItem[]>([])
  const [loadingConvos, setLoadingConvos] = useState(false)

  useEffect(() => {
    if (activeView === "chat") {
      const fetchConversations = async () => {
        setLoadingConvos(true)
        try {
          const token = localStorage.getItem("token")
          const res = await fetch("/api/conversations", {
            headers: {
              Authorization: token ? `Bearer ${token}` : "",
            },
          })
          if (res.ok) {
            const data = await res.json()
            setConversations(data.conversations || [])
          } else {
            setConversations([])
          }
        } catch {
          setConversations([])
        }
        setLoadingConvos(false)
      }
      fetchConversations()
    }
  }, [activeView, refreshDocs])

  useEffect(() => {
    const handler = (e: any) => {
      if (e.detail && e.detail.documentId) {
        setSelectedPDF(e.detail.documentId);
        setActiveView('chat');
      }
    };
    window.addEventListener('start-chat', handler);
    return () => window.removeEventListener('start-chat', handler);
  }, [setSelectedPDF, setActiveView]);

  return (
    <div className="w-80 bg-[#232326] border-r border-gray-700 flex flex-col h-screen">
      <div className="flex-shrink-0 p-4 border-b border-gray-700 flex items-center justify-between bg-gradient-to-r from-[#232326] to-[#1C1C1E]">
        <div className="flex items-center space-x-3">
          <div>
            <h1 className="text-2xl font-bold text-white leading-tight">Chat with PDF</h1>
            <p className="text-xs text-gray-400">Your AI-powered document assistant</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            className="bg-[#FFB020] hover:bg-[#FFD700] text-black font-medium rounded-xl"
            onClick={() => {
              const fileInput = document.getElementById("pdf-upload") as HTMLInputElement
              fileInput?.click()
            }}
            disabled={uploading}
          >
            {uploading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : <Upload className="h-4 w-4" />}
            {uploading ? "Uploading..." : ""}
          </Button>
          <input
            id="pdf-upload"
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0]
              if (file && onPDFUpload) {
                onPDFUpload(file)
                fetchDocuments()
                e.target.value = ""
              }
            }}
          />
        </div>
      </div>

      <div className="flex-shrink-0 p-4">
        <div className="flex space-x-1 bg-[#1C1C1E] rounded-xl p-1">
          <Button
            variant={activeView === "documents" ? "default" : "ghost"}
            size="sm"
            className={`flex-1 rounded-lg ${
              activeView === "documents"
                ? "bg-[#FFB020] text-black hover:bg-[#FFD700]"
                : "text-gray-400 hover:text-white hover:bg-gray-700"
            }`}
            onClick={() => setActiveView("documents")}
          >
            <FileText className="mr-2 h-4 w-4" />
            PDFs
          </Button>
          <Button
            variant={activeView === "chat" ? "default" : "ghost"}
            size="sm"
            className={`flex-1 rounded-lg ${
              activeView === "chat"
                ? "bg-[#FFB020] text-black hover:bg-[#FFD700]"
                : "text-gray-400 hover:text-white hover:bg-gray-700"
            }`}
            onClick={() => setActiveView("chat")}
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            Chats
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {activeView === "documents" ? (
          <div className="space-y-2">
            {documents.length === 0 ? (
              <div className="text-gray-400">No documents uploaded yet.</div>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.document_id}
                  className={`p-3 rounded-xl border cursor-pointer transition-colors ${
                    selectedPDF === doc.document_id
                      ? "bg-[#FFB020]/10 border-[#FFB020]"
                      : "bg-[#2C2C2E] border-gray-600 hover:border-gray-500"
                  }`}
                  onClick={() => setSelectedPDF(doc.document_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white truncate">{doc.name || doc.document_id}</h3>
                      <p className="text-xs text-gray-400">Uploaded: {doc.upload_time ? new Date(doc.upload_time).toLocaleString() : ""}</p>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <button
                        className="ml-2 p-0 rounded hover:bg-yellow-600/20"
                        title="Start new chat for this PDF"
                        onClick={e => {
                          e.stopPropagation();
                          if (typeof window !== 'undefined') {
                            const event = new CustomEvent('start-chat', { detail: { documentId: doc.document_id } });
                            window.dispatchEvent(event);
                          }
                        }}
                      >
                        <Plus className="h-4 w-4 text-[#FFB020]" />
                      </button>
                      <button
                        className="ml-2 p-0 rounded hover:bg-red-600/20"
                        title="Delete PDF"
                        onClick={async e => {
                          e.stopPropagation();
                          if (!window.confirm("Delete this document?")) return;
                          const token = localStorage.getItem("token");
                          const res = await fetch(`/api/documents/${doc.document_id}`, {
                            method: "DELETE",
                            headers: {
                              Authorization: token ? `Bearer ${token}` : "",
                            },
                          });
                          if (res.ok) {
                            fetchDocuments();
                            if (selectedPDF === doc.document_id) setSelectedPDF(null);
                            setConversations(prevConvs => {
                              const toDelete = prevConvs.filter(c => c.title && c.title.includes(doc.document_id));
                              toDelete.forEach(async (conv) => {
                                await fetch(`/api/conversations/${conv.id}`, {
                                  method: "DELETE",
                                  headers: {
                                    Authorization: token ? `Bearer ${token}` : "",
                                  },
                                });
                              });
                              return prevConvs.filter(c => !c.title || !c.title.includes(doc.document_id));
                            });
                            if (selectedConversation && conversations.some(c => c.title && c.title.includes(doc.document_id))) {
                              setSelectedConversation(null);
                            }
                          } else {
                            alert("Failed to delete document.");
                          }
                        }}
                      >
                        <Trash2 className="h-4 w-4 text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {loadingConvos ? (
              <div className="text-gray-400 animate-pulse">Loading conversations...</div>
            ) : conversations.length === 0 ? (
              <div className="text-gray-400">No conversations found.</div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`p-3 rounded-xl border cursor-pointer transition-colors ${
                    selectedConversation === conv.id
                      ? "bg-[#FFB020]/10 border-[#FFB020]"
                      : "bg-[#2C2C2E] border-gray-600 hover:border-gray-500"
                  }`}
                  onClick={() => setSelectedConversation(conv.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white truncate">{conv.title || conv.id}</h3>
                      <p className="text-xs text-gray-400">
                        {conv.lastMessage ? conv.lastMessage.slice(0, 36) + (conv.lastMessage.length > 36 ? '…' : '') : ''}
                      </p>
                      <p className="text-xs text-gray-500">{conv.date}</p>
                    </div>
                    <button
                      className="ml-2 p-1 rounded hover:bg-red-600/20"
                      title="Delete conversation"
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (!window.confirm("Delete this conversation?")) return;
                        const token = localStorage.getItem("token");
                        const res = await fetch(`/api/conversations/${conv.id}`, {
                          method: "DELETE",
                          headers: {
                            Authorization: token ? `Bearer ${token}` : "",
                          },
                        });
                        if (res.ok) {
                          setConversations((prev) => prev.filter((c) => c.id !== conv.id));
                          if (selectedConversation === conv.id) setSelectedConversation(null);
                        } else {
                          alert("Failed to delete conversation.");
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-red-400 p-0" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div className="flex-shrink-0 p-4 border-t border-gray-700">
        <Button
          variant="outline"
          size="sm"
          className="w-full border-gray-600 text-white hover:bg-gray-700 bg-transparent"
          onClick={onLogout}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}
