# Fallahy — AI & Data Service (جزء روان)

هاي الخدمة فيها كل الجزء الذكي والتحليلي من مشروع فلاحي:
**مساعد Claude، الإدخال الصوتي (Azure Speech)، خريطة المزارعين (Azure Maps)، وتحليلات الأسعار.**

الفكرة: هاي خدمة مستقلة، بتشتغل لحالها على رابط (مثلاً `http://localhost:8000`).
التطبيق (React Native) أو الباك-إند (Laravel) **بس بينادي الـ endpoints** — ما في تداخل بالكود بيناتنا.

---

## ١. كيف تشغّلها (٣ خطوات)

```bash
# 1) ثبّت المكتبات
pip install -r requirements.txt

# 2) (اختياري) حط المفاتيح
cp .env.example .env      # وعبّي المفاتيح جوّا .env

# 3) شغّل الخدمة
uvicorn main:app --reload --port 8000
```

بعدها افتح بالمتصفّح: **http://localhost:8000/docs**
رح تشوف كل الـ endpoints وتقدر تجرّبها مباشرة بالضغط على "Try it out".

> **مهم:** الخدمة بتشتغل حتى بدون مفاتيح (وضع DEMO ببيانات حقيقية) عشان تقدروا تجرّبوا فوراً.
> لما تحطّوا المفاتيح بتتفعّل المكالمات الحقيقية لـ Azure و Claude تلقائياً.

---

## ٢. كيف تنادوها من التطبيق

### من Laravel (PHP):
```php
$res = Http::get('http://localhost:8000/api/analytics/price-comparison', [
    'crop' => 'بندورة',
]);
$data = $res->json();   // ['market_price'=>5, 'fallahy_price'=>3, 'savings_percent'=>40, ...]
```

### من React Native (JavaScript):
```js
const res = await fetch('http://localhost:8000/api/ai/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'إيمتى بيوصل طلبي؟', role: 'buyer' }),
});
const data = await res.json();   // { reply: "...", transfer_to_whatsapp: false }
```

---

## ٣. الـ Endpoints الجاهزة

| الوظيفة | الطريقة | الرابط |
|---|---|---|
| مساعد الدردشة (Claude) | POST | `/api/ai/chat` |
| تحويل صوت لنص | POST | `/api/voice/transcribe` |
| فهم منتج من صوت المزارع | POST | `/api/voice/parse-product` |
| فهم طلب من صوت المشتري | POST | `/api/voice/parse-order` |
| المزارعون القريبون | GET | `/api/maps/nearby-farmers` |
| مقارنة السعر + التوفير | GET | `/api/analytics/price-comparison` |
| شريط الأسعار الحي | GET | `/api/analytics/price-ticker` |
| اتجاه سعر محصول (للرسم) | GET | `/api/analytics/price-trend` |
| لوحة المزارع | GET | `/api/analytics/farmer-dashboard` |

التفاصيل الكاملة (الـ input والـ output لكل واحد) موجودة بملف **API_CONTRACTS.md**.

---

## ٤. وين تحطّوا المفاتيح

افتحوا ملف `.env` وحطّوا:
- `ANTHROPIC_API_KEY` — لمساعد Claude وفهم الصوت
- `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION` — لتحويل الصوت لنص
- `AZURE_MAPS_KEY` — لوقت الوصول الحقيقي بالخريطة

**ملاحظة أمان:** المفاتيح بتنحط هون بالسيرفر بس — **ما بتنحط أبداً بالموبايل**. التطبيق بينادي هالخدمة، والخدمة هي اللي بتحكي مع Azure و Claude.

---

## ٥. البيانات

ملفات البيانات بمجلد `نفس المجلد (`:
- `farmers.json` — ٦ مزارع حقيقيين (فلسطين + الأردن) بمنتجاتهم وإحداثياتهم
- `prices.json` — تاريخ أسعار ١٤ يوم للتحليلات وشريط الأسعار

بقدروا تبدّلوها ببياناتكم بسهولة، نفس الشكل.
