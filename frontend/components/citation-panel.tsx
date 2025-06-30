"use client"

import { FileText, ExternalLink, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface Citation {
  id: string
  page: number
  snippet: string
  relevance: number
}

interface CitationPanelProps {
  citations: Citation[]
  onCitationClick: (citation: Citation) => void
  onClose?: () => void
}

export function CitationPanel({ citations, onCitationClick, onClose }: CitationPanelProps) {
  const [expanded, setExpanded] = useState<{ [id: string]: boolean }>({});

  const handleToggle = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="h-screen bg-[#232326] flex flex-col">
      <div className="flex-shrink-0 p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="mr-2 h-5 w-5 text-[#FFB020]" />
            <h3 className="text-white font-semibold">Sources & Citations</h3>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-white" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-4">
          {citations.map((citation, index) => {
            const isExpanded = expanded[citation.id] || false;
            const snippet = isExpanded || citation.snippet.length <= 60
              ? citation.snippet
              : citation.snippet.slice(0, 60) + '…';
            return (
              <div
                key={citation.id ?? index}
                className="p-3 rounded-xl bg-[#2C2C2E] border border-gray-600 hover:border-[#FFB020]/50 cursor-pointer transition-colors"
                onClick={() => handleToggle(citation.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <Badge variant="secondary" className="bg-[#FFB020]/20 text-[#FFB020]">
                    Page {citation.page}
                  </Badge>
                </div>

                <p className="text-sm text-gray-300 leading-relaxed mb-3">{snippet}</p>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Citation #{index + 1}</span>
                </div>
              </div>
            );
          })}

          {citations.length === 0 && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">No citations available</p>
              <p className="text-sm text-gray-500">Citations will appear here when you chat with your PDFs</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
