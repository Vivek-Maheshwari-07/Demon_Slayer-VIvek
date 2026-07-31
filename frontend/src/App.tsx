import { useState, useEffect } from "react";
import { Navigation } from "./components/Navigation";
import { PdfUpload } from "./components/PdfUpload";
import { ChatPanel } from "./components/ChatPanel";
import { ClaimsView } from "./components/ClaimsView";
import { SummaryView } from "./components/SummaryView";
import { BriefView } from "./components/BriefView";
import { LimitationsView } from "./components/LimitationsView";
import { Flashcards } from "./components/Flashcards";
import { ConceptMap } from "./components/ConceptMap";
import { apiClient } from "./api/client";
import { Loader2, AlertCircle, AlertTriangle, X, CheckCircle } from "lucide-react";

function App() {
  const [paperId, setPaperId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("chat");
  const [isDemoFallback, setIsDemoFallback] = useState<boolean>(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [processingState, setProcessingState] = useState<{ isProcessing: boolean; message: string }>({
    isProcessing: false,
    message: "",
  });

  useEffect(() => {
    const handleFallbackDetected = () => {
      setIsDemoFallback(true);
    };

    window.addEventListener("episteme-fallback-detected", handleFallbackDetected);
    return () => {
      window.removeEventListener("episteme-fallback-detected", handleFallbackDetected);
    };
  }, []);

  const showToast = (message: string, type: "success" | "error" = "error") => {
    setToast({ message, type });
    // Auto-dismiss toast in 5 seconds
    setTimeout(() => {
      setToast(null);
    }, 5000);
  };

  /**
   * Triggers immediately after PdfUpload successfully uploads the PDF.
   * Runs claims extraction and backend caching while displaying the overlay.
   */
  const handlePaperIngested = async (newPaperId: string) => {
    setProcessingState({
      isProcessing: true,
      message: "Running Chain-of-Verification (CoVe) engine. Extracting factually-grounded claims...",
    });

    try {
      // Pre-fetch claims (which triggers verification and local caching on backend)
      await apiClient.getClaims(newPaperId);
      
      setPaperId(newPaperId);
      setActiveTab("chat");
      showToast("Paper ingested & verified successfully! 🚀", "success");
    } catch (err: any) {
      showToast(err.message || "Failed to extract verified claims.");
    } finally {
      setProcessingState({ isProcessing: false, message: "" });
    }
  };

  const resetPaper = () => {
    setPaperId(null);
    setActiveTab("chat");
    setToast(null);
  };

  const renderActiveView = () => {
    if (!paperId) return null;

    switch (activeTab) {
      case "chat":
        return <ChatPanel paperId={paperId} />;
      case "claims":
        return <ClaimsView paperId={paperId} />;
      case "summary":
        return <SummaryView paperId={paperId} />;
      case "brief":
        return <BriefView paperId={paperId} />;
      case "limitations":
        return <LimitationsView paperId={paperId} />;
      case "flashcards":
        return <Flashcards paperId={paperId} />;
      case "graph":
        return <ConceptMap paperId={paperId} />;
      default:
        return <ChatPanel paperId={paperId} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#060814] text-slate-100 flex flex-col relative font-sans">
      {/* Sticky Demo Fallback Warning Banner */}
      {isDemoFallback && (
        <div className="bg-amber-500/20 border-b border-amber-500/40 text-amber-200 px-4 py-2.5 flex items-center justify-center gap-2 text-xs md:text-sm font-semibold sticky top-0 z-50 backdrop-blur-md shadow-lg">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>⚠️ API Connection Failed or Rate Limited: Displaying offline cached demo data.</span>
        </div>
      )}

      {/* Toast Notification Banner */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 animate-fadeIn duration-200">
          <div
            className={`flex items-center gap-3 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-md max-w-md ${
              toast.type === "success"
                ? "bg-emerald-950/80 border-emerald-500/30 text-emerald-200"
                : "bg-red-950/80 border-red-500/30 text-red-200"
            }`}
          >
            {toast.type === "success" ? (
              <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            )}
            <p className="text-sm font-medium pr-4">{toast.message}</p>
            <button
              onClick={() => setToast(null)}
              className="text-slate-400 hover:text-slate-200 transition-colors ml-auto cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Processing Loader Overlay */}
      {processingState.isProcessing && (
        <div className="fixed inset-0 bg-[#060814]/90 z-40 flex flex-col items-center justify-center p-6 backdrop-blur-sm">
          <div className="flex flex-col items-center max-w-md text-center space-y-6">
            <Loader2 className="w-16 h-16 text-violet-500 animate-spin" />
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-white tracking-tight">EPISTEME Ingestion Pipeline</h3>
              <p className="text-sm text-slate-400 font-medium leading-relaxed animate-pulse">
                {processingState.message}
              </p>
            </div>
            <div className="text-[10px] text-slate-600 uppercase tracking-widest border-t border-slate-900/60 pt-4 w-full">
              Parallel Thread Execution Active
            </div>
          </div>
        </div>
      )}

      {!paperId ? (
        // Document Upload Interface (Center layout)
        <div className="flex-1 flex items-center justify-center p-4">
          <PdfUpload setPaperId={handlePaperIngested} />
        </div>
      ) : (
        // Main Application Shell
        <div className="flex-1 flex overflow-hidden">
          {/* Left Navigation Sidebar */}
          <Navigation
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            resetPaper={resetPaper}
          />

          {/* Main Content Workspace */}
          <main className="flex-1 overflow-y-auto p-8 bg-gradient-to-br from-[#060814] via-[#090e1f] to-[#0c142c]">
            <div className="max-w-5xl mx-auto">
              {renderActiveView()}
            </div>
          </main>
        </div>
      )}
    </div>
  );
}

export default App;
