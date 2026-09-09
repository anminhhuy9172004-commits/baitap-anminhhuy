import requests
from datetime import datetime


URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_price(symbol, name):

    r = requests.get(
        URL.format(symbol),
        params={
            "range": "1d",
            "interval": "1d"
        },
        headers=HEADERS,
        timeout=10
    )

    r.raise_for_status()

    result = r.json()["chart"]["result"][0]
    meta = result["meta"]

    return {
        "name": name,
        "price": meta["regularMarketPrice"],
        "currency": meta["currency"],
        "updated_at": datetime.fromtimestamp(
            meta["regularMarketTime"]
        ).isoformat()
    }


def get_yahoo_history(
    symbol,
    hours=24
):

    r = requests.get(
        URL.format(symbol),
        params={
            "range": "1d",
            "interval": "5m"
        },
        headers=HEADERS,
        timeout=15
    )

    r.raise_for_status()

    result = r.json()["chart"]["result"][0]

    timestamps = result.get(
        "timestamp",
        []
    )

    quote = result.get(
        "indicators",
        {}
    ).get(
        "quote",
        [{}]
    )[0]

    closes = quote.get(
        "close",
        []
    )

    currency = result.get(
        "meta",
        {}
    ).get(
        "currency",
        "USD"
    )

    history = []

    for timestamp, price in zip(
        timestamps,
        closes
    ):

        if price is None:
            continue

        history.append({

            "symbol": symbol,

            "price": float(price),

            "currency": currency,

            "source": "Yahoo Finance",

            "updated_at":
                datetime.fromtimestamp(
                    timestamp
                ).isoformat()

        })


    # Giới hạn đúng 24h
    if len(history) > 288:
        history = history[-288:]


    return history


def get_yahoo_oil():

    return {

        "source": "Yahoo Finance",

        "brent": get_price(
            "BZ=F",
            "Brent Crude Futures"
        ),

        "wti": get_price(
            "CL=F",
            "WTI Crude Futures"
        )

    }


if __name__ == "__main__":

    print(
        "===== YAHOO OIL CURRENT ====="
    )

    print(
        get_yahoo_oil()
    )


    print(
        "\n===== BRENT HISTORY ====="
    )

    brent = get_yahoo_history(
        "BZ=F"
    )

    print(
        "Points:",
        len(brent)
    )

    print(
        brent[-10:]
    )


    print(
        "\n===== WTI HISTORY ====="
    )

    wti = get_yahoo_history(
        "CL=F"
    )

    print(
        "Points:",
        len(wti)
    )

    print(
        wti[-10:]
    )