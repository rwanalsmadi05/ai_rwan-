"""
voice.py
--------
Voice input for farmers and buyers.
1) transcribe(): audio bytes -> Arabic text  (Azure Speech REST API)
2) parse_product(): farmer speech -> structured product
3) parse_order():   buyer speech  -> list of cart items

Parsing uses Claude to understand Palestinian/Jordanian dialect reliably.
A regex fallback keeps it working in demo mode without any keys.
"""
import json
import re
import requests
import config


def transcribe(audio_bytes: bytes, content_type: str = "audio/wav") -> dict:
    """Send audio to Azure Speech and get Arabic text back."""
    if not config.HAS_AZURE_SPEECH:
        return {
            "text": "ضيف بندورة كيلو بثلاث شيكل مية كيلو متوفر",
            "source": "demo",
        }

    region = config.AZURE_SPEECH_REGION
    url = (
        f"https://{region}.stt.speech.microsoft.com/speech/recognition/"
        "conversation/cognitiveservices/v1?language=ar-JO"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": config.AZURE_SPEECH_KEY,
        "Content-Type": content_type,
    }
    r = requests.post(url, headers=headers, data=audio_bytes, timeout=30)
    r.raise_for_status()
    data = r.json()
    return {"text": data.get("DisplayText", ""), "source": "azure"}


# ---------- intent parsing ----------

_PRODUCT_PROMPT = (
    "حلّل جملة المزارع التالية واستخرج المنتج بصيغة JSON فقط بدون أي شرح. "
    'الصيغة: {{"name": "...", "price": رقم, "quantity": رقم, "unit": "kg"}}. '
    'إذا لم يُذكر شيء استخدم null. الجملة: "{text}"'
)
_ORDER_PROMPT = (
    "حلّل طلب المشتري التالي واستخرج المنتجات بصيغة JSON فقط بدون شرح. "
    'الصيغة: {{"items": [{{"name": "...", "quantity": رقم, "unit": "kg"}}]}}. '
    'الجملة: "{text}"'
)

_AR_NUM = {
    "صفر": 0, "وحدة": 1, "واحد": 1, "اثنين": 2, "ثنين": 2, "ثلاث": 3, "تلت": 3,
    "تلاته": 3, "اربع": 4, "أربع": 4, "خمس": 5, "ست": 6, "سبع": 7, "ثمان": 8,
    "تمان": 8, "تسع": 9, "عشر": 10, "عشرة": 10, "مية": 100, "مئة": 100,
}


def _word_to_num(text: str):
    for w, n in _AR_NUM.items():
        if w in text:
            return n
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None


def _claude_json(prompt: str) -> dict | None:
    if not config.HAS_CLAUDE:
        return None
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def parse_product(text: str) -> dict:
    """Farmer: 'ضيف بندورة كيلو بـ3 شيكل 100 كيلو متوفر' -> structured product."""
    parsed = _claude_json(_PRODUCT_PROMPT.format(text=text))
    if parsed:
        parsed["source"] = "claude"
        return parsed

    # Fallback (demo): naive extraction that also understands Arabic number words.
    known = ["بندورة", "خيار", "باذنجان", "كوسا", "فلفل", "زيتون", "ليمون", "تين", "موز", "خس", "زعتر"]
    name = next((k for k in known if k in text), None)

    tokens = text.split()
    nums = []  # (value, token_index)
    for i, tok in enumerate(tokens):
        d = re.search(r"\d+", tok)
        if d:
            nums.append((int(d.group()), i))
        else:
            for w, n in _AR_NUM.items():
                if w in tok and w not in ("كيلو",):
                    nums.append((n, i))
                    break

    price = quantity = None
    # The number right before a currency word is the price.
    for val, idx in nums:
        nxt = tokens[idx + 1] if idx + 1 < len(tokens) else ""
        if "شيكل" in nxt or "دينار" in nxt or "شيكل" in tokens[idx] or "دينار" in tokens[idx]:
            price = val
    # The largest remaining number is the available quantity.
    rest = [v for v, _ in nums if v != price]
    if rest:
        quantity = max(rest)
    if price is None and nums:
        price = nums[0][0]

    return {"name": name, "price": price, "quantity": quantity, "unit": "kg", "source": "demo"}


def parse_order(text: str) -> dict:
    """Buyer: 'بدي كيلو بندورة وخيار' -> list of cart items."""
    parsed = _claude_json(_ORDER_PROMPT.format(text=text))
    if parsed:
        parsed["source"] = "claude"
        return parsed

    known = ["بندورة", "خيار", "باذنجان", "كوسا", "فلفل", "زيتون", "ليمون", "تين", "موز", "خس", "زعتر"]
    items = [{"name": k, "quantity": 1, "unit": "kg"} for k in known if k in text]
    return {"items": items, "source": "demo"}
