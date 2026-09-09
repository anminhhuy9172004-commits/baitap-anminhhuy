import threading
import time

from crawler.gold_wgc import get_wgc_gold_reference


def update_gold_reference():

    try:

        data = get_wgc_gold_reference()

        print(
            "WGC SOURCE CHECK:",
            data["status"],
            data["checked_at"]
        )

        return data

    except Exception as e:

        print(
            "WGC UPDATE ERROR:",
            e
        )

        return None


def start_gold_reference_updater():

    def worker():

        print("=" * 60)
        print("WGC REFERENCE UPDATER STARTED")
        print("=" * 60)

        # Kiểm tra lần đầu
        update_gold_reference()

        while True:

            # WGC không phải realtime.
            # Kiểm tra định kỳ mỗi 6 giờ.
            time.sleep(6 * 60 * 60)

            update_gold_reference()

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()

    return thread