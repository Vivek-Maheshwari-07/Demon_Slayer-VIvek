import React, { useState, useEffect } from "react";
import { BookOpen, Loader2, AlertTriangle, Shield, Check, Cpu, Award } from "lucide-react";
import { apiClient } from "../api/client";

interface BriefResponse {
  problem: string;
  method: string;
  dataset: string;
  results: string;
  limitations: string;
  future_work: string;
  contribution: string;
}

interface BriefViewProps {
  paperId: string;
}

export const BriefView: React.FC<BriefViewProps> = ({ paperId }) => {
  const [brief, setBrief] = useState<BriefResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBrief = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getBrief(paperId);
        setBrief(data);
      } catch (err: any) {
        setError(err.message || "Failed to retrieve brief.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchBrief();
  }, [paperId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Generating technical brief...</p>
      </div>
    );
  }

  if (error || !brief) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Brief Generation Failed</h3>
        <p className="text-sm text-slate-400">{error || "No brief available."}</p>
      </div>
    );
  }

  const sections = [
    { title: "Core Research Problem", content: brief.problem, icon: Shield, color: "text-red-400 bg-red-500/10" },
    { title: "Proposed Methodology", content: brief.method, icon: Cpu, color: "text-violet-400 bg-violet-500/10" },
    { title: "Experimental Dataset", content: brief.dataset, icon: BookOpen, color: "text-blue-400 bg-blue-500/10" },
    { title: "Key Empirical Results", content: brief.results, icon: Check, color: "text-emerald-400 bg-emerald-500/10" },
    { title: "Identified Limitations", content: brief.limitations, icon: AlertTriangle, color: "text-amber-400 bg-amber-500/10" },
    { title: "Future Work Directions", content: brief.future_work, icon: BookOpen, color: "text-indigo-400 bg-indigo-500/10" },
  ];

  return (
    <div className="space-y-8 animate-fadeIn animate-duration-200">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-violet-400" />
          <span>Technical Brief</span>
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Structured decomposition of the paper's core scientific contributions.
        </p>
      </div>

      {/* Contribution Highlight */}
      <div className="p-6 bg-violet-600/10 border border-violet-500/20 rounded-2xl flex items-start gap-4">
        <div className="p-3 bg-violet-600/20 border border-violet-500/30 rounded-xl text-violet-400 shrink-0">
          <Award className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-violet-300 uppercase tracking-wider">Primary Contribution</h3>
          <p className="text-slate-200 text-sm leading-relaxed">{brief.contribution}</p>
        </div>
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((sec, idx) => {
          const Icon = sec.icon;
          return (
            <div key={idx} className="p-6 bg-slate-900/30 border border-slate-900 rounded-2xl space-y-3">
              <div className="flex items-center gap-2.5">
                <div className={`p-1.5 rounded-lg ${sec.color}`}>
                  <Icon className="w-4 h-4 shrink-0" />
                </div>
                <h4 className="text-sm font-bold text-slate-100">{sec.title}</h4>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed pl-8">
                {sec.content}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
