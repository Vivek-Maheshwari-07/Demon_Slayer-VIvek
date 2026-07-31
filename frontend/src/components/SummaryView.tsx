import React, { useState, useEffect } from "react";
import { FileText, Loader2, AlertTriangle, Sparkles, BookOpen } from "lucide-react";
import { apiClient } from "../api/client";

interface SummaryResponse {
  executive: string;
  detailed: string;
}

interface SummaryViewProps {
  paperId: string;
}

export const SummaryView: React.FC<SummaryViewProps> = ({ paperId }) => {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getSummary(paperId);
        setSummary(data);
      } catch (err: any) {
        setError(err.message || "Failed to retrieve summary.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, [paperId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Synthesizing document summary...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Summary Failed</h3>
        <p className="text-sm text-slate-400">{error || "No summary available."}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn animate-duration-200">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <FileText className="w-6 h-6 text-violet-400" />
          <span>Research Summary</span>
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Synthesized overview of the paper's main objectives and details.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Executive Summary */}
        <div className="p-6 bg-slate-900/30 border border-slate-900 rounded-2xl space-y-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5">
            <Sparkles className="w-24 h-24 text-white" />
          </div>
          <div className="flex items-center gap-2 text-xs text-violet-400 font-bold uppercase tracking-wider">
            <Sparkles className="w-4.5 h-4.5" />
            <span>Executive Overview</span>
          </div>
          <p className="text-slate-200 text-base leading-relaxed font-serif pt-1">
            {summary.executive}
          </p>
        </div>

        {/* Detailed Breakdown */}
        <div className="p-6 bg-slate-900/30 border border-slate-900 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-xs text-violet-400 font-bold uppercase tracking-wider">
            <BookOpen className="w-4.5 h-4.5" />
            <span>Detailed Technical Breakdown</span>
          </div>
          <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap pt-1 pl-1">
            {summary.detailed}
          </div>
        </div>
      </div>
    </div>
  );
};
