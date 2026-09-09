import threading
import time

from crawler.gold_api import get_gold_price

from services.gold_history import (
    init_gold_db,
    save_gold_price,
    get_gold_history
)


gold_cache = {
    "status": "loading",
    "symbol": "XAU",
    "name": "Gold Spot",
    "price": None,
    "change_24h": None,
    "currency": "USD",
    "unit": "USD/oz",
    "source": "Gold API",
    "updated_at": None
}


def calculate_change_24h(
    current_price: float,
    symbol: str = "XAU"
):

    try:

        history = get_gold_history(
            symbol=symbol,
            hours=24
        )

        if not history:
            return None

        first_price = history[0]["price"]

        if first_price is None:
            return None

        first_price = float(
            first_price
        )

        if first_price <= 0:
            return None

        change = (
            (current_price - first_price)
            / first_price
        ) * 100

        return round(
            change,
            2
        )

    except Exception as e:

        print(
            "GOLD CHANGE 24H ERROR:",
            e
        )

        return None


def update_gold():

    try:

        data = get_gold_price()

        # ----------------------------------------------------
        # Lưu giá mới vào database trước
        # ----------------------------------------------------

        save_gold_price(
            symbol=data["symbol"],
            price=data["price"],
            currency=data["currency"],
            unit=data["unit"],
            source=data["source"],
            updated_at=data["updated_at"]
        )

        # ----------------------------------------------------
        # Tính thay đổi 24h
        # ----------------------------------------------------

        change_24h = calculate_change_24h(
            current_price=data["price"],
            symbol=data["symbol"]
        )

        # ----------------------------------------------------
        # Update cache
        # ----------------------------------------------------

        gold_cache.update({

            "status": "success",

            "symbol":
                data["symbol"],

            "name":
                data["name"],

            "price":
                data["price"],

            "change_24h":
                change_24h,

            "currency":
                data["currency"],

            "unit":
                data["unit"],

            "source":
                data["source"],

            "updated_at":
                data["updated_at"]

        })

        print(
            "GOLD UPDATED:",
            data["price"],
            data["currency"],
            data["unit"],
            data["updated_at"],
            "| CHANGE 24H:",
            change_24h
        )

    except Exception as e:

        print(
            "GOLD UPDATE ERROR:",
            e
        )


def start_gold_updater(
    interval_seconds: int = 60
):

    init_gold_db()

    def worker():

        print(
            "============================================================"
        )

        print(
            "GOLD UPDATER STARTED"
        )

        print(
            "GOLD UPDATE INTERVAL:",
            interval_seconds,
            "seconds"
        )

        print(
            "============================================================"
        )

        # Lấy ngay lần đầu tiên
        update_gold()

        while True:

            time.sleep(
                interval_seconds
            )

            update_gold()

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()

    return thread