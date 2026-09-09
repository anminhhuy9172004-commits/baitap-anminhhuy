import requests
from datetime import datetime, timezone


# ============================================================
# WORLD GOLD COUNCIL API
# ============================================================

WGC_PRICE_API = (
    "https://fsapi.gold.org/api/goldprice/v13/chart/price/"
)

WGC_PAGE_URL = (
    "https://www.gold.org/goldhub/data/gold-prices"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": WGC_PAGE_URL
}


# ============================================================
# REQUEST WGC API
# ============================================================

def get_wgc_data():

    response = requests.get(
        WGC_PRICE_API,
        headers=HEADERS,
        params={
            "cache09092024": ""
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# FIND PRICE SERIES
# ============================================================

def find_price_series(obj):

    """
    Tìm mảng dữ liệu có dạng:

        [
            [timestamp, price],
            [timestamp, price],
            ...
        ]

    trong JSON của WGC.
    """

    if isinstance(obj, list):

        # ----------------------------------------------------
        # Kiểm tra xem chính list này có phải price series
        # ----------------------------------------------------

        valid_points = []

        for item in obj:

            if not isinstance(item, list):
                continue

            if len(item) < 2:
                continue

            timestamp = item[0]
            price = item[1]

            try:

                timestamp = float(timestamp)
                price = float(price)

            except (
                TypeError,
                ValueError
            ):

                continue

            if timestamp <= 0:
                continue

            if price <= 0:
                continue

            valid_points.append(
                (
                    timestamp,
                    price
                )
            )


        # ----------------------------------------------------
        # Nếu có nhiều point hợp lệ
        # đây chính là price series
        # ----------------------------------------------------

        if len(valid_points) >= 2:

            return valid_points


        # ----------------------------------------------------
        # Không phải -> tìm sâu hơn
        # ----------------------------------------------------

        for item in obj:

            result = find_price_series(
                item
            )

            if result is not None:

                return result


    elif isinstance(obj, dict):

        for value in obj.values():

            result = find_price_series(
                value
            )

            if result is not None:

                return result


    return None


# ============================================================
# GET AS OF DATE
# ============================================================

def find_as_of_date(obj):

    """
    Tìm chính xác field asOfDate.
    """

    if isinstance(obj, dict):

        if "asOfDate" in obj:

            value = obj["asOfDate"]

            if value:

                return str(value)


        for value in obj.values():

            result = find_as_of_date(
                value
            )

            if result is not None:

                return result


    elif isinstance(obj, list):

        for item in obj:

            result = find_as_of_date(
                item
            )

            if result is not None:

                return result


    return None


# ============================================================
# GET GOLD REFERENCE
# ============================================================

def get_wgc_gold_reference():

    print(
        "WGC: requesting reference data..."
    )


    data = get_wgc_data()


    # ========================================================
    # FIND PRICE SERIES
    # ========================================================

    price_series = find_price_series(
        data
    )


    if not price_series:

        raise ValueError(
            "Không tìm thấy price series "
            "trong WGC API response."
        )


    # ========================================================
    # LATEST PRICE
    # ========================================================

    latest_timestamp, latest_price = max(
        price_series,
        key=lambda x: x[0]
    )


    # ========================================================
    # WGC AS OF DATE
    # ========================================================

    as_of_date = find_as_of_date(
        data
    )


    # ========================================================
    # FALLBACK DATE
    # ========================================================

    if not as_of_date:

        as_of_date = datetime.fromtimestamp(
            latest_timestamp / 1000,
            tz=timezone.utc
        ).strftime(
            "%Y-%m-%d"
        )


    updated_at = datetime.now(
        timezone.utc
    ).isoformat()


    # ========================================================
    # LOG
    # ========================================================

    print(
        "WGC PRICE:",
        latest_price
    )

    print(
        "WGC REFERENCE DATE:",
        as_of_date
    )

    print(
        "WGC DATA POINTS:",
        len(price_series)
    )


    # ========================================================
    # RESULT
    # ========================================================

    return {

        "status":
            "success",

        "symbol":
            "XAU",

        "name":
            "Gold Reference Price",

        "price":
            latest_price,

        "currency":
            "USD",

        "unit":
            "USD/oz",

        "source":
            "World Gold Council",

        "reference_date":
            as_of_date,

        "updated_at":
            updated_at,

        "url":
            WGC_PRICE_API

    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "WORLD GOLD COUNCIL"
    )

    print(
        "=" * 60
    )


    try:

        result = get_wgc_gold_reference()


        print()


        for key, value in result.items():

            print(
                f"{key}: {value}"
            )


    except Exception as e:

        print(
            "WGC ERROR:",
            repr(e)
        )