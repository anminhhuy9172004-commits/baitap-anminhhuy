import re
import requests


WGC_URL = "https://www.gold.org/goldhub/data/gold-prices"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    )
}


def discover():

    print("=" * 70)
    print("WGC DATA DISCOVERY")
    print("=" * 70)

    response = requests.get(
        WGC_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    html = response.text

    print(
        "HTTP STATUS:",
        response.status_code
    )

    print(
        "HTML SIZE:",
        len(html)
    )

    print()


    # ========================================================
    # SEARCH URLS
    # ========================================================

    print("=" * 70)
    print("POSSIBLE DATA URLS")
    print("=" * 70)


    urls = re.findall(
        r'https?://[^"\'<>\s]+',
        html
    )


    found_urls = set()


    for url in urls:

        lower = url.lower()

        if any(
            keyword in lower
            for keyword in [
                "api",
                "json",
                "gold",
                "price",
                "data"
            ]
        ):

            found_urls.add(url)


    for url in sorted(found_urls):

        print(url)


    print()


    # ========================================================
    # SEARCH API / JSON PATHS
    # ========================================================

    print("=" * 70)
    print("POSSIBLE API / JSON PATHS")
    print("=" * 70)


    patterns = [

        r'["\']([^"\']*api[^"\']*)["\']',

        r'["\']([^"\']*json[^"\']*)["\']',

        r'["\']([^"\']*gold[^"\']*)["\']',

        r'["\']([^"\']*price[^"\']*)["\']',

        r'["\']([^"\']*reference[^"\']*)["\']',

    ]


    paths = set()


    for pattern in patterns:

        matches = re.findall(
            pattern,
            html,
            flags=re.IGNORECASE
        )


        for match in matches:

            if len(match) < 500:

                paths.add(match)


    for path in sorted(paths):

        print(path)


    print()


    # ========================================================
    # SEARCH JAVASCRIPT FILES
    # ========================================================

    print("=" * 70)
    print("JAVASCRIPT FILES")
    print("=" * 70)


    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE
    )


    for script in scripts:

        print(script)


    print()


    # ========================================================
    # SAVE HTML
    # ========================================================

    output_file = "wgc_page.html"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)


    print(
        "HTML SAVED:",
        output_file
    )

    print("=" * 70)


if __name__ == "__main__":

    try:

        discover()

    except Exception as e:

        print(
            "DISCOVERY ERROR:",
            repr(e)
        )