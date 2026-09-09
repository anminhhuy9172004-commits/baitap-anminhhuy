from fastapi import APIRouter

import services.market_updater as market_updater
from services.market_history import get_history


router = APIRouter()


@router.get("/world-oil")
def world_oil():
    data = market_updater.market_cache.get("world_oil")

    if data is None:
        print("[API] Oil cache empty - updating current market...")
        result = market_updater.update_current_market()
        data = result.get("world_oil")

    return data


@router.get("/world-oil/current")
def world_oil_current():
    result = market_updater.market_cache

    if result.get("world_oil") is None:
        result = market_updater.update_current_market()

    return {
        "status": "success",
        "data": result
    }


@router.get("/world-oil/history")
def world_oil_history(
    symbol: str = "Brent",
    hours: int = 24
):
    data = get_history(symbol, hours)

    return {
        "status": "success",
        "symbol": symbol,
        "hours": hours,
        "source": "Yahoo Finance",
        "data": data
    }