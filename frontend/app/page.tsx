"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { MainPanel } from "@/components/main-panel"
import { LoginPage } from "@/components/auth/login-page"
import { RegisterPage } from "@/components/auth/register-page"
import { SidebarProvider } from "@/components/ui/sidebar"
import { FadeMessage } from "@/components/ui/fade-message"

type AuthView = "login" | "register"

export default function ChatPDFApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authView, setAuthView] = useState<AuthView>("login")
  const [activeView, setActiveView] = useState<"documents" | "chat">("documents")
  const [selectedPDF, setSelectedPDF] = useState<string | null>(null)
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const [refreshDocs, setRefreshDocs] = useState(0)
  const [documents, setDocuments] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      setIsAuthenticated(true)
    }
  }, [])

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("token")
      const res = await fetch("/api/documents", {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      })
      if (!res.ok) {
        return
      }
      const data = await res.json()
      setDocuments(data.documents)
    } catch (e: any) {
      //pass
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [refreshDocs])

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        setUploadError(errorData.detail || "Login failed");
        return;
      }
      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      setIsAuthenticated(true);
      setUploadError(null);
    } catch (error) {
      setUploadError("An error occurred. Please try again.");
    }
  };

  const handleRegister = async (name: string, email: string, password: string) => {
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: name, email, password }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        setUploadError(errorData.detail || "Registration failed");
        return;
      }
      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      setIsAuthenticated(true);
      setUploadError(null);
    } catch (error) {
      setUploadError("An error occurred. Please try again.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setActiveView("documents");
    setSelectedPDF(null);
    setSelectedConversation(null);
    setUploadError(null);
    setUploadSuccess(null);
  }

  const handlePDFUpload = async (file: File) => {
    setUploadError(null);
    setUploadSuccess(null);
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("token");
    try {
      const response = await fetch("/api/documents/upload", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        setUploadError(errorData.detail || "PDF upload failed");
        setUploading(false);
        return;
      }
      const data = await response.json();
      setSelectedPDF(data.document_id);
      setSelectedConversation(data.conversation_id);
      setActiveView("chat");
      setUploadSuccess(data.message || "PDF uploaded and processed.");
      setRefreshDocs((prev) => prev + 1);
      await fetchDocuments();
    } catch (error) {
      setUploadError("An error occurred during PDF upload.");
    }
    setUploading(false);
  }

  const handleSelectPDF = (id: string) => {
    setSelectedPDF(id)
  }
  const handleDeletePDF = (id: string) => {
    if (selectedPDF === id) setSelectedPDF("")
  }

  const handleChat = async (documentId: string) => {
    setSelectedPDF(documentId);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`/api/conversations/by-document/${documentId}`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedConversation(data.conversation_id);
      } else {
        setSelectedConversation("");
      }
    } catch {
      setSelectedConversation("");
    }
    setActiveView("chat");
  }

  if (!isAuthenticated) {
    if (authView === "login") {
      return <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setAuthView("register")} />
    } else {
      return <RegisterPage onRegister={handleRegister} onSwitchToLogin={() => setAuthView("login")} />
    }
  }

  return (
    <div className="h-screen bg-[#1C1C1E] text-white">
      <SidebarProvider>
        <div className="flex h-full w-full">
          <Sidebar
            activeView={activeView}
            setActiveView={setActiveView}
            selectedPDF={selectedPDF}
            setSelectedPDF={setSelectedPDF}
            selectedConversation={selectedConversation}
            setSelectedConversation={setSelectedConversation}
            onLogout={handleLogout}
            onPDFUpload={handlePDFUpload}
            refreshDocs={refreshDocs}
            documents={documents}
            uploading={uploading}
            fetchDocuments={fetchDocuments}
          />
          <div className="flex-1 h-full">
            {uploadError && (
              <FadeMessage message={uploadError} className="fixed top-4 right-4 z-50 shadow-lg" onFadeComplete={() => setUploadError(null)} />
            )}
            {uploadSuccess && (
              <FadeMessage message={uploadSuccess} className="fixed top-4 right-4 z-50 shadow-lg" onFadeComplete={() => setUploadSuccess(null)} />
            )}
            <MainPanel
              activeView={activeView}
              selectedPDF={selectedPDF}
              selectedConversation={selectedConversation}
              refreshDocs={refreshDocs}
              onSelectPDF={handleSelectPDF}
              onDeletePDF={handleDeletePDF}
              documents={documents}
              fetchDocuments={fetchDocuments}
              onChat={handleChat}
            />
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
}
