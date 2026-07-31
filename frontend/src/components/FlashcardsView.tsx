import React, { useState, useEffect } from "react";
import { Copy, Loader2, AlertTriangle, RefreshCw, Sparkles } from "lucide-react";

interface Flashcard {
  question: string;
  answer: string;
  difficulty: "Easy" | "Medium" | "Hard";
}

interface FlashcardsViewProps {
  paperId: string;
}

export const FlashcardsView: React.FC<FlashcardsViewProps> = ({ paperId }) => {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [flippedCards, setFlippedCards] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const fetchCards = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/paper/${paperId}/flashcards`);
        if (!response.ok) {
          throw new Error("Claims must be generated first. Please view the 'Verified Claims' tab first.");
        }
        const data = await response.json();
        setCards(Array.isArray(data) ? data : data.root || []);
      } catch (err: any) {
        setError(err.message || "Failed to retrieve flashcards.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCards();
  }, [paperId]);

  const toggleFlip = (index: number) => {
    setFlippedCards((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Generating active recall flashcards...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Flashcard Generation Locked</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn animate-duration-200">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Copy className="w-6 h-6 text-violet-400" />
            <span>Active Recall Flashcards</span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Derive conceptual study cards based on extracted facts. Click a card to flip it.
          </p>
        </div>
        <div className="px-3.5 py-1.5 bg-violet-600/10 border border-violet-500/20 rounded-full flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-violet-400" />
          <span className="text-xs text-violet-300 font-medium">Deck Size: {cards.length}</span>
        </div>
      </div>

      {/* Grid of Flashcards */}
      {cards.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/20 border border-slate-900 rounded-2xl max-w-xl mx-auto">
          <p className="text-slate-400 text-sm">No flashcards generated.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card, idx) => {
            const isFlipped = !!flippedCards[idx];
            const diffColor =
              card.difficulty === "Easy"
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : card.difficulty === "Medium"
                ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                : "bg-red-500/10 text-red-400 border-red-500/20";

            return (
              <div
                key={idx}
                onClick={() => toggleFlip(idx)}
                className="h-64 cursor-pointer relative group [perspective:1000px] select-none"
              >
                <div
                  className={`w-full h-full duration-500 [transform-style:preserve-3d] relative ${
                    isFlipped ? "[transform:rotateY(180deg)]" : ""
                  }`}
                >
                  {/* FRONT SIDE (Question) */}
                  <div className="absolute inset-0 w-full h-full bg-slate-900/50 border border-slate-900 rounded-2xl p-6 flex flex-col justify-between [backface-visibility:hidden]">
                    {/* Header */}
                    <div className="flex justify-between items-center">
                      <span className={`px-2.5 py-0.5 text-[10px] font-bold border rounded-full uppercase tracking-wider ${diffColor}`}>
                        {card.difficulty}
                      </span>
                      <RefreshCw className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                    </div>

                    {/* Question text */}
                    <div className="my-auto">
                      <p className="text-sm font-semibold text-slate-100 text-center leading-relaxed">
                        {card.question}
                      </p>
                    </div>

                    {/* Hint */}
                    <div className="text-center text-[10px] text-slate-500 uppercase tracking-wider">
                      Click to reveal answer
                    </div>
                  </div>

                  {/* BACK SIDE (Answer) */}
                  <div className="absolute inset-0 w-full h-full bg-violet-950/15 border border-violet-900/30 rounded-2xl p-6 flex flex-col justify-between [backface-visibility:hidden] [transform:rotateY(180deg)]">
                    {/* Header */}
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-violet-400 uppercase tracking-wider">
                        Answer
                      </span>
                      <RefreshCw className="w-4 h-4 text-violet-500/50" />
                    </div>

                    {/* Answer text */}
                    <div className="my-auto overflow-y-auto max-h-36 pr-1">
                      <p className="text-xs text-slate-200 text-center leading-relaxed font-serif">
                        {card.answer}
                      </p>
                    </div>

                    {/* Hint */}
                    <div className="text-center text-[10px] text-violet-500/60 uppercase tracking-wider">
                      Click to flip back
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
