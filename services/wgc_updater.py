import threading
import time

from crawler.gold_wgc import (
    get_wgc_gold_reference
)

from services.wgc_history import (
    init_wgc_db,
    save_wgc_reference,
    get_latest_wgc_reference
)


# ============================================================
# WGC CACHE
# ============================================================

wgc_cache = {
    "status": "loading",
    "symbol": "XAU",
    "name": "Gold Reference Price",
    "price": None,
    "currency": "USD",
    "unit": "USD/oz",
    "source": "World Gold Council",
    "reference_date": None,
    "updated_at": None
}


# ============================================================
# LOAD LATEST DATA FROM DATABASE
# ============================================================

def load_latest_from_database():

    latest = get_latest_wgc_reference()

    if latest is None:

        print(
            "WGC: no previous reference data."
        )

        return False


    wgc_cache.update({

        "status": "success",

        "symbol": latest["symbol"],

        "name": "Gold Reference Price",

        "price": latest["price"],

        "currency": latest["currency"],

        "unit": latest["unit"],

        "source": latest["source"],

        "reference_date": latest["reference_date"],

        "updated_at": latest["updated_at"]

    })


    print(
        "WGC CACHE LOADED:",
        latest["price"],
        latest["reference_date"]
    )


    return True


# ============================================================
# UPDATE WGC
# ============================================================

def update_wgc():

    try:

        print(
            "WGC: checking for new reference data..."
        )


        result = get_wgc_gold_reference()


        if result is None:

            print(
                "WGC: crawler returned no data."
            )

            # Giữ cache hiện tại
            return


        price = result.get(
            "price"
        )


        reference_date = result.get(
            "reference_date"
        )


        updated_at = result.get(
            "updated_at"
        )


        # ====================================================
        # KHÔNG CÓ GIÁ MỚI
        # ====================================================

        if price is None:

            print(
                "WGC: no new price."
            )

            print(
                "WGC: keeping previous reference."
            )

            return


        # ====================================================
        # KHÔNG CÓ NGÀY REFERENCE
        # ====================================================

        if not reference_date:

            print(
                "WGC: missing reference_date."
            )

            print(
                "WGC: keeping previous reference."
            )

            return


        # ====================================================
        # LẤY DỮ LIỆU HIỆN TẠI
        # ====================================================

        latest = get_latest_wgc_reference()


        # ====================================================
        # KIỂM TRA DỮ LIỆU CŨ / MỚI
        # ====================================================

        if latest is not None:

            latest_date = latest[
                "reference_date"
            ]


            # ------------------------------------------------
            # WGC trả về dữ liệu cũ hơn DB
            # ------------------------------------------------

            if reference_date < latest_date:

                print(
                    "WGC: received older data:",
                    reference_date
                )

                print(
                    "WGC: keeping newer data:",
                    latest_date
                )

                # Quan trọng:
                # đảm bảo cache có dữ liệu DB
                load_latest_from_database()

                return


        # ====================================================
        # SAVE
        # ====================================================

        changed = save_wgc_reference(

            symbol=result["symbol"],

            price=price,

            currency=result["currency"],

            unit=result["unit"],

            source=result["source"],

            reference_date=reference_date,

            updated_at=updated_at

        )


        # ====================================================
        # CÓ THAY ĐỔI
        # ====================================================

        if changed:

            print(
                "WGC: new reference data detected."
            )

            load_latest_from_database()


        # ====================================================
        # KHÔNG CÓ THAY ĐỔI
        #
        # Đây là phần quan trọng đã sửa.
        # ====================================================

        else:

            print(
                "WGC: reference data unchanged."
            )

            print(
                "WGC: loading existing reference from DB."
            )

            load_latest_from_database()


    except Exception as e:

        print(
            "WGC UPDATE ERROR:",
            repr(e)
        )

        print(
            "WGC: keeping previous reference."
        )


# ============================================================
# START WGC UPDATER
# ============================================================

def start_wgc_updater(
    interval_seconds=3600
):

    # --------------------------------------------------------
    # Init database
    # --------------------------------------------------------

    init_wgc_db()


    # --------------------------------------------------------
    # LOAD DATA NGAY KHI SERVER START
    #
    # Đây là cơ chế last-known-good.
    # --------------------------------------------------------

    load_latest_from_database()


    # --------------------------------------------------------
    # Worker
    # --------------------------------------------------------

    def worker():

        print(
            "============================================================"
        )

        print(
            "WGC REFERENCE UPDATER STARTED"
        )

        print(
            "WGC CHECK INTERVAL:",
            interval_seconds,
            "seconds"
        )

        print(
            "============================================================"
        )


        # ----------------------------------------------------
        # Check ngay lần đầu
        # ----------------------------------------------------

        update_wgc()


        # ----------------------------------------------------
        # Check định kỳ
        # ----------------------------------------------------

        while True:

            time.sleep(
                interval_seconds
            )

            update_wgc()


    # --------------------------------------------------------
    # Background thread
    # --------------------------------------------------------

    thread = threading.Thread(

        target=worker,

        daemon=True

    )


    thread.start()


    return thread