"use client"

import { FileText, Download, Eye, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface DocumentManagerProps {
  selectedPDF: string | null
}

const mockPDFs = [
  {
    id: "1",
    name: "Research Paper.pdf",
    size: "2.4 MB",
    uploadDate: "2024-01-15",
    pages: 24,
    description: "A comprehensive research paper on machine learning applications in healthcare.",
  },
  {
    id: "2",
    name: "Technical Manual.pdf",
    size: "5.1 MB",
    uploadDate: "2024-01-14",
    pages: 156,
    description: "Complete technical documentation for the new software platform.",
  },
  {
    id: "3",
    name: "Financial Report.pdf",
    size: "1.8 MB",
    uploadDate: "2024-01-13",
    pages: 45,
    description: "Q4 2023 financial report with detailed analysis and projections.",
  },
  {
    id: "4",
    name: "User Guide.pdf",
    size: "3.2 MB",
    uploadDate: "2024-01-12",
    pages: 67,
    description: "Complete user guide for the new application features.",
  },
  {
    id: "5",
    name: "API Documentation.pdf",
    size: "4.7 MB",
    uploadDate: "2024-01-11",
    pages: 89,
    description: "Comprehensive API documentation with examples and best practices.",
  },
]

export function DocumentManager({ selectedPDF }: DocumentManagerProps) {
  const selectedDoc = mockPDFs.find((pdf) => pdf.id === selectedPDF)

  return (
    <div className="h-screen flex flex-col">
      {/* Header - Fixed */}
      <div className="flex-shrink-0 p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white mb-2">Document Manager</h1>
        <p className="text-gray-400">Manage your uploaded PDFs and start conversations</p>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          {selectedDoc ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Document Details */}
              <div className="lg:col-span-2">
                <Card className="bg-[#232326] border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center">
                      <FileText className="mr-2 h-5 w-5 text-[#FFB020]" />
                      {selectedDoc.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">File Size:</span>
                        <span className="text-white ml-2">{selectedDoc.size}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Pages:</span>
                        <span className="text-white ml-2">{selectedDoc.pages}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Uploaded:</span>
                        <span className="text-white ml-2">{selectedDoc.uploadDate}</span>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-white font-medium mb-2">Description</h3>
                      <p className="text-gray-400">{selectedDoc.description}</p>
                    </div>

                    <div className="flex flex-wrap gap-3 pt-4">
                      <Button className="bg-[#FFB020] hover:bg-[#FFD700] text-black">
                        <Eye className="mr-2 h-4 w-4" />
                        Preview
                      </Button>
                      <Button variant="outline" className="border-gray-600 text-white hover:bg-gray-700 bg-transparent">
                        <Download className="mr-2 h-4 w-4" />
                        Download
                      </Button>
                      <Button
                        variant="outline"
                        className="border-red-600 text-red-400 hover:bg-red-600/10 bg-transparent"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <div>
                <Card className="bg-[#232326] border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button className="w-full bg-[#FFB020] hover:bg-[#FFD700] text-black">Start New Chat</Button>
                    <Button
                      variant="outline"
                      className="w-full border-gray-600 text-white hover:bg-gray-700 bg-transparent"
                    >
                      Generate Summary
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full border-gray-600 text-white hover:bg-gray-700 bg-transparent"
                    >
                      Extract Key Points
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockPDFs.map((pdf) => (
                <Card
                  key={pdf.id}
                  className="bg-[#232326] border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
                >
                  <CardHeader>
                    <CardTitle className="text-white flex items-center text-lg">
                      <FileText className="mr-2 h-5 w-5 text-[#FFB020]" />
                      <span className="truncate">{pdf.name}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Size:</span>
                        <span className="text-white">{pdf.size}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Pages:</span>
                        <span className="text-white">{pdf.pages}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Uploaded:</span>
                        <span className="text-white">{pdf.uploadDate}</span>
                      </div>
                    </div>
                    <p className="text-gray-400 text-sm mt-3 line-clamp-2">{pdf.description}</p>

                    <div className="flex space-x-2 mt-4">
                      <Button size="sm" className="flex-1 bg-[#FFB020] hover:bg-[#FFD700] text-black">
                        Chat
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-gray-600 text-white hover:bg-gray-700 bg-transparent"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
