"""AI Content Moderation Service.

Evaluates user-generated content (reviews, product comments, search queries)
for profanity, toxicity, hate speech, spam/phishing links, and private contact info.
Combines fast regex heuristics, optional LLM semantic analysis, and Redis caching.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.ai_cache_service import AICacheService

logger = logging.getLogger("ai_moderation_service")

# Prohibited patterns and keywords
PROFANITY_PATTERNS = [
    r"\b(damn|hell|ass|bastard|bitch|crap|shit|fuck|dick|piss|cunt|slut|whore)\b",
    r"\b(scam|fraud|fake|cheat|thief|stealing|robbed)\b",
]

HATE_SPEECH_PATTERNS = [
    r"\b(idiot|moron|stupid|loser|hate you|kill yourself|trash)\b",
]

SPAM_PATTERNS = [
    r"(https?:\/\/[^\s]+)",               # External URLs
    r"(www\.[^\s]+)",                      # Web links
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email addresses
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # Phone numbers
    r"\b(free money|earn \$\d+|crypto giveaway|click here|telegram:)\b",  # Spam phrases
]


class AIModerationService:
    """Enterprise Content Moderation Service."""

    @classmethod
    def _heuristic_check(cls, text: str) -> Dict[str, Any]:
        """Runs fast, deterministic regex-based safety checks."""
        flagged_categories: List[str] = []
        censored = text

        # 1. Profanity check
        for pattern in PROFANITY_PATTERNS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                flagged_categories.append("profanity")
                for m in matches:
                    word = m.group()
                    masked = word[0] + ("*" * (len(word) - 1))
                    censored = re.sub(re.escape(word), masked, censored, flags=re.IGNORECASE)

        # 2. Hate speech / toxicity check
        for pattern in HATE_SPEECH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                flagged_categories.append("toxicity")
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                for m in matches:
                    word = m.group()
                    masked = word[0] + ("*" * (len(word) - 1))
                    censored = re.sub(re.escape(word), masked, censored, flags=re.IGNORECASE)

        # 3. Spam and contact info check
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                flagged_categories.append("spam_or_contact_leak")
                censored = re.sub(pattern, "[REDACTED LINK/CONTACT]", censored, flags=re.IGNORECASE)

        unique_categories = list(set(flagged_categories))
        is_safe = len(unique_categories) == 0

        if not is_safe:
            if "profanity" in unique_categories or "toxicity" in unique_categories:
                status = "rejected"
                reason = f"Violates community guidelines: flagged for {', '.join(unique_categories)}."
                confidence = 0.95
            else:
                status = "flagged"
                reason = "Potential spam or unauthorized contact information detected."
                confidence = 0.88
        else:
            status = "approved"
            reason = "Content adheres to safety and community standards."
            confidence = 0.99

        return {
            "is_safe": is_safe,
            "status": status,
            "flagged_categories": unique_categories,
            "confidence_score": confidence,
            "reason": reason,
            "censored_content": censored,
            "provider": "heuristic-engine",
        }

    @classmethod
    def moderate_content(
        cls,
        content: str,
        content_type: str = "review",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Moderates content with Redis caching and multi-tier evaluation.

        Args:
            content: Text to moderate.
            content_type: Context ("review", "comment", "query", "product").
            use_cache: Whether to check and populate Redis cache.

        Returns:
            Dict containing moderation report.
        """
        stripped_content = content.strip()
        if not stripped_content:
            return {
                "is_safe": True,
                "status": "approved",
                "flagged_categories": [],
                "confidence_score": 1.0,
                "reason": "Empty content allowed.",
                "censored_content": "",
                "cached": False,
                "provider": "none",
            }

        # 1. Check Redis Cache
        cache_key = AICacheService.generate_key(
            AICacheService.PREFIX_MODERATION,
            {"text": stripped_content, "type": content_type}
        )
        if use_cache:
            cached_result, is_hit = AICacheService.get(cache_key)
            if is_hit and cached_result:
                cached_result["cached"] = True
                return cached_result

        # 2. Fast Heuristic Check
        result = cls._heuristic_check(stripped_content)

        # 3. Optional LLM Semantic Moderation for nuanced or ambiguous edge cases
        if settings.GROQ_API_KEY and result["is_safe"] and len(stripped_content.split()) > 6:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY)
                prompt = (
                    f"Perform strict content moderation for an e-commerce platform on the following {content_type}.\n"
                    f"Evaluate if it contains hate speech, harassment, scams, or unsafe content.\n"
                    f"Content: \"\"\"{stripped_content}\"\"\"\n"
                    f"Respond ONLY with valid JSON in this format:\n"
                    f'{{"is_safe": true/false, "status": "approved"|"flagged"|"rejected", "categories": [], "reason": "brief reason"}}'
                )
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=200,
                )
                llm_data = json.loads(response.choices[0].message.content)
                if not llm_data.get("is_safe", True):
                    result["is_safe"] = False
                    result["status"] = llm_data.get("status", "flagged")
                    result["flagged_categories"] = llm_data.get("categories", ["semantic_policy_violation"])
                    result["reason"] = llm_data.get("reason", "LLM safety guardrail triggered.")
                    result["provider"] = "groq-guardrail"
            except Exception as exc:
                logger.warning("Optional LLM moderation call skipped/failed: %s", exc)

        result["cached"] = False

        # 4. Save to Redis Cache (1 hour TTL)
        if use_cache:
            AICacheService.set(cache_key, result, ttl_seconds=3600)

        return result
