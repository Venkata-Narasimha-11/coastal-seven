"""AI Agents & Tool Calling Service.

Implements autonomous AI agent patterns with tool/function calling for:
1. check_product_stock(product_name_or_id)
2. lookup_product_price(product_name_or_id)
3. apply_coupon_calculator(coupon_code, order_amount)
4. check_order_status(order_id)
5. search_catalog(query, max_price)

Supports multi-turn tool calling with Groq/Gemini and deterministic local intent execution.
"""

import json
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.order import Order
from app.models.product import Product
from app.services.ai_cache_service import AICacheService

logger = logging.getLogger("ai_agent_service")

# Coupon definitions
COUPONS = {
    "SAVE10": {"discount_percent": 10, "max_discount": 5000, "min_order": 500},
    "WELCOME20": {"discount_percent": 20, "max_discount": 2000, "min_order": 1000},
    "FLAT500": {"flat_discount": 500, "min_order": 2500},
    "FESTIVE15": {"discount_percent": 15, "max_discount": 3000, "min_order": 1500},
}

# Tool schemas in JSON Schema format (OpenAI / Groq compatible)
AGENT_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "check_product_stock",
            "description": "Check real-time warehouse inventory and stock availability for a product by name or ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name_or_id": {
                        "type": "string",
                        "description": "The exact name, keyword, or integer ID of the product."
                    }
                },
                "required": ["product_name_or_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_product_price",
            "description": "Look up current price, MRP, and discount for a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name_or_id": {
                        "type": "string",
                        "description": "The product name or ID to look up."
                    }
                },
                "required": ["product_name_or_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_coupon_calculator",
            "description": "Calculate discount and final checkout price given a coupon code and order subtotal amount in INR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coupon_code": {
                        "type": "string",
                        "description": "The promo or coupon code (e.g., SAVE10, WELCOME20, FLAT500)."
                    },
                    "order_amount": {
                        "type": "number",
                        "description": "The cart or order amount in Indian Rupees (₹)."
                    }
                },
                "required": ["coupon_code", "order_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Retrieve current tracking status, stage, and total for an order by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The numeric ID of the order."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_catalog",
            "description": "Search the product catalog for items matching a keyword or budget limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Product search query."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price filter in INR."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


class AIAgentService:
    """Enterprise AI Shopping Agent with Autonomous Tool Calling."""

    # -------------------------------------------------------------
    # Tool Implementations
    # -------------------------------------------------------------
    @classmethod
    def execute_check_product_stock(cls, db: Session, product_name_or_id: str) -> Dict[str, Any]:
        """Tool 1: Real-time stock lookup."""
        p_query = db.query(Product).filter(Product.is_active == True)
        if product_name_or_id.isdigit():
            product = p_query.filter(Product.id == int(product_name_or_id)).first()
        else:
            product = p_query.filter(Product.name.ilike(f"%{product_name_or_id.strip()}%")).first()

        if not product:
            return {"found": False, "message": f"No active product found matching '{product_name_or_id}'."}

        status = "In Stock" if product.stock > 10 else ("Low Stock" if product.stock > 0 else "Out of Stock")
        return {
            "found": True,
            "product_id": product.id,
            "product_name": product.name,
            "stock_quantity": product.stock,
            "status": status,
            "in_stock": product.stock > 0,
            "category": product.category.name if product.category else "General",
            "price": float(product.price),
        }

    @classmethod
    def execute_lookup_product_price(cls, db: Session, product_name_or_id: str) -> Dict[str, Any]:
        """Tool 2: Product price lookup."""
        p_query = db.query(Product).filter(Product.is_active == True)
        if product_name_or_id.isdigit():
            product = p_query.filter(Product.id == int(product_name_or_id)).first()
        else:
            product = p_query.filter(Product.name.ilike(f"%{product_name_or_id.strip()}%")).first()

        if not product:
            return {"found": False, "message": f"Product '{product_name_or_id}' not found."}

        return {
            "found": True,
            "product_id": product.id,
            "product_name": product.name,
            "price": float(product.price),
            "formatted_price": f"₹{float(product.price):,.2f}",
            "category": product.category.name if product.category else "General",
        }

    @classmethod
    def execute_apply_coupon_calculator(cls, coupon_code: str, order_amount: float) -> Dict[str, Any]:
        """Tool 3: Coupon and promotional discount calculation."""
        code = coupon_code.strip().upper()
        coupon_data = COUPONS.get(code)

        if not coupon_data:
            valid_codes = ", ".join(COUPONS.keys())
            return {
                "valid": False,
                "message": f"Coupon code '{code}' is invalid. Active coupons are: {valid_codes}.",
            }

        min_order = coupon_data.get("min_order", 0)
        if order_amount < min_order:
            return {
                "valid": False,
                "message": f"Coupon '{code}' requires a minimum order value of ₹{min_order:,.2f}. Current amount is ₹{order_amount:,.2f}.",
            }

        discount = 0.0
        if "flat_discount" in coupon_data:
            discount = float(coupon_data["flat_discount"])
        elif "discount_percent" in coupon_data:
            pct = coupon_data["discount_percent"]
            max_disc = coupon_data.get("max_discount", float("inf"))
            raw_discount = (order_amount * pct) / 100.0
            discount = min(raw_discount, max_disc)

        final_amount = max(0.0, order_amount - discount)
        return {
            "valid": True,
            "coupon_code": code,
            "original_amount": round(order_amount, 2),
            "discount_amount": round(discount, 2),
            "final_amount": round(final_amount, 2),
            "savings_message": f"Coupon {code} successfully applied! You save ₹{discount:,.2f} on your order.",
        }

    @classmethod
    def execute_check_order_status(cls, db: Session, order_id: int) -> Dict[str, Any]:
        """Tool 4: Order status lookup."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"found": False, "message": f"Order #{order_id} could not be found."}

        status_str = order.status.value if hasattr(order.status, "value") else str(order.status)
        return {
            "found": True,
            "order_id": order.id,
            "status": status_str,
            "total_amount": float(order.total_amount),
            "items_count": len(order.order_items) if order.order_items else 0,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "Recently",
        }

    @classmethod
    def execute_search_catalog(cls, db: Session, query: str, max_price: Optional[float] = None) -> Dict[str, Any]:
        """Tool 5: Catalog search tool."""
        q = db.query(Product).filter(Product.is_active == True)
        search_term = f"%{query.strip()}%"
        q = q.filter(Product.name.ilike(search_term) | Product.description.ilike(search_term))
        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        products = q.limit(5).all()
        matches = [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "stock": p.stock,
                "category": p.category.name if p.category else "General"
            }
            for p in products
        ]
        return {"matches": matches, "count": len(matches)}

    # -------------------------------------------------------------
    # Agent Dispatcher & Execution Loop
    # -------------------------------------------------------------
    @classmethod
    def execute_tool(cls, tool_name: str, args: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Dispatches and executes a tool function securely."""
        if tool_name == "check_product_stock":
            return cls.execute_check_product_stock(db, str(args.get("product_name_or_id", "")))
        elif tool_name == "lookup_product_price":
            return cls.execute_lookup_product_price(db, str(args.get("product_name_or_id", "")))
        elif tool_name == "apply_coupon_calculator":
            return cls.execute_apply_coupon_calculator(
                coupon_code=str(args.get("coupon_code", "")),
                order_amount=float(args.get("order_amount", 0.0))
            )
        elif tool_name == "check_order_status":
            return cls.execute_check_order_status(db, int(args.get("order_id", 0)))
        elif tool_name == "search_catalog":
            return cls.execute_search_catalog(
                db,
                query=str(args.get("query", "")),
                max_price=args.get("max_price")
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    @classmethod
    def _local_agent_reasoner(cls, query: str, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
        """Intelligent local agent loop for tool selection and response synthesis when offline."""
        q_lower = query.lower()
        tool_calls: List[Dict[str, Any]] = []

        # 1. Coupon intent detection
        coupon_match = re.search(r"\b(coupon|promo|code|save10|welcome20|flat500|festive15)\b", q_lower)
        amount_match = re.search(r"(\d+(?:\.\d+)?)", query)

        # 2. Stock intent detection
        stock_match = any(w in q_lower for w in ["stock", "available", "left", "inventory", "in stock"])

        # 3. Price intent detection
        price_match = any(w in q_lower for w in ["price", "cost", "how much", "rate", "mrp"])

        # 4. Order status intent detection
        order_match = re.search(r"order\s*(?:#|number|id)?\s*(\d+)", q_lower)

        # Execute detected tools
        product_query = ""
        # Extract potential product name
        for word in ["sony", "apple", "iphone", "samsung", "macbook", "headphone", "shoe", "laptop", "watch"]:
            if word in q_lower:
                product_query = word
                break

        # Tool 1 or 2: Stock or Price Lookup
        if (stock_match or price_match) and product_query:
            if stock_match:
                stock_res = cls.execute_tool("check_product_stock", {"product_name_or_id": product_query}, db)
                tool_calls.append({
                    "tool": "check_product_stock",
                    "arguments": {"product_name_or_id": product_query},
                    "result": stock_res
                })
            else:
                price_res = cls.execute_tool("lookup_product_price", {"product_name_or_id": product_query}, db)
                tool_calls.append({
                    "tool": "lookup_product_price",
                    "arguments": {"product_name_or_id": product_query},
                    "result": price_res
                })

        # Tool 3: Coupon Calculator
        if coupon_match:
            code = "SAVE10"
            for c in COUPONS:
                if c.lower() in q_lower:
                    code = c
                    break
            # Find order amount or fallback to ₹10,000 or price of found product
            amount = 10000.0
            if tool_calls and tool_calls[0]["result"].get("price"):
                amount = float(tool_calls[0]["result"]["price"])
            elif amount_match:
                amount = float(amount_match.group(1))

            coupon_res = cls.execute_tool("apply_coupon_calculator", {"coupon_code": code, "order_amount": amount}, db)
            tool_calls.append({
                "tool": "apply_coupon_calculator",
                "arguments": {"coupon_code": code, "order_amount": amount},
                "result": coupon_res
            })

        # Tool 4: Order Status
        if order_match:
            oid = int(order_match.group(1))
            order_res = cls.execute_tool("check_order_status", {"order_id": oid}, db)
            tool_calls.append({
                "tool": "check_order_status",
                "arguments": {"order_id": oid},
                "result": order_res
            })

        # If no specific tool matched, run catalog search
        if not tool_calls:
            search_res = cls.execute_tool("search_catalog", {"query": query}, db)
            tool_calls.append({
                "tool": "search_catalog",
                "arguments": {"query": query},
                "result": search_res
            })

        # Synthesize friendly answer based on tool outputs
        synthesis_parts = []
        for tc in tool_calls:
            t_name = tc["tool"]
            res = tc["result"]
            if t_name == "check_product_stock":
                if res.get("found"):
                    synthesis_parts.append(
                        f"📦 **Stock Status for {res['product_name']}**: Currently **{res['status']}** with **{res['stock_quantity']} units available** (Price: ₹{res['price']:,.2f})."
                    )
                else:
                    synthesis_parts.append(f"⚠️ {res['message']}")
            elif t_name == "lookup_product_price":
                if res.get("found"):
                    synthesis_parts.append(
                        f"💰 **Pricing**: The **{res['product_name']}** is priced at **{res['formatted_price']}** in our {res['category']} collection."
                    )
                else:
                    synthesis_parts.append(f"⚠️ {res['message']}")
            elif t_name == "apply_coupon_calculator":
                if res.get("valid"):
                    synthesis_parts.append(
                        f"🎉 **Coupon Calculation**: {res['savings_message']}\n"
                        f"• Subtotal: ₹{res['original_amount']:,.2f}\n"
                        f"• Discount: -₹{res['discount_amount']:,.2f}\n"
                        f"• **Final Total: ₹{res['final_amount']:,.2f}**"
                    )
                else:
                    synthesis_parts.append(f"ℹ️ {res['message']}")
            elif t_name == "check_order_status":
                if res.get("found"):
                    synthesis_parts.append(
                        f"🚚 **Order #{res['order_id']} Tracking**: Current status is **{res['status'].upper()}** for {res['items_count']} item(s) totalling ₹{res['total_amount']:,.2f}."
                    )
                else:
                    synthesis_parts.append(f"⚠️ {res['message']}")
            elif t_name == "search_catalog":
                count = res.get("count", 0)
                if count > 0:
                    matches_text = "\n".join([f"• **{m['name']}**: ₹{m['price']:,.2f} ({m['category']})" for m in res["matches"]])
                    synthesis_parts.append(f"🔍 Found {count} matching products in our catalog:\n{matches_text}")
                else:
                    synthesis_parts.append(f"🔍 I searched our catalog for '{query}', but found no direct matches.")

        final_response = "\n\n".join(synthesis_parts)
        return final_response, tool_calls

    @classmethod
    def run_agent(cls, query: str, db: Session, use_cache: bool = True) -> Dict[str, Any]:
        """Runs the AI Agent loop with tool calling, caching, and multi-step reasoning."""
        start_time = time.time()
        cache_key = AICacheService.generate_key(AICacheService.PREFIX_AGENT, {"query": query.strip().lower()})

        # 1. Check Redis Cache
        if use_cache:
            cached_data, is_hit = AICacheService.get(cache_key)
            if is_hit and cached_data:
                cached_data["cached"] = True
                cached_data["latency_ms"] = round((time.time() - start_time) * 1000, 2)
                return cached_data

        tool_calls: List[Dict[str, Any]] = []
        answer = ""
        provider = "local-agent-reasoner"

        # 2. Try LLM Function Calling if Groq API Key is present
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY)
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are SIVORA's autonomous AI Stylist & Shopping Agent. "
                            "Use the provided tools to fetch real-time store data (stock, prices, order status, coupon discounts). "
                            "Always synthesize a clear, elegant, and grounded response citing tool results."
                        )
                    },
                    {"role": "user", "content": query}
                ]
                first_response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=messages,
                    tools=AGENT_TOOL_SCHEMAS,
                    tool_choice="auto",
                    temperature=0.2,
                )
                msg = first_response.choices[0].message
                if msg.tool_calls:
                    messages.append(msg)
                    for tc in msg.tool_calls:
                        t_name = tc.function.name
                        t_args = json.loads(tc.function.arguments or "{}")
                        t_result = cls.execute_tool(t_name, t_args, db)
                        tool_calls.append({
                            "tool": t_name,
                            "arguments": t_args,
                            "result": t_result,
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": t_name,
                            "content": json.dumps(t_result, default=str),
                        })

                    second_response = client.chat.completions.create(
                        model=settings.GROQ_MODEL,
                        messages=messages,
                        temperature=0.3,
                    )
                    answer = second_response.choices[0].message.content
                    provider = "groq-tool-calling"
                else:
                    answer = msg.content
                    provider = "groq-direct"
            except Exception as exc:
                logger.warning("Groq tool-calling agent encountered error (%s). Falling back to local agent...", exc)

        # 3. Fallback to Local Deterministic Agent
        if not answer:
            answer, tool_calls = cls._local_agent_reasoner(query, db)
            provider = "local-agent-reasoner"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        response_payload = {
            "query": query,
            "response": answer,
            "tool_calls": tool_calls,
            "tools_count": len(tool_calls),
            "provider": provider,
            "cached": False,
            "latency_ms": latency_ms,
        }

        # 4. Cache response in Redis (5-minute TTL)
        if use_cache:
            AICacheService.set(cache_key, response_payload, ttl_seconds=300)

        return response_payload
