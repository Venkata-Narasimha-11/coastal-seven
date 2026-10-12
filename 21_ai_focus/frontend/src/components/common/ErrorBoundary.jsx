import React from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an unhandled error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center p-4">
          <Card className="max-w-lg w-full border-destructive/30 shadow-lg">
            <CardHeader className="text-center space-y-2 pb-4">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <CardTitle className="text-lg font-bold text-foreground">
                Something went wrong
              </CardTitle>
              <CardDescription className="text-xs">
                An unexpected interface error occurred during render.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-md bg-muted/60 p-3 font-mono text-[11px] text-destructive break-all max-h-36 overflow-y-auto">
                {this.state.error?.message || "Unknown error"}
              </div>
              <div className="flex justify-center gap-3 pt-2">
                <Button variant="outline" size="sm" onClick={() => (window.location.href = "/")}>
                  <Home className="mr-1.5 h-3.5 w-3.5" /> Back to Store
                </Button>
                <Button size="sm" onClick={this.handleReset}>
                  <RefreshCw className="mr-1.5 h-3.5 w-3.5" /> Reload Page
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
