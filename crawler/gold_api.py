import requests


GOLD_API_URL = "https://api.gold-api.com/price/XAU"


def get_gold_price():

    response = requests.get(
        GOLD_API_URL,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    price = data.get("price")

    if price is None:
        raise ValueError(
            "Gold API không trả về price"
        )

    return {
        "symbol": "XAU",
        "name": "Gold Spot",
        "price": float(price),
        "currency": "USD",
        "unit": "USD/oz",
        "source": "Gold API",
        "updated_at": data.get("updatedAt")
    }


if __name__ == "__main__":

    print("=" * 40)
    print("GOLD API")
    print("=" * 40)

    result = get_gold_price()

    print(
        "Symbol:",
        result["symbol"]
    )

    print(
        "Name:",
        result["name"]
    )

    print(
        "Price:",
        result["price"]
    )

    print(
        "Currency:",
        result["currency"]
    )

    print(
        "Unit:",
        result["unit"]
    )

    print(
        "Source:",
        result["source"]
    )

    print(
        "Updated:",
        result["updated_at"]
    )