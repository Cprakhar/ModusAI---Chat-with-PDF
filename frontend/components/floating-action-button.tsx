"use client"

import { useState } from "react"
import { Plus, Upload, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"

// Add props to the component:
interface FloatingActionButtonProps {
  onUploadPDF?: () => void
  onNewChat?: () => void
}

export function FloatingActionButton({ onUploadPDF, onNewChat }: FloatingActionButtonProps = {}) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="fixed bottom-6 right-6 z-[9999]">
      {/* Expanded Actions */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 space-y-3 animate-in slide-in-from-bottom-2">
          <Button
            size="sm"
            className="bg-[#232326] hover:bg-[#2C2C2E] text-white border border-gray-600 shadow-lg"
            onClick={() => {
              const fileInput = document.getElementById("pdf-upload") as HTMLInputElement
              fileInput?.click()
              setIsExpanded(false)
            }}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload PDF
          </Button>
          <Button
            size="sm"
            className="bg-[#232326] hover:bg-[#2C2C2E] text-white border border-gray-600 shadow-lg"
            onClick={() => {
              onNewChat?.()
              setIsExpanded(false)
            }}
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            New Chat
          </Button>
        </div>
      )}

      {/* Main FAB */}
      <Button
        size="lg"
        className={`h-14 w-14 rounded-full shadow-lg transition-all duration-200 ${
          isExpanded ? "bg-gray-600 hover:bg-gray-700 rotate-45" : "bg-[#FFB020] hover:bg-[#FFD700]"
        }`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Plus className={`h-6 w-6 ${isExpanded ? "text-white" : "text-black"}`} />
      </Button>
    </div>
  )
}
