import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertOctagon, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught React rendering error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#060814] text-slate-100 flex flex-col items-center justify-center p-6 text-center font-sans">
          <div className="max-w-md p-8 bg-slate-950/80 border border-slate-800 rounded-3xl shadow-2xl space-y-6">
            <div className="w-16 h-16 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-center justify-center mx-auto text-red-400">
              <AlertOctagon className="w-8 h-8" />
            </div>
            
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white tracking-tight">Component Execution Error</h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                {this.state.error?.message || "An unexpected error occurred while rendering the view."}
              </p>
            </div>

            <button
              onClick={this.handleReset}
              className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm rounded-xl transition-all cursor-pointer inline-flex items-center gap-2 shadow-lg"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reload Application</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
