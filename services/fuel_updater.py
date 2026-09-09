import threading
import time
from crawler.fuel_crawler import crawl_fuel_prices

fuel_cache = {
    "status": "loading",
    "article": None,
    "article_url": None,
    "image_url": None,
    "prices": [],
    "updated_at": None
}


def update_fuel():
    global fuel_cache

    print("FUEL: checking latest Petrolimex data...")

    try:
        result = crawl_fuel_prices()

        if result.get("status") != "success":
            print("FUEL: crawler failed")
            print(result.get("message", "Unknown error"))
            return False

        prices = result.get("prices", [])

        # Chỉ chấp nhận dữ liệu hoàn chỉnh
        if len(prices) != 8:
            print(f"FUEL: rejected {len(prices)}/8 products")
            return False

        # Kiểm tra tất cả giá
        for item in prices:
            if not item.get("region_1") or not item.get("region_2"):
                print("FUEL: invalid price data")
                return False

        fuel_cache.update({
            "status": "success",
            "article": result.get("article"),
            "article_url": result.get("article_url"),
            "image_url": result.get("image_url"),
            "prices": prices,
            "updated_at": time.strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        })

        print("FUEL: cache updated")
        print(f"FUEL: {len(prices)}/8 products")

        return True

    except Exception as e:
        print("FUEL UPDATE ERROR:", e)
        return False


def start_fuel_updater(interval_seconds=3600):
    """
    Update ngay khi server start,
    sau đó kiểm tra mỗi interval_seconds.
    """

    update_fuel()

    def worker():
        while True:
            time.sleep(interval_seconds)
            update_fuel()

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()

    return thread


if __name__ == "__main__":
    update_fuel()
    print("\nCACHE:")
    print(fuel_cache)