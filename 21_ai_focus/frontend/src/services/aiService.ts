/**
 * Day 21 Enterprise AI Service Client.
 * Communicates with FastAPI AI endpoints supporting:
 * - AI Product Descriptions
 * - Semantic Vector Search
 * - AI Content Moderation
 * - AI Agent & Tool Calling
 * - Redis Cache Analytics
 */

import apiClient from "./apiClient";

export interface GenerateDescriptionPayload {
  name: string;
  category?: string;
  features?: string[];
  price?: number;
  tone?: "engaging" | "professional" | "technical" | "concise" | "luxury";
  target_audience?: string;
}

export interface GeneratedDescriptionResponse {
  product_name: string;
  category: string;
  tone: string;
  description: string;
  suggested_tags: string[];
  provider: string;
  cached: boolean;
  latency_ms: number;
}

export interface SemanticSearchParams {
  q: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  limit?: number;
}

export interface SemanticSearchResultItem {
  id: number;
  name: string;
  category: string;
  price: number;
  stock: number;
  similarity_score: number;
  image_url: string;
  description: string;
}

export interface SemanticSearchResponse {
  query: string;
  total_results: number;
  results: SemanticSearchResultItem[];
  provider: string;
  cached: boolean;
  latency_ms: number;
}

export interface ModerationPayload {
  content: string;
  content_type?: "review" | "comment" | "query" | "product";
}

export interface ModerationResponse {
  is_safe: boolean;
  status: "approved" | "flagged" | "rejected";
  flagged_categories: string[];
  confidence_score: number;
  reason: string;
  censored_content: string;
  cached: boolean;
  provider: string;
}

export interface AgentResponse {
  query: string;
  response: string;
  tool_calls: Array<{
    tool: string;
    arguments: Record<string, any>;
    result: Record<string, any>;
  }>;
  tools_count: number;
  provider: string;
  cached: boolean;
  latency_ms: number;
}

export const aiService = {
  /**
   * Generates SEO-optimized, engaging product description via LLM/Fallback
   */
  async generateDescription(payload: GenerateDescriptionPayload): Promise<GeneratedDescriptionResponse> {
    return apiClient.post<GeneratedDescriptionResponse>(
      "/api/v1/ai/generate-description",
      payload
    );
  },

  /**
   * Performs semantic vector search based on user intent and contextual similarity
   */
  async semanticSearch(params: SemanticSearchParams): Promise<SemanticSearchResponse> {
    return apiClient.get<SemanticSearchResponse>("/api/v1/ai/semantic-search", {
      params,
    });
  },

  /**
   * Moderates user-generated content for safety, profanity, and toxicity
   */
  async moderateContent(payload: ModerationPayload): Promise<ModerationResponse> {
    return apiClient.post<ModerationResponse>("/api/v1/ai/moderate", payload);
  },

  /**
   * Invokes autonomous AI agent with tool calling capabilities
   */
  async invokeAgent(query: string): Promise<AgentResponse> {
    return apiClient.post<AgentResponse>("/api/v1/ai/agent", { query });
  },

  /**
   * Retrieves Redis AI response caching metrics
   */
  async getCacheMetrics(): Promise<{ status: string; metrics: any }> {
    return apiClient.get<{ status: string; metrics: any }>("/api/v1/ai/cache-metrics");
  },

  /**
   * Clears Redis AI response caches
   */
  async clearCache(): Promise<{ status: string; cleared_count: number }> {
    return apiClient.post<{ status: string; cleared_count: number }>("/api/v1/ai/clear-cache");
  },
};

export default aiService;
