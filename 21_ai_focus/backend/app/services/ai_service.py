import json
import logging
import time
from typing import AsyncGenerator, List, Dict, Any, Optional

from app.config import settings
from app.services.ai_agent_service import AIAgentService
from app.services.ai_cache_service import AICacheService
from app.services.ai_moderation_service import AIModerationService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are Gunturu Store's intelligent, friendly AI Shopping Assistant.
Your goal is to guide shoppers, answer product questions, and provide personalized recommendations based exclusively on our store's catalog.

=== CATALOG CONTEXT ===
{context}
=======================

STRICT INSTRUCTIONS:
1. ONLY recommend products that are explicitly listed in the CATALOG CONTEXT above.
2. If the user asks for something not in our catalog, politely clarify that we do not currently carry it and suggest the closest available alternative from the context.
3. Include specific product names, accurate prices in Indian Rupees (₹), and key features.
4. Keep your tone enthusiastic, polite, professional, and concise.
5. End your recommendation with a clean bulleted summary citing the products you recommended.
"""

class AIService:
    """
    Day 21 AI Service:
    Manages multi-provider LLMs (Groq, Gemini), Fallback Strategy,
    Prompt Engineering, SSE Token Streaming, Content Moderation,
    Tool Calling integration, and Redis Caching.
    """

    @classmethod
    def build_prompt(cls, query: str, context: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        system_content = SYSTEM_PROMPT_TEMPLATE.format(context=context)
        messages = [{"role": "system", "content": system_content}]

        # Append last 4 messages from conversation history for multi-turn context
        if history:
            for msg in history[-4:]:
                if msg.get("role") in ["user", "assistant"] and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})
        return messages

    @classmethod
    def _stream_groq(cls, messages: List[Dict[str, str]]) -> Any:
        from groq import Groq
        if not settings.GROQ_API_KEY:
            raise ValueError("Groq API key not configured")
        client = Groq(api_key=settings.GROQ_API_KEY)
        return client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            stream=True
        )

    @classmethod
    def _stream_gemini(cls, messages: List[Dict[str, str]]) -> Any:
        import google.generativeai as genai
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        # Flatten messages to prompt string for Gemini
        user_prompt = messages[-1]["content"]
        system_instruction = messages[0]["content"]
        full_prompt = f"{system_instruction}\n\nUser Question: {user_prompt}"

        return model.generate_content(full_prompt, stream=True)

    @classmethod
    def _generate_mock_stream(
        cls,
        query: str,
        context: str,
        sources: List[Dict[str, Any]],
        tools_executed: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Intelligent Local Fallback Provider:
        Generates contextual recommendations grounded in the ChromaDB retrieved sources
        and any executed application tools.
        """
        tool_intro = ""
        if tools_executed:
            tool_summaries = []
            for t in tools_executed:
                if t.get("tool") == "apply_coupon_calculator" and t.get("result", {}).get("valid"):
                    tool_summaries.append(f"Applied coupon **{t['result']['coupon_code']}** for ₹{t['result']['discount_amount']:,.2f} discount!")
                elif t.get("tool") == "check_product_stock" and t.get("result", {}).get("found"):
                    tool_summaries.append(f"Checked live inventory: **{t['result']['stock_quantity']} units in stock**!")
            if tool_summaries:
                tool_intro = " ℹ️ " + " | ".join(tool_summaries) + "\n\n"

        if not sources:
            text = (
                f"{tool_intro}Hello! Welcome to Gunturu Store. I searched our catalog, but couldn't find exact matches "
                f"for '{query}'. You can browse our categories above or check our top-rated electronics!"
            )
        else:
            top_prod = sources[0]
            recommendations = []
            for s in sources[:3]:
                recommendations.append(
                    f"• **{s['name']}** ({s['category']}): ₹{s['price']:,.2f} — {s['stock']} in stock."
                )
            recs_text = "\n".join(recommendations)

            text = (
                f"{tool_intro}Hello! Based on our current catalog, here are the best recommendations for **'{query}'**:\n\n"
                f"{recs_text}\n\n"
                f"Our top pick is the **{top_prod['name']}** for ₹{top_prod['price']:,.2f}. "
                "You can click on any product card below to view details or add it directly to your shopping cart! "
                "Don't forget to use coupon code **SAVE10** at checkout for an instant 10% discount! 🎁"
            )

        # Break text into word tokens for smooth streaming effect
        words = text.split(" ")
        tokens = []
        for i, word in enumerate(words):
            tokens.append(word + (" " if i < len(words) - 1 else ""))
        return tokens

    @classmethod
    async def stream_chat(
        cls,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        db: Any = None
    ) -> AsyncGenerator[str, None]:
        """
        Server-Sent Events (SSE) generator:
        1. AI Content Moderation Check
        2. RAG Retrieval from ChromaDB
        3. Agent Tool Calling Check (Stock, Coupons, Pricing)
        4. Multi-Provider Fallback (Groq -> Gemini -> Fallback)
        5. Token Streaming & Final Done Event
        """
        # 1. AI Content Moderation Check
        mod_result = AIModerationService.moderate_content(query, content_type="query")
        if not mod_result["is_safe"] and mod_result["status"] == "rejected":
            warning_msg = (
                "⚠️ **Safety Notice**: Your message was flagged for containing prohibited or sensitive content. "
                "Please adhere to our community guidelines so we can assist you."
            )
            yield f"data: {json.dumps({'type': 'token', 'content': warning_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'provider': 'moderation-guardrail'})}\n\n"
            return

        # 2. RAG Retrieval from ChromaDB
        rag_data = RAGService.retrieve_relevant_context(query, n_results=4, db=db)
        context = rag_data["context_text"]
        sources = rag_data["sources"]

        # Yield sources immediately to frontend so product cards render
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

        # 3. Autonomous Tool Calling check if DB session available
        tools_executed: List[Dict[str, Any]] = []
        if db is not None:
            try:
                # Detect and run tools via AIAgentService local reasoner
                _, agent_tools = AIAgentService._local_agent_reasoner(query, db)
                if agent_tools:
                    tools_executed = agent_tools
                    for t in agent_tools:
                        yield f"data: {json.dumps({'type': 'tool_executed', 'tool': t['tool'], 'result': t['result']})}\n\n"
            except Exception as e:
                logger.warning("Tool calling agent check skipped: %s", e)

        messages = cls.build_prompt(query, context, history)
        provider_used = "mock"
        streamed_success = False

        # 4. Try Groq Provider
        if settings.GROQ_API_KEY:
            try:
                logger.info(f"Attempting primary provider: Groq ({settings.GROQ_MODEL})")
                groq_stream = cls._stream_groq(messages)
                for chunk in groq_stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"
                provider_used = "groq"
                streamed_success = True
            except Exception as e:
                logger.warning(f"Groq provider failed ({e}). Falling back to next provider...")

        # 5. Try Gemini Provider (Fallback 1)
        if not streamed_success and settings.GEMINI_API_KEY:
            try:
                logger.info(f"Attempting fallback provider: Gemini ({settings.GEMINI_MODEL})")
                gemini_stream = cls._stream_gemini(messages)
                for chunk in gemini_stream:
                    text_piece = chunk.text or ""
                    if text_piece:
                        yield f"data: {json.dumps({'type': 'token', 'content': text_piece})}\n\n"
                provider_used = "gemini"
                streamed_success = True
            except Exception as e:
                logger.warning(f"Gemini provider failed ({e}). Falling back to local assistant...")

        # 6. Fallback Provider (Grounding in ChromaDB sources + executed tools)
        if not streamed_success:
            logger.info("Using Intelligent Grounded Fallback Provider")
            tokens = cls._generate_mock_stream(query, context, sources, tools_executed)
            for token in tokens:
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                # Typing latency simulation (15ms) for realistic streaming
                time.sleep(0.015)
            provider_used = "fallback-rag"

        # 7. Yield Done Event
        yield f"data: {json.dumps({'type': 'done', 'provider': provider_used})}\n\n"
