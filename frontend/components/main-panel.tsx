"use client"

import { ChatInterface } from "@/components/chat-interface"

interface MainPanelProps {
  activeView: "documents" | "chat"
  selectedPDF: string | null
  selectedConversation: string | null
  refreshDocs?: number
  onSelectPDF: (id: string) => void
  onDeletePDF: (id: string) => void
  documents: any[]
  fetchDocuments: () => void
  onChat?: (documentId: string) => void
}

export function MainPanel({ activeView, selectedPDF, selectedConversation }: MainPanelProps) {
  return (
    <div className="h-full bg-[#1C1C1E]">
      <ChatInterface selectedConversation={selectedConversation} />
    </div>
  )
}
