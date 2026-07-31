import React, { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { BrainCircuit, Loader2, AlertTriangle } from "lucide-react";
import { apiClient } from "../api/client";

interface Node {
  id: string;
  label: string;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

interface ConceptMapProps {
  paperId: string;
}

export const ConceptMap: React.FC<ConceptMapProps> = ({ paperId }) => {
  const [graphData, setGraphData] = useState<{ nodes: Node[]; links: Edge[] } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });

  // Handle container resizing dynamically for the HTML5 Canvas
  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width || 800,
          height: Math.max(entry.contentRect.height, 450) || 500,
        });
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const fetchConceptMap = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getConceptMap(paperId);
        
        // Map edges to 'links' as expected by react-force-graph-2d
        const links = (data.edges || []).map((edge: any) => ({
          source: edge.source,
          target: edge.target,
          label: edge.label,
        }));
        
        setGraphData({
          nodes: data.nodes || [],
          links: links,
        });
      } catch (err: any) {
        setError(err.message || "Failed to load concept map.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchConceptMap();
  }, [paperId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Initializing 2D Canvas force graph...</p>
      </div>
    );
  }

  if (error || !graphData) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Concept Map Locked</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn animate-duration-200">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-violet-400" />
            <span>Interactive Knowledge Graph</span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            2D force-directed canvas. Left-click drag to pan; scroll to zoom. Click nodes to focus.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Graph Canvas Container */}
        <div 
          ref={containerRef} 
          className="lg:col-span-3 h-[500px] bg-slate-950/60 border border-slate-900 rounded-2xl overflow-hidden relative"
        >
          <ForceGraph2D
            graphData={graphData}
            width={dimensions.width}
            height={dimensions.height}
            nodeId="id"
            nodeLabel="label"
            nodeAutoColorBy="id"
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={0.95}
            linkLabel="label"
            onNodeClick={(node: any) => {
              setSelectedNode(node);
            }}
            cooldownTicks={100}
            // Enhance node drawing to display node labels directly on the canvas
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.label;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;
              const textWidth = ctx.measureText(label).width;
              const bWidth = textWidth + 8;
              const bHeight = fontSize + 4;
              
              // Draw background pill
              ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
              ctx.beginPath();
              ctx.roundRect(node.x - bWidth / 2, node.y - bHeight / 2, bWidth, bHeight, 4);
              ctx.fill();
              
              // Draw pill border
              ctx.strokeStyle = node.color || "#8b5cf6";
              ctx.lineWidth = 1 / globalScale;
              ctx.stroke();

              // Draw Label Text
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";
              ctx.fillStyle = "#f8fafc";
              ctx.fillText(label, node.x, node.y);
            }}
          />
        </div>

        {/* Selected Entity Inspector */}
        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="text-xs text-violet-400 font-bold uppercase tracking-wider">
              Entity Inspector
            </div>

            {selectedNode ? (
              <div className="space-y-3">
                <h3 className="text-lg font-bold text-white leading-tight">
                  {selectedNode.label}
                </h3>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                    Node ID
                  </span>
                  <p className="text-xs text-slate-300 font-mono select-all">
                    {selectedNode.id}
                  </p>
                </div>
                
                {/* Find related links */}
                <div className="space-y-2">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                    Connections
                  </span>
                  <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
                    {graphData.links
                      .filter((link: any) => link.source.id === selectedNode.id || link.target.id === selectedNode.id || link.source === selectedNode.id || link.target === selectedNode.id)
                      .map((link: any, idx) => {
                        const src = typeof link.source === 'object' ? link.source.label : link.source;
                        const tgt = typeof link.target === 'object' ? link.target.label : link.target;
                        const isOut = (typeof link.source === 'object' ? link.source.id : link.source) === selectedNode.id;
                        
                        return (
                          <div key={idx} className="text-xs p-2 bg-slate-900/40 border border-slate-900 rounded-lg">
                            <span className="font-semibold text-slate-300">
                              {isOut ? "To: " : "From: "}
                            </span>
                            <span className="text-slate-400">{isOut ? tgt : src}</span>
                            <p className="text-[10px] text-violet-400 font-bold mt-0.5 uppercase">
                              Relationship: {link.label}
                            </p>
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500 italic">
                Select a concept node in the network to inspect its relationships.
              </p>
            )}
          </div>

          <div className="text-[10px] text-slate-600 border-t border-slate-900/60 pt-4 mt-4">
            Canvas leverages HTML5 2D contexts for hardware accelerated physics.
          </div>
        </div>
      </div>
    </div>
  );
};
export default ConceptMap;
