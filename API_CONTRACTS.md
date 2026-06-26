# API Contracts — Fallahy AI & Data Service

اتفاقية كل endpoint: شو بياخد (input) وشو بيرجّع (output).
الفريق بيبني على أساس هاي الأشكال. كل الردود JSON.

Base URL (محلياً): `http://localhost:8000`

---

## 1) POST `/api/ai/chat` — مساعد الدردشة

**Input:**
```json
{ "message": "إيمتى بيوصل طلبي؟", "role": "buyer", "history": null }
```
- `role`: `"buyer"` أو `"farmer"`
- `history` (اختياري): `[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]`

**Output:**
```json
{
  "reply": "طلبك عادةً يوصل خلال 25–40 دقيقة...",
  "transfer_to_whatsapp": false,
  "source": "claude"
}
```
- لما `transfer_to_whatsapp` = `true` → التطبيق يحوّل المستخدم لواتساب الطرف الثاني.

---

## 2) POST `/api/voice/transcribe` — صوت لنص

**Input:** ملف صوتي (multipart/form-data، الحقل اسمه `audio`).

**Output:**
```json
{ "text": "ضيف بندورة كيلو بثلاث شيكل مية كيلو متوفر", "source": "azure" }
```

---

## 3) POST `/api/voice/parse-product` — فهم منتج من صوت المزارع

**Input:**
```json
{ "text": "ضيف بندورة كيلو بثلاث شيكل مية كيلو متوفر" }
```

**Output:**
```json
{ "name": "بندورة", "price": 3, "quantity": 100, "unit": "kg", "source": "claude" }
```
→ التطبيق يعبّي حقول "إضافة منتج" تلقائياً من هالنتيجة.

---

## 4) POST `/api/voice/parse-order` — فهم طلب من صوت المشتري

**Input:**
```json
{ "text": "بدي كيلو بندورة وخيار" }
```

**Output:**
```json
{ "items": [
    { "name": "بندورة", "quantity": 1, "unit": "kg" },
    { "name": "خيار",   "quantity": 1, "unit": "kg" }
  ], "source": "claude" }
```
→ التطبيق يضيف هالعناصر للسلة.

---

## 5) GET `/api/maps/nearby-farmers` — المزارعون القريبون

**Input (query params):**
- `lat` (مطلوب) — خط عرض المشتري
- `lng` (مطلوب) — خط طول المشتري
- `radius_km` (اختياري، افتراضي 50)
- `crop` (اختياري) — فلترة بمحصول، مثلاً `بندورة`

مثال: `/api/maps/nearby-farmers?lat=32.46&lng=35.30&radius_km=60&crop=بندورة`

**Output:**
```json
{
  "count": 2,
  "source": "haversine",
  "farmers": [
    {
      "id": "F001", "name": "مزرعة أبو أحمد", "city": "جنين",
      "rating": 4.8, "verified": true,
      "lat": 32.4615, "lng": 35.3008,
      "distance_km": 0.18, "travel_minutes": null,
      "products": [ { "name": "بندورة", "fallahy_price": 3.0, "...": "..." } ]
    }
  ]
}
```
→ مرتّبين من الأقرب للأبعد. `travel_minutes` بيتعبّى لما يكون في مفتاح Azure Maps.

---

## 6) GET `/api/analytics/price-comparison` — مقارنة السعر (لحظة الـ WOW)

**Input:** `?crop=بندورة`

**Output:**
```json
{
  "crop": "بندورة", "name_en": "Tomatoes",
  "market_price": 5.0, "fallahy_price": 3.0,
  "saved": 2.0, "savings_percent": 40,
  "message": "السوق 5.0 ← فلاحي 3.0 — وفّرت 40%!"
}
```

---

## 7) GET `/api/analytics/price-ticker` — شريط الأسعار الحي

**Output:**
```json
{ "ticker": [
    { "crop": "بندورة", "price": 3.0, "change": -0.1, "direction": "down" }
  ] }
```
- `direction`: `"down"` (أرخص = أخضر) / `"up"` (أغلى = أحمر) / `"flat"`.

---

## 8) GET `/api/analytics/price-trend` — اتجاه السعر (للرسم البياني)

**Input:** `?crop=بندورة`

**Output:**
```json
{
  "crop": "بندورة", "name_en": "Tomatoes",
  "series": [ { "date": "2026-06-13", "market": 5.5, "fallahy": 3.3 } ],
  "avg_market": 5.26, "avg_fallahy": 3.13
}
```

---

## 9) GET `/api/analytics/farmer-dashboard` — لوحة المزارع

**Input:** `?farmer_id=F001`

**Output:**
```json
{
  "farmer_id": "F001", "farmer_name": "مزرعة أبو أحمد", "rating": 4.8,
  "product_count": 3, "estimated_daily_revenue": 154.0,
  "best_sellers": [ { "name": "بندورة", "fallahy_price": 3.0 } ],
  "smart_alerts": [ "الطلب على بندورة مرتفع — السعر صاعد، فكّر تزيد الكمية." ]
}
```
