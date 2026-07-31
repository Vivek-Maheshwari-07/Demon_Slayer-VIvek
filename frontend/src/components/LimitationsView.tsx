import React, { useState, useEffect } from "react";
import { AlertTriangle, ShieldAlert, Sparkles } from "lucide-react";
import { CitationCard } from "./CitationCard";
import { apiClient } from "../api/client";
import type { Limitation } from "../api/types";

interface LimitationsViewProps {
  paperId: string;
}

export const LimitationsView: React.FC<LimitationsViewProps> = ({ paperId }) => {
  const [limitations, setLimitations] = useState<Limitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLimitations = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getLimitations(paperId);
        setLimitations(data?.limitations || []);
      } catch (err: any) {
        setError(err.message || "Failed to retrieve paper limitations.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLimitations();
  }, [paperId]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-2">
          <div className="h-8 w-64 bg-slate-900 animate-pulse rounded-lg" />
          <div className="h-4 w-96 bg-slate-900 animate-pulse rounded-lg" />
        </div>

        <div className="grid grid-cols-1 gap-6">
          {[1, 2].map((idx) => (
            <div key={idx} className="p-6 bg-slate-900/40 border border-slate-900 rounded-2xl space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full bg-slate-800 animate-pulse shrink-0" />
                <div className="h-5 w-3/4 bg-slate-800 animate-pulse rounded-lg" />
              </div>
              <div className="h-4 w-full bg-slate-800 animate-pulse rounded-lg" />
              <div className="flex justify-end pt-2">
                <div className="h-6 w-36 bg-slate-800 animate-pulse rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Limitations Extraction Failed</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-red-900/60 hover:bg-red-800 border border-red-800 text-white rounded-lg text-sm transition-colors cursor-pointer"
        >
          Retry Pipeline
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn animate-duration-200">
      {/* Title Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            <span>Identified Paper Limitations</span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Core constraints, hardware boundaries, and assumptions explicitly cited in the research paper.
          </p>
        </div>
        <div className="px-3.5 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded-full flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span className="text-xs text-amber-300 font-medium">
            Limitations Identified: {limitations.length}
          </span>
        </div>
      </div>

      {/* Limitations List */}
      {limitations.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/20 border border-slate-900 rounded-2xl max-w-xl mx-auto">
          <p className="text-slate-400 text-sm">
            No explicit technical limitations were extracted for this document.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {limitations.map((item, idx) => (
            <div
              key={idx}
              className="p-6 bg-slate-900/30 border border-slate-900 hover:border-slate-800/80 rounded-2xl space-y-4 hover:bg-slate-900/50 transition-all duration-200 shadow-md group"
            >
              {/* Limitation Statement */}
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <h3 className="text-base font-bold text-slate-100 leading-snug group-hover:text-white transition-colors">
                  {item.limitation}
                </h3>
              </div>

              {/* Supporting Citation Badge */}
              <div className="pl-8 pt-2 flex items-center justify-between gap-4 border-t border-slate-900/40">
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
                  Verbatim Source Citation
                </span>
                <CitationCard
                  text={item.citation.text}
                  page={item.citation.page}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LimitationsView;
