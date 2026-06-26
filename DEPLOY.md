# خطوات النشر — خلّي الخدمة تشتغل من أي مكان 🌍

الهدف: رابط ثابت زي `https://fallahy-ai.onrender.com` بيشتغل من أي موبايل، أي واي فاي،
بدون مشاكل localhost أو IP. مجاني وما بيتطلّب بطاقة ائتمان.

أضفنا للمشروع ملفّات النشر الجاهزة (`render.yaml`, `Procfile`, `runtime.txt`) فما بتحتاجي تعملي إشي تقني.

---

## الطريقة الأسهل: Render عن طريق GitHub

### الخطوة ١ — ارفعي المشروع على GitHub
1. روحي على https://github.com واعملي repository جديد (مثلاً `fallahy-ai-service`).
2. ارفعي محتويات المجلد (drag & drop من زر "uploading an existing file").
   - **مهم:** لا ترفعي ملف `.env` لو عملتيه (فيه المفاتيح). ملف `.gitignore` بيمنعه تلقائياً.

### الخطوة ٢ — اربطيه بـ Render
1. روحي على https://render.com وسجّلي دخول بحساب GitHub.
2. اضغطي **New +** ← **Web Service**.
3. اختاري الـ repository تبعك (`fallahy-ai-service`).
4. Render رح يقرأ ملف `render.yaml` تلقائياً ويعبّي كل شي. لو سأل يدوياً، حطّي:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### الخطوة ٣ — حطّي المفاتيح (Environment Variables)
بصفحة الـ service، روحي على **Environment** وأضيفي:
| Key | Value |
|---|---|
| `ANTHROPIC_API_KEY` | مفتاح Claude تبعك |
| `AZURE_SPEECH_KEY` | مفتاح Azure Speech |
| `AZURE_SPEECH_REGION` | `westeurope` (أو منطقتك) |
| `AZURE_MAPS_KEY` | مفتاح Azure Maps |

> بدون مفاتيح بيشتغل بوضع demo برضه — بس حطّيهم عشان الديمو الحقيقي.

### الخطوة ٤ — اضغطي Deploy
بعد ٢–٣ دقايق بيطلعلك رابط زي:
```
https://fallahy-ai-service.onrender.com
```
افتحيه + `/docs` للتأكد:
```
https://fallahy-ai-service.onrender.com/docs
```

---

## الخطوة الأخيرة — عطي الرابط لفريقك

فريقك بس بيبدّلوا `localhost:8000` بالرابط الجديد بالتطبيق. مثال:

```js
// قبل
const BASE = 'http://localhost:8000';
// بعد
const BASE = 'https://fallahy-ai-service.onrender.com';

const res = await fetch(`${BASE}/api/analytics/price-comparison?crop=بندورة`);
```

وهيك التطبيق بيشتغل من أي موبايل، أي مكان، عَ Expo Go أو غيره. ✅

---

## ملاحظة وحدة عن الخطة المجانية

سيرفر Render المجاني "بينام" بعد ١٥ دقيقة بدون استخدام، وأول طلب بعدها بياخد ~٣٠ ثانية يصحى.
**حيلة للديمو:** قبل عرضك بدقيقتين، افتحي الرابط مرة وحدة عشان يصحى السيرفر، وبعدها بيكون سريع طول العرض.

---

## بديل سريع لو ما بدك GitHub: Railway
نفس الفكرة على https://railway.app — بيقرأ ملف `Procfile` تلقائياً. ارفعي المشروع، حطّي نفس المفاتيح، وبيطلعلك رابط.
