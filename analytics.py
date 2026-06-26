"""
analytics.py
------------
The data-analysis layer. Pure computation on real price history.
- price_comparison(): market vs Fallahy + savings %  (the WOW moment)
- price_ticker():     live up/down per crop, stock-market style
- price_trend():      time series for a crop chart
- farmer_dashboard(): revenue, best sellers, simple demand signal
"""
import json
import statistics
import config

_PRICES = json.loads((config.DATA_DIR / "prices.json").read_text(encoding="utf-8"))["crops"]
_FARMERS = json.loads((config.DATA_DIR / "farmers.json").read_text(encoding="utf-8"))["farmers"]


def price_comparison(crop: str) -> dict:
    """Market price vs Fallahy price + savings for one crop (latest day)."""
    data = _PRICES.get(crop)
    if not data:
        return {"error": f"crop '{crop}' not found"}
    latest = data["history"][-1]
    market, fallahy = latest["market"], latest["fallahy"]
    saved = round(market - fallahy, 2)
    pct = round((saved / market) * 100)
    return {
        "crop": crop,
        "name_en": data["name_en"],
        "market_price": market,
        "fallahy_price": fallahy,
        "saved": saved,
        "savings_percent": pct,
        "message": f"السوق {market} ← فلاحي {fallahy} — وفّرت {pct}%!",
    }


def price_ticker() -> dict:
    """Stock-market style ticker: each crop with direction vs yesterday."""
    ticker = []
    for crop, data in _PRICES.items():
        hist = data["history"]
        today, yesterday = hist[-1]["fallahy"], hist[-2]["fallahy"]
        change = round(today - yesterday, 2)
        direction = "down" if change < 0 else ("up" if change > 0 else "flat")
        ticker.append({
            "crop": crop,
            "name_en": data["name_en"],
            "price": today,
            "change": change,
            "direction": direction,  # buyers love "down" = cheaper
        })
    return {"ticker": ticker}


def price_trend(crop: str) -> dict:
    """Full time series for a line chart."""
    data = _PRICES.get(crop)
    if not data:
        return {"error": f"crop '{crop}' not found"}
    return {
        "crop": crop,
        "name_en": data["name_en"],
        "series": data["history"],
        "avg_market": round(statistics.mean(d["market"] for d in data["history"]), 2),
        "avg_fallahy": round(statistics.mean(d["fallahy"] for d in data["history"]), 2),
    }


def farmer_dashboard(farmer_id: str) -> dict:
    """Revenue snapshot, best sellers, and a simple demand signal per crop."""
    farmer = next((f for f in _FARMERS if f["id"] == farmer_id), None)
    if not farmer:
        return {"error": f"farmer '{farmer_id}' not found"}

    products = farmer["products"]
    # Simple demand signal: if a crop's market price is rising over the last
    # 3 recorded days, demand is likely high -> suggest the farmer stock up.
    alerts = []
    for p in products:
        hist = _PRICES.get(p["name"], {}).get("history", [])
        if len(hist) >= 3:
            recent = [d["market"] for d in hist[-3:]]
            if recent[-1] > recent[0]:
                alerts.append(f"الطلب على {p['name']} مرتفع — السعر صاعد، فكّر تزيد الكمية.")
            low_stock = p["quantity"] < 50
            if low_stock:
                alerts.append(f"كمية {p['name']} قليلة ({p['quantity']} {p['unit']}).")

    est_revenue = sum(p["fallahy_price"] * min(p["quantity"], 20) for p in products)
    best = sorted(products, key=lambda x: x["fallahy_price"] * x["quantity"], reverse=True)

    return {
        "farmer_id": farmer_id,
        "farmer_name": farmer["name"],
        "rating": farmer["rating"],
        "product_count": len(products),
        "estimated_daily_revenue": round(est_revenue, 1),
        "best_sellers": [{"name": p["name"], "fallahy_price": p["fallahy_price"]} for p in best[:3]],
        "smart_alerts": alerts or ["كل شي تمام، لا يوجد تنبيهات اليوم."],
    }
