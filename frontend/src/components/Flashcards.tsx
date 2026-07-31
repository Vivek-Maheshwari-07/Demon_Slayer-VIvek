import React, { useState, useEffect } from "react";
import { Copy, Loader2, AlertTriangle, ArrowLeft, ArrowRight, RefreshCw, Sparkles } from "lucide-react";
import { apiClient } from "../api/client";

interface Flashcard {
  question: string;
  answer: string;
  difficulty: "Easy" | "Medium" | "Hard";
}

interface FlashcardsProps {
  paperId: string;
}

export const Flashcards: React.FC<FlashcardsProps> = ({ paperId }) => {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  useEffect(() => {
    const fetchCards = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getFlashcards(paperId);
        setCards(data || []);
      } catch (err: any) {
        setError(err.message || "Failed to load flashcards.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCards();
  }, [paperId]);

  const handleNext = () => {
    if (currentIndex < cards.length - 1) {
      setIsFlipped(false);
      // Wait for flip back transition before changing card content
      setTimeout(() => {
        setCurrentIndex((prev) => prev + 1);
      }, 150);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setIsFlipped(false);
      setTimeout(() => {
        setCurrentIndex((prev) => prev - 1);
      }, 150);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <Loader2 className="w-10 h-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm">Generating active recall flashcards...</p>
      </div>
    );
  }

  if (error || cards.length === 0) {
    return (
      <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-red-200 text-center max-w-xl mx-auto mt-12 space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-white">Active Recall Locked</h3>
        <p className="text-sm text-slate-400 leading-relaxed">
          {error || "No study flashcards available for this paper."}
        </p>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const difficultyColors =
    currentCard.difficulty === "Easy"
      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      : currentCard.difficulty === "Medium"
      ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
      : "bg-red-500/10 text-red-400 border-red-500/20";

  return (
    <div className="space-y-6 max-w-2xl mx-auto animate-fadeIn animate-duration-200">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Copy className="w-6 h-6 text-violet-400" />
            <span>Active Recall Deck</span>
          </h2>
          <p className="text-slate-400 text-sm">
            Combat memory decay by testing yourself on core conceptual claims.
          </p>
        </div>
        <div className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 text-xs font-semibold">
          Card {currentIndex + 1} of {cards.length}
        </div>
      </div>

      {/* Main Flashcard View */}
      <div 
        onClick={() => setIsFlipped(!isFlipped)} 
        className="h-80 w-full cursor-pointer relative [perspective:1000px] select-none group"
      >
        <div 
          className={`w-full h-full duration-500 [transform-style:preserve-3d] relative ${
            isFlipped ? "[transform:rotateY(180deg)]" : ""
          }`}
        >
          {/* Question Front */}
          <div className="absolute inset-0 w-full h-full bg-slate-950/60 border border-slate-900 hover:border-slate-800/80 rounded-3xl p-8 flex flex-col justify-between [backface-visibility:hidden] shadow-2xl transition-colors duration-200">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                Question
              </span>
              <RefreshCw className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
            </div>

            <div className="text-center px-4">
              <p className="text-lg md:text-xl font-bold text-slate-100 leading-relaxed">
                {currentCard.question}
              </p>
            </div>

            <div className="text-center text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
              Click Card to Reveal Answer
            </div>
          </div>

          {/* Answer Back */}
          <div className="absolute inset-0 w-full h-full bg-violet-950/15 border border-violet-900/30 rounded-3xl p-8 flex flex-col justify-between [backface-visibility:hidden] [transform:rotateY(180deg)] shadow-2xl">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider">
                Answer Key
              </span>
              <span className={`px-2.5 py-0.5 text-[10px] font-bold border rounded-full uppercase tracking-wider ${difficultyColors}`}>
                {currentCard.difficulty}
              </span>
            </div>

            <div className="text-center px-4 overflow-y-auto max-h-48 scrollbar-thin">
              <p className="text-sm md:text-base text-slate-200 leading-relaxed font-serif">
                {currentCard.answer}
              </p>
            </div>

            <div className="text-center text-[10px] text-violet-500/60 font-semibold uppercase tracking-wider">
              Click Card to Flip Back
            </div>
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex items-center justify-between px-2 pt-2">
        <button
          onClick={handlePrev}
          disabled={currentIndex === 0}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-950/20 border border-slate-800 disabled:border-slate-900 text-slate-300 disabled:text-slate-600 rounded-xl text-sm font-semibold transition-all duration-150 cursor-pointer disabled:cursor-not-allowed"
        >
          <ArrowLeft className="w-4 h-4 shrink-0" />
          <span>Previous</span>
        </button>

        <button
          onClick={() => setIsFlipped(!isFlipped)}
          className="px-6 py-2.5 bg-violet-600/10 hover:bg-violet-600/20 border border-violet-500/30 text-violet-300 rounded-xl text-sm font-bold transition-all duration-150 cursor-pointer flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          <span>{isFlipped ? "Show Question" : "Show Answer"}</span>
        </button>

        <button
          onClick={handleNext}
          disabled={currentIndex === cards.length - 1}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-950/20 border border-slate-800 disabled:border-slate-900 text-slate-300 disabled:text-slate-600 rounded-xl text-sm font-semibold transition-all duration-150 cursor-pointer disabled:cursor-not-allowed"
        >
          <span>Next</span>
          <ArrowRight className="w-4 h-4 shrink-0" />
        </button>
      </div>
    </div>
  );
};
export default Flashcards;
