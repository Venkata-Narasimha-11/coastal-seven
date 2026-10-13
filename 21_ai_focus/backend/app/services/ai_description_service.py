"""AI-Powered Product Description Generator Service.

Generates structured, persuasive, and SEO-optimized e-commerce product descriptions
using multi-provider LLMs (Groq, Gemini), intelligent local heuristic fallback,
and 24-hour Redis response caching.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.ai_cache_service import AICacheService

logger = logging.getLogger("ai_description_service")

DESCRIPTION_SYSTEM_PROMPT = """You are an expert e-commerce copywriter for an upscale online store.
Your goal is to write a compelling, accurate, and high-converting product description based on the provided product details.

Guidelines:
- Tone: {tone}
- Format: Clean GitHub Markdown with:
  1. A catchy headline.
  2. A vibrant product overview (2-3 sentences).
  3. Key Highlights & Features (clean bullet points).
  4. Why You'll Love It / Ideal use cases.
- Avoid repetitive buzzwords and keep it focused and grounded in the provided details.
"""


class AIDescriptionService:
    """Enterprise AI Product Description Generation Service."""

    @classmethod
    def _generate_fallback_description(
        cls,
        name: str,
        category: str,
        features: List[str],
        price: Optional[float],
        tone: str,
        target_audience: Optional[str]
    ) -> Dict[str, Any]:
        """Intelligent Rule-Based Description Generator:

        Produces rich, formatted Markdown e-commerce copy when external LLM APIs are offline.
        """
        formatted_price = f"₹{price:,.2f}" if price else "competitive pricing"
        audience_str = target_audience or f"{category.lower()} enthusiasts and discerning shoppers"

        feature_bullets = ""
        if features:
            for f in features:
                feature_bullets += f"- **{f}**: Built for exceptional performance and daily dependability.\n"
        else:
            feature_bullets = (
                f"- **Premium Build**: Crafted with high-grade materials for enduring durability.\n"
                f"- **Modern Ergonomics**: Thoughtfully engineered for optimal user comfort.\n"
                f"- **Intuitive Experience**: Seamlessly integrates into your modern lifestyle.\n"
            )

        if tone == "technical":
            headline = f"### Engineered Precision: {name}"
            intro = (
                f"The **{name}** is engineered specifically for {audience_str} who demand benchmark reliability. "
                f"Positioned at {formatted_price}, this unit combines industrial-grade components with rigorous standards."
            )
        elif tone == "luxury":
            headline = f"### Elegance Redefined: {name}"
            intro = (
                f"Elevate your daily routine with the masterfully crafted **{name}**. "
                f"Designed for {audience_str}, it offers uncompromising luxury, refined aesthetics, and timeless style."
            )
        elif tone == "concise":
            headline = f"### {name}"
            intro = f"Compact, versatile, and high-performing. The **{name}** delivers outstanding value for {audience_str}."
        else:  # engaging / professional
            headline = f"### Discover Excellence with {name}"
            intro = (
                f"Upgrade your lifestyle with the all-new **{name}**. Perfectly suited for {audience_str}, "
                f"this best-in-class product delivers the ideal harmony of modern design, peak efficiency, and great value at {formatted_price}."
            )

        description = (
            f"{headline}\n\n"
            f"{intro}\n\n"
            f"#### ✨ Key Features & Highlights\n"
            f"{feature_bullets}\n"
            f"#### 🎯 Why You'll Love It\n"
            f"Whether you are upgrading your current setup or shopping for the perfect gift, "
            f"the {name} offers unrivaled reliability backed by SIVORA's verified luxury warranty and rapid delivery."
        )

        return {
            "description": description,
            "provider": "heuristic-engine",
            "suggested_tags": [category.lower(), "bestseller", "premium", tone],
        }

    @classmethod
    def generate_description(
        cls,
        name: str,
        category: str = "General",
        features: Optional[List[str]] = None,
        price: Optional[float] = None,
        tone: str = "engaging",
        target_audience: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Generates a structured product description using Redis cache, LLM providers, and fallback."""
        start_time = time.time()
        features_list = features or []

        # 1. Check Redis Cache
        cache_payload = {
            "name": name,
            "category": category,
            "features": sorted(features_list),
            "price": price,
            "tone": tone,
            "target_audience": target_audience,
        }
        cache_key = AICacheService.generate_key(AICacheService.PREFIX_DESCRIPTION, cache_payload)

        if use_cache:
            cached_data, is_hit = AICacheService.get(cache_key)
            if is_hit and cached_data:
                cached_data["cached"] = True
                cached_data["latency_ms"] = round((time.time() - start_time) * 1000, 2)
                return cached_data

        # 2. Try Primary Provider (Groq)
        generated_result = None
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY)
                prompt = (
                    f"Product Name: {name}\n"
                    f"Category: {category}\n"
                    f"Price: INR {price}\n"
                    f"Key Features: {', '.join(features_list) if features_list else 'Standard flagship features'}\n"
                    f"Target Audience: {target_audience or 'General shoppers'}\n"
                )
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT.format(tone=tone)},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=600,
                )
                content = response.choices[0].message.content
                if content:
                    generated_result = {
                        "description": content,
                        "provider": "groq",
                        "suggested_tags": [category.lower(), tone, "featured"],
                    }
            except Exception as exc:
                logger.warning("Groq description generation failed (%s). Trying Gemini fallback...", exc)

        # 3. Try Secondary Provider (Gemini)
        if not generated_result and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                full_prompt = (
                    f"{DESCRIPTION_SYSTEM_PROMPT.format(tone=tone)}\n\n"
                    f"Product: {name} (Category: {category}, Price: ₹{price})\n"
                    f"Features: {', '.join(features_list)}\n"
                )
                response = model.generate_content(full_prompt)
                if response.text:
                    generated_result = {
                        "description": response.text,
                        "provider": "gemini",
                        "suggested_tags": [category.lower(), tone, "featured"],
                    }
            except Exception as exc:
                logger.warning("Gemini description generation failed (%s). Using local fallback...", exc)

        # 4. Fallback Provider (Deterministic Template Engine)
        if not generated_result:
            generated_result = cls._generate_fallback_description(
                name=name,
                category=category,
                features=features_list,
                price=price,
                tone=tone,
                target_audience=target_audience,
            )

        latency_ms = round((time.time() - start_time) * 1000, 2)
        response_payload = {
            "product_name": name,
            "category": category,
            "tone": tone,
            "description": generated_result["description"],
            "suggested_tags": generated_result.get("suggested_tags", []),
            "provider": generated_result["provider"],
            "cached": False,
            "latency_ms": latency_ms,
        }

        # 5. Populate Redis Cache with 24-hour TTL
        if use_cache:
            AICacheService.set(cache_key, response_payload, ttl_seconds=settings.REDIS_AI_CACHE_TTL_SECONDS)

        return response_payload
