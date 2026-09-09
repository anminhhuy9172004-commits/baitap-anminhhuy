from datetime import datetime


gold_reference_cache = {
    "status": "not_loaded",
    "symbol": "XAU",
    "name": "Gold Reference Price",
    "price": None,
    "currency": "USD",
    "unit": "USD/oz",
    "source": "World Gold Council",
    "updated_at": None
}


def set_gold_reference(
    price: float,
    updated_at: str | None = None
):
    """
    Cập nhật giá vàng tham chiếu từ World Gold Council.

    WGC reference data không phải realtime feed.
    Chỉ cập nhật khi có dữ liệu/reference mới.
    """

    if price <= 0:
        raise ValueError(
            "Gold reference price must be greater than 0"
        )

    if updated_at is None:
        updated_at = datetime.now().isoformat()

    gold_reference_cache.update({
        "status": "success",
        "symbol": "XAU",
        "name": "Gold Reference Price",
        "price": float(price),
        "currency": "USD",
        "unit": "USD/oz",
        "source": "World Gold Council",
        "updated_at": updated_at
    })


def get_gold_reference():
    """
    Trả về giá vàng tham chiếu hiện tại.
    """

    return gold_reference_cache