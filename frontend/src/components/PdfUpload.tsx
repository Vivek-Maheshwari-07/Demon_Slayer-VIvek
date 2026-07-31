import React, { useState, useRef } from "react";
import { Upload, AlertCircle, Loader2 } from "lucide-react";

interface PdfUploadProps {
  setPaperId: (paperId: string) => void;
}

export const PdfUpload: React.FC<PdfUploadProps> = ({ setPaperId }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const uploadFile = async (file: File) => {
    if (!file.name.endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Upload failed. Please check backend status.");
      }

      const data = await response.json();
      if (data.paper_id) {
        setPaperId(data.paper_id);
      } else {
        throw new Error("Invalid response from server.");
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend server.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-xl p-8 bg-slate-900/60 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-md">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">EPISTEME</h1>
        <p className="text-slate-400 text-sm">
          AI-Powered Academic Research Companion
        </p>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-10 cursor-pointer transition-all duration-300 ${
          isDragActive
            ? "border-violet-500 bg-violet-950/20"
            : "border-slate-800 hover:border-slate-700 bg-slate-950/40 hover:bg-slate-950/60"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-violet-500 animate-spin mb-4" />
            <p className="text-slate-300 font-medium animate-pulse">
              Parsing & Chunking Document...
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Extracting spatial page layouts and building vector embeddings
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center text-center">
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-full mb-4">
              <Upload className="w-8 h-8 text-slate-400" />
            </div>
            <p className="text-slate-200 font-semibold mb-1">
              Drag & drop your research paper here
            </p>
            <p className="text-sm text-slate-400 mb-6">
              or click to browse from files (PDF only)
            </p>
            <span className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-medium rounded-lg text-sm transition-colors duration-200 shadow-lg shadow-violet-500/20">
              Select Document
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 mt-6 p-4 bg-red-950/40 border border-red-900/50 rounded-xl text-red-200 text-sm">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="mt-8 text-center text-xs text-slate-500 border-t border-slate-800/60 pt-4">
        Supports large academic PDFs. Documents are index-partitioned page-by-page.
      </div>
    </div>
  );
};
