import { Component, ErrorInfo, ReactNode } from "react";
import { RefreshCw, Sparkles } from "lucide-react";
import { Button } from "../ui/Button";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  fallbackMessage?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class AIErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("AI Feature Error Boundary caught an error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-center dark:border-amber-500/20">
          <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <Sparkles className="h-5 w-5 animate-pulse" />
          </div>
          <h4 className="text-sm font-semibold text-foreground">
            {this.props.fallbackTitle || "AI Service Momentarily Unavailable"}
          </h4>
          <p className="mt-1 text-xs text-muted-foreground">
            {this.props.fallbackMessage ||
              "The AI feature encountered a temporary issue. Standard store operations are unaffected."}
          </p>
          {this.state.error && (
            <p className="mt-2 text-[11px] font-mono text-destructive">
              {this.state.error.message}
            </p>
          )}
          <div className="mt-3 flex justify-center">
            <Button
              size="sm"
              variant="outline"
              onClick={this.handleReset}
              className="h-8 gap-1.5 text-xs border-amber-500/30 hover:bg-amber-500/10"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Try Again
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default AIErrorBoundary;
