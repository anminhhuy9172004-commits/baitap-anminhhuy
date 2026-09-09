from fastapi import APIRouter

from services.gold_updater import gold_cache
from services.gold_history import get_gold_history

from services.wgc_updater import (
    wgc_cache
)


router = APIRouter()


# ============================================================
# GOLD REALTIME - GOLD API
# ============================================================

@router.get("/gold")
def get_gold():

    return gold_cache


# ============================================================
# GOLD HISTORY - GOLD API
# ============================================================

@router.get("/gold/history")
def get_gold_history_api(
    symbol: str = "XAU",
    hours: int = 24
):

    if hours <= 0:

        hours = 24


    if hours > 720:

        hours = 720


    return {

        "status":
            "success",

        "symbol":
            symbol,

        "hours":
            hours,

        "data":
            get_gold_history(
                symbol,
                hours
            )

    }


# ============================================================
# GOLD REFERENCE - WORLD GOLD COUNCIL
# ============================================================

@router.get("/gold/reference")
def get_gold_reference_api():

    return wgc_cache