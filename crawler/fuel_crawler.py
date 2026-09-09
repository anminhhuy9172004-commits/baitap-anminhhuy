import re
import requests
import cv2
import numpy as np
import pytesseract
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESS

BASE = "https://www.petrolimex.com.vn"
NEWS = BASE + "/ndi/thong-cao-bao-chi.html"

PRODUCTS = [
    ("Xăng sinh học E10 RON 95-V", "VND/liter"),
    ("Xăng sinh học E10 RON 95-III", "VND/liter"),
    ("Xăng sinh học E5 RON 92-II", "VND/liter"),
    ("Điêzen 0,001S-V", "VND/liter"),
    ("Điêzen 0,05S-II", "VND/liter"),
    ("Dầu hỏa 2-K", "VND/liter"),
    ("Mazút N°2B (3,5S)", "VND/kg"),
    ("Mazút 180cst - 0,5S (RMG)", "VND/kg"),
]


def get_article():
    r = requests.get(NEWS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        title = " ".join(a.get_text(" ", strip=True).split())

        if "điều chỉnh giá xăng dầu" in title.lower():
            return title, urljoin(BASE, a["href"])

    raise RuntimeError("Không tìm thấy bài Petrolimex.")


def download(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()

    arr = np.frombuffer(r.content, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def get_image(article_url):
    r = requests.get(article_url, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    html = r.text

    candidates = set()

    # URL files.petrolimex xuất hiện trực tiếp trong HTML
    pattern = (
        r'https?://files\.petrolimex\.com\.vn/'
        r'[^"\'>\s\\]+'
        r'\.(?:jpg|jpeg|png|webp)'
    )

    for url in re.findall(pattern, html, re.I):
        candidates.add(url)

    # href/src/data-src
    for tag in soup.find_all(True):

        for attr in [
            "href",
            "src",
            "data-src",
            "data-original",
            "data-image",
            "srcset",
        ]:

            value = tag.get(attr)

            if not value:
                continue

            for part in value.split(","):

                src = part.strip().split(" ")[0]

                if not src:
                    continue

                url = urljoin(article_url, src)

                if "files.petrolimex.com.vn" in url.lower():
                    candidates.add(url)

    scored = []

    for url in candidates:

        low = url.lower()
        score = 0

        if "/jpgs/" in low:
            score += 1000

        if "/thumbnails/" in low:
            score -= 1000

        for bad in [
            "logo",
            "icon",
            "hover",
            "banner",
            "background",
            "avatar",
        ]:
            if bad in low:
                score -= 500

        scored.append((score, url))

    scored.sort(reverse=True)

    print(f"IMAGE CANDIDATES: {len(scored)}")

    for score, url in scored:

        print("CHECK IMAGE:", url)

        try:
            im = download(url)
        except Exception:
            continue

        if im is None:
            continue

        h, w = im.shape[:2]

        print(f"  SIZE: {w} x {h}")

        if "/jpgs/" in url.lower() and w >= 700 and h >= 400:

            print("PRICE IMAGE:", url)

            return url, im

    raise RuntimeError("Không tìm thấy ảnh bảng giá.")


def get_numbers(text):

    result = []

    for x in re.findall(r"\d[\d\.,]*", text):

        x = re.sub(r"[^\d]", "", x)

        if len(x) == 5:
            result.append(int(x))

    return result


def ocr_cell(cell):

    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=6,
        fy=6,
        interpolation=cv2.INTER_CUBIC
    )

    blur = cv2.GaussianBlur(gray, (0, 0), 1)

    sharp = cv2.addWeighted(
        gray,
        1.8,
        blur,
        -0.8,
        0
    )

    variants = [gray, sharp]

    _, otsu = cv2.threshold(
        sharp,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    variants.append(otsu)

    results = []

    for img in variants:

        for psm in [6, 7, 8, 10, 13]:

            text = pytesseract.image_to_string(
                img,
                config=(
                    f"--psm {psm} "
                    "-c tessedit_char_whitelist=0123456789."
                )
            )

            values = get_numbers(text)

            results.extend(values)

            if values:
                return values[-1]

    return results[-1] if results else None


def ocr_table(im):

    h, w = im.shape[:2]

    print(f"IMAGE: {w} x {h}")

    # ----------------------------------------------------------
    # Vùng bảng dữ liệu
    # ----------------------------------------------------------

    y1 = int(h * 0.27)
    y2 = int(h * 0.75)

    x1 = int(w * 0.62)
    x2 = int(w * 0.995)

    area = im[y1:y2, x1:x2]

    ah, aw = area.shape[:2]

    row_h = ah / 8

    # Hai cột giá
    mid = int(aw * 0.50)

    rows = []

    for i in range(8):

        top = max(
            0,
            int(i * row_h) - 6
        )

        bottom = min(
            ah,
            int((i + 1) * row_h) + 6
        )

        row = area[top:bottom]

        # ----------------------------------------------
        # Cột Vùng 1
        # ----------------------------------------------

        left_cell = row[:, :mid]

        # ----------------------------------------------
        # Cột Vùng 2
        # ----------------------------------------------

        right_cell = row[:, mid:]

        v1 = ocr_cell(left_cell)
        v2 = ocr_cell(right_cell)

        values = []

        if v1 is not None:
            values.append(v1)

        if v2 is not None:
            values.append(v2)

        print(
            f"ROW {i + 1}: "
            f"V1={v1} V2={v2}"
        )

        rows.append(values)

    return rows


def parse(rows):

    if len(rows) != 8:
        return []

    result = []

    for i, row in enumerate(rows):

        if len(row) < 2:
            continue

        v1 = row[0]
        v2 = row[1]

        if not (
            10000 <= v1 <= 99999
            and
            10000 <= v2 <= 99999
        ):
            continue

        result.append({
            "name": PRODUCTS[i][0],
            "unit": PRODUCTS[i][1],
            "region_1": v1,
            "region_2": v2,
        })

    return result


def crawl_fuel_prices():

    print("=" * 60)
    print("PETROLIMEX FUEL CRAWLER")
    print("=" * 60)

    title, article_url = get_article()

    print("ARTICLE:", title)
    print("URL:", article_url)

    image_url, image = get_image(article_url)

    rows = ocr_table(image)

    valid = sum(
        len(row) >= 2
        for row in rows
    )

    print(f"OCR VALID ROWS: {valid}/8")

    if valid != 8:

        return {
            "status": "error",
            "prices": [],
            "message": f"OCR chỉ đọc được {valid}/8 dòng.",
        }

    prices = parse(rows)

    if len(prices) != 8:

        return {
            "status": "error",
            "prices": [],
            "message": f"Parse chỉ tạo được {len(prices)}/8.",
        }

    print("\nFINAL PRICES")

    for p in prices:

        print(
            f"{p['name']}: "
            f"{p['region_1']:,} / "
            f"{p['region_2']:,}"
        )

    return {
        "status": "success",
        "article": title,
        "article_url": article_url,
        "image_url": image_url,
        "prices": prices,
    }


if __name__ == "__main__":

    result = crawl_fuel_prices()

    print("\nFINAL RESULT:")
    print(result)