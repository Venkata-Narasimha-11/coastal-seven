import React, { useState } from "react";
import { Sparkles, Loader2, Check, RefreshCw, X, Zap } from "lucide-react";
import { Button } from "../ui/Button";
import { aiService, GeneratedDescriptionResponse } from "../../services/aiService";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  productName: string;
  category?: string;
  price?: number;
  onApplyDescription: (description: string) => void;
}

export const AIDescriptionModal: React.FC<Props> = ({
  isOpen,
  onClose,
  productName,
  category = "General",
  price,
  onApplyDescription,
}) => {
  const [tone, setTone] = useState<"engaging" | "professional" | "technical" | "luxury" | "concise">("engaging");
  const [featuresInput, setFeaturesInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GeneratedDescriptionResponse | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!productName.trim()) {
      setError("Please provide a product name before generating a description.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const features = featuresInput
        .split("\n")
        .map((f) => f.trim())
        .filter((f) => f.length > 0);

      const data = await aiService.generateDescription({
        name: productName,
        category,
        features,
        price,
        tone,
      });
      setResult(data);
    } catch (err: any) {
      console.error("AI Description generation failed:", err);
      setError(err?.response?.data?.detail?.message || err?.message || "Failed to generate description");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (result?.description) {
      onApplyDescription(result.description);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-2xl rounded-2xl bg-card border border-border p-6 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">AI Description Generator</h3>
              <p className="text-xs text-muted-foreground">
                Generate high-converting e-commerce copy for <span className="font-semibold text-foreground">{productName || "Product"}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-foreground uppercase tracking-wider block mb-1.5">
                Tone & Voice
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value as any)}
                className="w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="engaging">✨ Engaging & Persuasive (Marketing)</option>
                <option value="professional">💼 Professional & Trustworthy</option>
                <option value="technical">⚙️ Technical & Specifications-focused</option>
                <option value="luxury">💎 Luxury & Sophisticated</option>
                <option value="concise">⚡ Concise & SEO-Optimized</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-foreground uppercase tracking-wider block mb-1.5">
                Category & Price Context
              </label>
              <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/40 p-2 rounded-xl border border-border">
                <span>📁 {category}</span>
                {price && <span>• ₹{price.toLocaleString()}</span>}
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-foreground uppercase tracking-wider block mb-1.5">
              Key Features / Bullets (Optional, 1 per line)
            </label>
            <textarea
              rows={3}
              value={featuresInput}
              onChange={(e) => setFeaturesInput(e.target.value)}
              placeholder="e.g.&#10;Industry-leading noise cancellation&#10;30-hour battery life with quick charging&#10;Ultra-comfortable lightweight fit"
              className="w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {error && (
            <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive">
              {error}
            </div>
          )}

          {/* Generated Result Preview */}
          {result && (
            <div className="space-y-3 rounded-xl border border-primary/20 bg-primary/5 p-4 animate-in fade-in">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-primary flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" /> Generated Copy Preview
                </span>
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                  <span className="rounded-md bg-muted px-2 py-0.5 font-mono">
                    Provider: {result.provider}
                  </span>
                  {result.cached && (
                    <span className="rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 flex items-center gap-1 font-mono font-medium">
                      <Zap className="h-3 w-3" /> Redis Cache HIT ({result.latency_ms}ms)
                    </span>
                  )}
                </div>
              </div>

              <div className="rounded-xl bg-card p-3 border border-border text-xs leading-relaxed text-foreground max-h-56 overflow-y-auto whitespace-pre-wrap font-sans">
                {result.description}
              </div>

              {result.suggested_tags && result.suggested_tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  <span className="text-[11px] text-muted-foreground">Tags:</span>
                  {result.suggested_tags.map((tag, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-primary/10 text-primary px-2 py-0.5 text-[10px] font-medium"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
          >
            Cancel
          </Button>

          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleGenerate}
              disabled={loading}
              className="gap-1.5"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  Generating...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  {result ? "Regenerate" : "Generate with AI"}
                </>
              )}
            </Button>

            {result && (
              <Button
                type="button"
                size="sm"
                onClick={handleApply}
                className="gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Check className="h-4 w-4" />
                Apply to Product
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIDescriptionModal;
