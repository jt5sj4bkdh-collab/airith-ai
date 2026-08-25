from dataclasses import dataclass
import aiohttp


BYBIT_URL = "https://api.bybit.com/v5/market/tickers"


@dataclass
class Asset:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    oi_value: float
    funding: float


@dataclass
class MarketSnapshot:
    assets: list[Asset]

    def to_text(self) -> str:
        lines = ["MARKET SNAPSHOT"]
        for a in self.assets:
            lines.append(
                f"{a.symbol}: ${a.price:,.2f} | "
                f"24h {a.change_24h:+.2f}% | "
                f"OI ${a.oi_value:,.0f} | "
                f"funding {a.funding * 100:+.4f}% | "
                f"volume ${a.volume_24h:,.0f}"
            )
        return "\n".join(lines)


async def get_asset(session: aiohttp.ClientSession, symbol: str) -> Asset:
    params = {"category": "linear", "symbol": symbol}
    async with session.get(BYBIT_URL, params=params, timeout=15) as response:
        response.raise_for_status()
        data = await response.json()

    if data.get("retCode") != 0:
        raise RuntimeError(data.get("retMsg", "Bybit API error"))

    item = data["result"]["list"][0]
    return Asset(
        symbol=symbol,
        price=float(item["lastPrice"]),
        change_24h=float(item["price24hPcnt"]) * 100,
        volume_24h=float(item["turnover24h"]),
        oi_value=float(item.get("openInterestValue") or 0),
        funding=float(item.get("fundingRate") or 0),
    )


async def get_market_snapshot() -> MarketSnapshot:
    async with aiohttp.ClientSession() as session:
        assets = await asyncio_gather(
            get_asset(session, "BTCUSDT"),
            get_asset(session, "ETHUSDT"),
        )
    return MarketSnapshot(assets=assets)


async def asyncio_gather(*coroutines):
    import asyncio
    return await asyncio.gather(*coroutines)
