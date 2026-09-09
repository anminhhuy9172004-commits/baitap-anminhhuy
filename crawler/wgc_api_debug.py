import json
import requests


URL = "https://fsapi.gold.org/api/goldprice/v13/chart/price/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": (
        "https://www.gold.org/goldhub/data/gold-prices"
    )
}


def main():

    print("=" * 70)
    print("WGC RAW API DEBUG")
    print("=" * 70)

    response = requests.get(
        URL,
        headers=HEADERS,
        params={
            "cache09092024": ""
        },
        timeout=30
    )

    print(
        "HTTP STATUS:",
        response.status_code
    )

    print(
        "CONTENT TYPE:",
        response.headers.get("content-type")
    )

    print(
        "CONTENT LENGTH:",
        len(response.text)
    )

    print()

    print("=" * 70)
    print("RAW RESPONSE")
    print("=" * 70)

    print(
        response.text
    )

    print()

    # ========================================================
    # TRY JSON
    # ========================================================

    try:

        data = response.json()

        print("=" * 70)
        print("JSON TYPE")
        print("=" * 70)

        print(
            type(data)
        )

        print()

        print("=" * 70)
        print("PRETTY JSON")
        print("=" * 70)

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as e:

        print(
            "JSON ERROR:",
            repr(e)
        )


if __name__ == "__main__":

    main()