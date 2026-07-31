import React, { useState, useEffect } from "react";
import { BrainCircuit, Loader2, AlertTriangle, Network, ArrowRight } from "lucide-react";

interface Node {
  id: string;
  label: string;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

interface ConceptMapResponse {
  nodes: Node[];
  edges: Edge[];
}

interface ConceptMapViewProps {
  paperId: string;
}

export const ConceptMapView: React.FC<ConceptMapViewProps> = ({ paperId }) => {
  const [mapData, setMapData] = useState<ConceptMapResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  useEffect(() => {
    const fetchMap = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/paper/${paperId}/conceptmap`);
        if (!response.ok) {
          throw new Error("Claims must be generated first. Please view the 'Verified Claims' tab first.");
        }
        const data = await response.json();
        setMapData(data);
        if (data.nodes && data.nodes.length > 0) {
          setSelectedNodeId(data.nodes[0].id);
        }
      } catch (err: any) {
        setError(err.message || "Failed to retrieve concept map.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMap();
  }, [paperId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Mapping conceptual topology...</p>
      </div>
    );
  }

  if (error || !mapData) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Concept Map Locked</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{error}</p>
      </div>
    );
  }

  // Get active relationships for the selected node
  const activeIncoming = mapData.edges.filter((e) => e.target === selectedNodeId);
  const activeOutgoing = mapData.edges.filter((e) => e.source === selectedNodeId);
  const selectedNodeLabel = mapData.nodes.find((n) => n.id === selectedNodeId)?.label || "";

  return (
    <div className="space-y-6 animate-fadeIn animate-duration-200">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <BrainCircuit className="w-6 h-6 text-violet-400" />
          <span>Knowledge & Concept Map</span>
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Topological network mapping key entities and their semantic linkages.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Entity Registry (Nodes) */}
        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs text-violet-400 font-bold uppercase tracking-wider">
            <Network className="w-4 h-4" />
            <span>Entities Catalog</span>
          </div>
          <div className="space-y-2 max-h-[450px] overflow-y-auto pr-1">
            {mapData.nodes.map((node) => {
              const isSelected = selectedNodeId === node.id;
              const relationCount = mapData.edges.filter(
                (e) => e.source === node.id || e.target === node.id
              ).length;

              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNodeId(node.id)}
                  className={`w-full text-left px-4 py-3.5 rounded-xl border transition-all duration-150 cursor-pointer flex justify-between items-center ${
                    isSelected
                      ? "bg-violet-600/10 border-violet-500/30 text-white font-semibold"
                      : "bg-slate-900/30 border-slate-900 hover:border-slate-800 text-slate-300 hover:text-slate-100"
                  }`}
                >
                  <span className="text-sm truncate pr-2">{node.label}</span>
                  <span className="text-[10px] bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-md text-slate-500 font-bold shrink-0">
                    {relationCount} rel
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Columns: Focus Node Connection Viewer */}
        <div className="lg:col-span-2 bg-slate-950/40 border border-slate-900 rounded-2xl p-6 flex flex-col justify-between min-h-[400px]">
          <div>
            {/* Header Focus */}
            <div className="border-b border-slate-900 pb-4 mb-6">
              <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider">
                Focused Node
              </span>
              <h3 className="text-xl font-bold text-white mt-1">{selectedNodeLabel}</h3>
            </div>

            {/* Relations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Incoming Connections */}
              <div className="space-y-3">
                <h4 className="text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  Incoming Influences
                </h4>
                {activeIncoming.length === 0 ? (
                  <p className="text-xs text-slate-600 italic">No incoming links found.</p>
                ) : (
                  <div className="space-y-2">
                    {activeIncoming.map((edge, idx) => {
                      const sourceLabel =
                        mapData.nodes.find((n) => n.id === edge.source)?.label || edge.source;
                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedNodeId(edge.source)}
                          className="p-3 bg-slate-900/40 border border-slate-900 hover:border-slate-800/80 rounded-xl transition-all duration-150 cursor-pointer flex flex-col gap-1 hover:bg-slate-900/60"
                        >
                          <span className="text-xs font-semibold text-slate-200 truncate">
                            {sourceLabel}
                          </span>
                          <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider flex items-center gap-1.5 mt-1">
                            <ArrowRight className="w-3 h-3 text-slate-500" />
                            {edge.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Outgoing Connections */}
              <div className="space-y-3">
                <h4 className="text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  Outgoing Relations
                </h4>
                {activeOutgoing.length === 0 ? (
                  <p className="text-xs text-slate-600 italic">No outgoing links found.</p>
                ) : (
                  <div className="space-y-2">
                    {activeOutgoing.map((edge, idx) => {
                      const targetLabel =
                        mapData.nodes.find((n) => n.id === edge.target)?.label || edge.target;
                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedNodeId(edge.target)}
                          className="p-3 bg-slate-900/40 border border-slate-900 hover:border-slate-800/80 rounded-xl transition-all duration-150 cursor-pointer flex flex-col gap-1 hover:bg-slate-900/60"
                        >
                          <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider flex items-center gap-1.5 mb-1">
                            {edge.label}
                            <ArrowRight className="w-3 h-3 text-slate-500" />
                          </span>
                          <span className="text-xs font-semibold text-slate-200 truncate">
                            {targetLabel}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="text-center text-[10px] text-slate-500 mt-6 pt-4 border-t border-slate-900/60">
            Select catalog concepts on the left sidebar to navigate the knowledge tree.
          </div>
        </div>
      </div>
    </div>
  );
};
