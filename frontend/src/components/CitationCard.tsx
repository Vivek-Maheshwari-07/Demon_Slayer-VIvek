import React, { useState } from "react";
import { Quote, ChevronDown, ChevronUp } from "lucide-react";

interface CitationCardProps {
  text: string;
  page: number;
  onClick?: () => void;
}

export const CitationCard: React.FC<CitationCardProps> = ({ text, page, onClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
    if (onClick) onClick();
  };

  return (
    <div 
      className={`inline-block text-left transition-all duration-200 mt-2 ${
        isExpanded ? "w-full block" : "w-auto"
      }`}
    >
      {/* Inline Badge */}
      <button
        onClick={handleToggle}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full border cursor-pointer transition-all duration-200 hover:shadow-[0_0_12px_rgba(139,92,246,0.6)] hover:border-violet-500/80 hover:text-white ${
          isExpanded
            ? "bg-violet-600/25 text-violet-300 border-violet-500/50 shadow-[0_0_10px_rgba(139,92,246,0.3)]"
            : "bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800"
        }`}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-pulse" />
        <span>Source: Page {page}</span>
        {isExpanded ? (
          <ChevronUp className="w-3.5 h-3.5 text-violet-400 shrink-0" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-slate-500 shrink-0" />
        )}
      </button>

      {/* Expanded Quote Box */}
      {isExpanded && (
        <div className="mt-2 p-3.5 bg-slate-950/80 border-y border-r border-slate-800/80 border-l-2 border-l-violet-500 rounded-r-xl rounded-l-md relative shadow-inner overflow-hidden animate-fadeIn animate-duration-200 shadow-[0_0_15px_rgba(139,92,246,0.1)]">
          <div className="absolute top-2 right-2 opacity-5 pointer-events-none">
            <Quote className="w-12 h-12 text-white" />
          </div>
          <p className="text-[12px] italic text-slate-300 font-serif leading-relaxed pr-6">
            "{text}"
          </p>
          <div className="mt-2 text-[10px] text-slate-500 font-medium uppercase tracking-wider flex justify-between items-center">
            <span>Verbatim quote verified</span>
            <span>Page {page}</span>
          </div>
        </div>
      )}
    </div>
  );
};
