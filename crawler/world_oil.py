import requests


URL = "https://api.oilpriceapi.com/v1/demo/prices"


def get_world_oil():
    """
    Lấy giá dầu thế giới từ OilPriceAPI.
    """

    response = requests.get(
        URL,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    prices = (
        data
        .get("data", {})
        .get("prices", [])
    )

    codes = {
        "BRENT_CRUDE_USD": "Brent",
        "WTI_USD": "WTI",
        "GASOLINE_RBOB_USD": "Gasoline RBOB",
        "GASOLINE_USD": "Gasoline",
        "DIESEL_USD": "Diesel",
        "HEATING_OIL_USD": "Heating Oil",
        "DUBAI_CRUDE_USD": "Dubai Crude",
        "URALS_CRUDE_USD": "Urals Crude"
    }

    result = {}

    for item in prices:

        code = item.get("code")

        if code not in codes:
            continue

        name = codes[code]

        result[name] = {
            "code": item.get("code"),
            "name": item.get("name"),
            "price": item.get("price"),
            "currency": item.get("currency"),
            "updated_at": item.get("updated_at"),
            "change_24h": item.get("change_24h"),
            "source": "OilPriceAPI"
        }

    return {
        "source": "OilPriceAPI",
        "prices": result
    }


if __name__ == "__main__":

    result = get_world_oil()

    print(
        "===== GIÁ DẦU THẾ GIỚI ====="
    )

    for name, item in result["prices"].items():

        print(
            f"{name}: "
            f"{item['price']} "
            f"{item['currency']} "
            f"({item['change_24h']}%)"
        )

        print(
            f"  Cập nhật: "
            f"{item['updated_at']}"
        )