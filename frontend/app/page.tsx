"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { MainPanel } from "@/components/main-panel"
import { LoginPage } from "@/components/auth/login-page"
import { RegisterPage } from "@/components/auth/register-page"
import { SidebarProvider } from "@/components/ui/sidebar"

type AuthView = "login" | "register"

export default function ChatPDFApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authView, setAuthView] = useState<AuthView>("login")
  const [activeView, setActiveView] = useState<"documents" | "chat">("documents")
  const [selectedPDF, setSelectedPDF] = useState<string | null>(null)
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.detail || "Login failed");
        return;
      }
      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      setIsAuthenticated(true);
    } catch (error) {
      alert("An error occurred. Please try again.");
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
        alert(errorData.detail || "Registration failed");
        return;
      }
      const data = await response.json();
      localStorage.setItem("token", data.access_token); // Store JWT after register
      setIsAuthenticated(true); // Auto-login
    } catch (error) {
      alert("An error occurred. Please try again.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token"); // Remove JWT token from storage
    setIsAuthenticated(false);
    setActiveView("documents");
    setSelectedPDF(null);
    setSelectedConversation(null);
  }

  const handlePDFUpload = (file: File) => {
    // Switch to chat view when PDF is uploaded
    setActiveView("chat")

    // You can also set a selected conversation or create a new one
    // setSelectedConversation(null) // Start fresh conversation
  }

  // Show auth pages if not authenticated
  if (!isAuthenticated) {
    if (authView === "login") {
      return <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setAuthView("register")} />
    } else {
      return <RegisterPage onRegister={handleRegister} onSwitchToLogin={() => setAuthView("login")} />
    }
  }

  // Show main app if authenticated
  return (
    <div className="h-screen bg-[#1C1C1E] text-white">
      <SidebarProvider>
        <div className="flex h-full">
          <Sidebar
            activeView={activeView}
            setActiveView={setActiveView}
            selectedPDF={selectedPDF}
            setSelectedPDF={setSelectedPDF}
            selectedConversation={selectedConversation}
            setSelectedConversation={setSelectedConversation}
            onLogout={handleLogout}
            onPDFUpload={handlePDFUpload}
          />
          <div className="flex-1 h-full">
            <MainPanel activeView={activeView} selectedPDF={selectedPDF} selectedConversation={selectedConversation} />
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
}
