import threading
import time

from crawler.world_oil import get_world_oil
from crawler.yahoo_oil import get_yahoo_oil, get_yahoo_history
from services.market_history import init_db, save_price


market_cache = {
    "world_oil": None,
    "yahoo": None,
    "updated_at": None,
}


def update_current_market():
    """Cap nhat gia hien tai, khong ghi vao database."""
    global market_cache

    try:
        world_oil = get_world_oil()
        yahoo = get_yahoo_oil()

        market_cache = {
            "world_oil": world_oil,
            "yahoo": yahoo,
            "updated_at": time.time(),
        }

        print("[MARKET] Current price updated")

        return market_cache

    except Exception as error:
        print("[MARKET] Current price error:", error)
        return market_cache


def update_history():
    """Dong bo history 5 phut tu Yahoo Finance vao SQLite."""
    try:
        init_db()

        brent_history = get_yahoo_history("BZ=F")

        for item in brent_history:
            save_price(
                "Brent",
                item["price"],
                item.get("currency", "USD"),
                "Yahoo Finance",
                item.get("updated_at"),
            )

        print(
            f"[MARKET] Brent history: "
            f"{len(brent_history)} points"
        )

        wti_history = get_yahoo_history("CL=F")

        for item in wti_history:
            save_price(
                "WTI",
                item["price"],
                item.get("currency", "USD"),
                "Yahoo Finance",
                item.get("updated_at"),
            )

        print(
            f"[MARKET] WTI history: "
            f"{len(wti_history)} points"
        )

    except Exception as error:
        print("[MARKET] History error:", error)


def update_market():
    """Test cap nhat current price va history."""

    update_current_market()
    update_history()

    return market_cache


def start_market_updater(
    current_interval=300,
    history_interval=1800,
):
    """Khoi dong background updater."""

    def worker():

        last_history = 0

        while True:

            update_current_market()

            now = time.time()

            if now - last_history >= history_interval:
                update_history()
                last_history = now

            time.sleep(current_interval)

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()

    print(
        "[MARKET] Updater started - "
        f"current: {current_interval}s, "
        f"history: {history_interval}s"
    )

    return thread


if __name__ == "__main__":

    print("===== MARKET UPDATER TEST =====")

    init_db()

    result = update_market()

    print("\n===== RESULT =====")
    print(result)