"use client"

import { useState } from "react"
import { FileText, MessageSquare, Settings, Upload, User, LogOut, Trash2, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface SidebarProps {
  activeView: "documents" | "chat"
  setActiveView: (view: "documents" | "chat") => void
  selectedPDF: string | null
  setSelectedPDF: (id: string | null) => void
  selectedConversation: string | null
  setSelectedConversation: (id: string | null) => void
  onLogout: () => void
  onPDFUpload?: (file: File) => void
}

// Mock data
const mockPDFs = [
  { id: "1", name: "Research Paper.pdf", size: "2.4 MB", uploadDate: "2024-01-15" },
  { id: "2", name: "Technical Manual.pdf", size: "5.1 MB", uploadDate: "2024-01-14" },
  { id: "3", name: "Financial Report.pdf", size: "1.8 MB", uploadDate: "2024-01-13" },
  { id: "4", name: "User Guide.pdf", size: "3.2 MB", uploadDate: "2024-01-12" },
  { id: "5", name: "API Documentation.pdf", size: "4.7 MB", uploadDate: "2024-01-11" },
  { id: "6", name: "Marketing Report.pdf", size: "2.1 MB", uploadDate: "2024-01-10" },
]

const mockConversations = [
  { id: "1", title: "Research Paper Analysis", lastMessage: "What are the key findings?", date: "2024-01-15" },
  { id: "2", title: "Technical Questions", lastMessage: "Explain the implementation details", date: "2024-01-14" },
  { id: "3", title: "Financial Overview", lastMessage: "Summarize Q4 results", date: "2024-01-13" },
  {
    id: "4",
    title: "User Experience Discussion",
    lastMessage: "How can we improve the interface?",
    date: "2024-01-12",
  },
  { id: "5", title: "API Integration Help", lastMessage: "Need help with authentication", date: "2024-01-11" },
  { id: "6", title: "Marketing Strategy", lastMessage: "Review the campaign metrics", date: "2024-01-10" },
]

export function Sidebar({
  activeView,
  setActiveView,
  selectedPDF,
  setSelectedPDF,
  selectedConversation,
  setSelectedConversation,
  onLogout,
  onPDFUpload,
}: SidebarProps) {
  const [pdfs, setPdfs] = useState(mockPDFs)
  const [conversations, setConversations] = useState(mockConversations)

  const handleDeletePDF = (id: string) => {
    setPdfs(pdfs.filter((pdf) => pdf.id !== id))
    if (selectedPDF === id) {
      setSelectedPDF(null)
    }
  }

  const handleDeleteConversation = (id: string) => {
    setConversations(conversations.filter((conv) => conv.id !== id))
    if (selectedConversation === id) {
      setSelectedConversation(null)
    }
  }

  return (
    <div className="w-80 bg-[#232326] border-r border-gray-700 flex flex-col h-screen">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-white">Chat with PDF</h1>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="p-1">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/placeholder.svg?height=32&width=32" />
                  <AvatarFallback className="bg-[#FFB020] text-black">JD</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-[#2C2C2E] border-gray-600">
              <DropdownMenuItem className="text-white hover:bg-gray-700">
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="text-white hover:bg-gray-700" onClick={onLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <Button
          className="w-full bg-[#FFB020] hover:bg-[#FFD700] text-black font-medium rounded-xl"
          onClick={() => {
            const fileInput = document.getElementById("pdf-upload") as HTMLInputElement
            fileInput?.click()
          }}
        >
          <Upload className="mr-2 h-4 w-4" />
          Upload PDF
        </Button>
        <input
          id="pdf-upload"
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) {
              // Handle file upload
              console.log("File uploaded:", file)

              // Add the new PDF to the list (simulate upload)
              const newPDF = {
                id: Date.now().toString(),
                name: file.name,
                size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
                uploadDate: new Date().toISOString().split("T")[0],
              }
              setPdfs((prev) => [newPDF, ...prev])

              // Switch to chat interface and select the new PDF
              setActiveView("chat")
              setSelectedPDF(newPDF.id)

              // Reset the input
              e.target.value = ""

              // Call the onPDFUpload prop if it exists
              onPDFUpload?.(file)
            }
          }}
        />
      </div>

      {/* Navigation */}
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

      {/* Scrollable Content - Takes remaining space above settings */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {activeView === "documents" ? (
          <div className="space-y-2">
            {pdfs.map((pdf) => (
              <div
                key={pdf.id}
                className={`p-3 rounded-xl border cursor-pointer transition-colors ${
                  selectedPDF === pdf.id
                    ? "bg-[#FFB020]/10 border-[#FFB020]"
                    : "bg-[#2C2C2E] border-gray-600 hover:border-gray-500"
                }`}
                onClick={() => setSelectedPDF(pdf.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-white truncate">{pdf.name}</h3>
                    <p className="text-sm text-gray-400">{pdf.size}</p>
                    <p className="text-xs text-gray-500">{pdf.uploadDate}</p>
                  </div>
                  <div className="flex space-x-1 ml-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-gray-400 hover:text-white"
                      onClick={(e) => {
                        e.stopPropagation()
                        console.log("View PDF:", pdf.id)
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-gray-400 hover:text-red-400"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeletePDF(pdf.id)
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {conversations.map((conv) => (
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
                    <h3 className="font-medium text-white truncate">{conv.title}</h3>
                    <p className="text-sm text-gray-400 truncate">{conv.lastMessage}</p>
                    <p className="text-xs text-gray-500">{conv.date}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-red-400 ml-2"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteConversation(conv.id)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Actions - Fixed at bottom of screen */}
      <div className="flex-shrink-0 p-4 border-t border-gray-700 bg-[#232326]">
        <div className="flex items-center justify-between">
          {/* Settings Button - Left side */}
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-xl p-2">
            <Settings className="h-5 w-5" />
          </Button>

          {/* Logout Button - Right side */}
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-xl p-2"
            onClick={onLogout}
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
