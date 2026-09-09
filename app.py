import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.fuel import router as fuel_router
from api.world_oil import router as world_oil_router
from api.gold import router as gold_router
from api.news import router as news_router

from services.fuel_updater import start_fuel_updater
from services.market_updater import start_market_updater
from services.gold_updater import start_gold_updater
from services.wgc_updater import start_wgc_updater
from services.news_updater import news_updater


app = FastAPI(
    title="Fuel Market API",
    description="API gia xang dau, thi truong vang va tin tuc",
    version="1.0.0"
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(fuel_router)
app.include_router(world_oil_router)
app.include_router(gold_router)
app.include_router(news_router)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():

    print("=" * 60)
    print("STARTING MARKET API")
    print("=" * 60)

    # --------------------------------------------------------
    # FUEL VIETNAM
    # --------------------------------------------------------

    print("Dang khoi dong Fuel updater...")

    start_fuel_updater(
        interval_seconds=3600
    )

    # --------------------------------------------------------
    # OIL MARKET
    # --------------------------------------------------------

    print("Dang khoi dong Oil market updater...")

    start_market_updater(
        current_interval=300,
        history_interval=1800
    )

    # --------------------------------------------------------
    # GOLD REALTIME
    # --------------------------------------------------------

    print("Dang khoi dong Gold updater...")

    start_gold_updater(
        interval_seconds=60
    )

    # --------------------------------------------------------
    # GOLD REFERENCE
    # --------------------------------------------------------

    print("Dang khoi dong WGC reference updater...")

    start_wgc_updater(
        interval_seconds=3600
    )

    # --------------------------------------------------------
    # NEWS
    # --------------------------------------------------------

    print("Dang khoi dong News updater...")

    asyncio.create_task(
        news_updater()
    )


# ============================================================
# HOME
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )