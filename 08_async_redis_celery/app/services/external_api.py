import asyncio
import time
from typing import Dict, Any, List


class ExternalApiService:
    """
    Simulates external microservices / third-party REST APIs with I/O latency.
    Used to demonstrate `asyncio.gather()` concurrent execution vs sequential awaits.
    """

    @staticmethod
    async def fetch_weather(city: str, simulated_delay: float = 0.25) -> Dict[str, Any]:
        """Simulate external weather API call."""
        await asyncio.sleep(simulated_delay)
        return {
            "service": "WeatherAPI",
            "city": city,
            "temperature_celsius": 24.5,
            "condition": "Partly Cloudy",
            "latency_seconds": simulated_delay,
        }

    @staticmethod
    async def fetch_currency_rates(base_currency: str = "USD", simulated_delay: float = 0.25) -> Dict[str, Any]:
        """Simulate external currency exchange rates API call."""
        await asyncio.sleep(simulated_delay)
        return {
            "service": "CurrencyAPI",
            "base": base_currency,
            "rates": {"EUR": 0.92, "GBP": 0.79, "INR": 83.45},
            "latency_seconds": simulated_delay,
        }

    @staticmethod
    async def fetch_stock_quote(symbol: str, simulated_delay: float = 0.25) -> Dict[str, Any]:
        """Simulate external stock market pricing API call."""
        await asyncio.sleep(simulated_delay)
        return {
            "service": "StockAPI",
            "symbol": symbol,
            "price": 182.50,
            "currency": "USD",
            "latency_seconds": simulated_delay,
        }

    @staticmethod
    async def run_sequential_demo(city: str, currency: str, stock: str) -> Dict[str, Any]:
        """
        Executes external calls SEQUENTIALLY.
        Total Time = Delay(Weather) + Delay(Currency) + Delay(Stock).
        """
        start = time.perf_counter()
        weather = await ExternalApiService.fetch_weather(city)
        rates = await ExternalApiService.fetch_currency_rates(currency)
        quotes = await ExternalApiService.fetch_stock_quote(stock)
        duration = round(time.perf_counter() - start, 4)

        return {
            "mode": "sequential",
            "duration_seconds": duration,
            "results": {
                "weather": weather,
                "currency": rates,
                "stock": quotes,
            },
        }

    @staticmethod
    async def run_concurrent_demo(city: str, currency: str, stock: str) -> Dict[str, Any]:
        """
        Executes external calls CONCURRENTLY with asyncio.gather().
        Total Time = MAX(Delay(Weather), Delay(Currency), Delay(Stock)).
        """
        start = time.perf_counter()
        weather, rates, quotes = await asyncio.gather(
            ExternalApiService.fetch_weather(city),
            ExternalApiService.fetch_currency_rates(currency),
            ExternalApiService.fetch_stock_quote(stock),
        )
        duration = round(time.perf_counter() - start, 4)

        return {
            "mode": "concurrent (asyncio.gather)",
            "duration_seconds": duration,
            "results": {
                "weather": weather,
                "currency": rates,
                "stock": quotes,
            },
        }
