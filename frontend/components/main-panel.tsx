"use client"

import { DocumentManager } from "@/components/document-manager"
import { ChatInterface } from "@/components/chat-interface"

interface MainPanelProps {
  activeView: "documents" | "chat"
  selectedPDF: string | null
  selectedConversation: string | null
}

export function MainPanel({ activeView, selectedPDF, selectedConversation }: MainPanelProps) {
  return (
    <div className="h-full bg-[#1C1C1E]">
      {activeView === "documents" ? (
        <DocumentManager selectedPDF={selectedPDF} />
      ) : (
        <ChatInterface selectedConversation={selectedConversation} />
      )}
    </div>
  )
}
