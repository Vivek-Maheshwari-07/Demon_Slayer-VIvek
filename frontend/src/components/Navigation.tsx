import React from "react";
import {
  MessageSquare,
  FileText,
  CheckCircle,
  BrainCircuit,
  Copy,
  BookOpen,
  LogOut,
} from "lucide-react";

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  resetPaper: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  setActiveTab,
  resetPaper,
}) => {
  const navItems = [
    { id: "chat", label: "Grounding Chat", icon: MessageSquare },
    { id: "claims", label: "Verified Claims", icon: CheckCircle },
    { id: "summary", label: "Research Summary", icon: FileText },
    { id: "brief", label: "Technical Brief", icon: BookOpen },
    { id: "flashcards", label: "Active Recall", icon: Copy },
    { id: "graph", label: "Concept Graph", icon: BrainCircuit },
  ];

  return (
    <aside className="w-64 bg-slate-950/80 border-r border-slate-900 flex flex-col justify-between h-screen sticky top-0 backdrop-blur-md">
      <div className="flex flex-col">
        {/* Sidebar Header */}
        <div className="p-6 border-b border-slate-900/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center font-bold text-white tracking-wider">
            E
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight leading-none">EPISTEME</h2>
            <span className="text-[10px] text-violet-400 font-semibold tracking-wider uppercase">
              AI companion
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-violet-600/10 text-violet-400 border border-violet-500/20 shadow-md shadow-violet-500/5 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-violet-400" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-slate-900/60">
        <button
          onClick={resetPaper}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-500 hover:text-red-400 hover:bg-red-950/10 transition-all duration-200 cursor-pointer"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <span>Ingest New Paper</span>
        </button>
      </div>
    </aside>
  );
};
