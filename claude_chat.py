"""
claude_chat.py
--------------
The AI chat assistant (Claude API).
- Answers common buyer & farmer questions.
- If Claude is not confident it can help, it flags the reply so the app
  can transfer the user to the other party's WhatsApp.
"""
import json
import config

# System prompts keep Claude focused and on-brand (Levantine Arabic).
BUYER_SYSTEM = (
    "أنت مساعد تطبيق فلاحي، سوق يربط المزارعين بالمستهلكين مباشرة. "
    "جاوب المشتري بالعربية بلهجة بسيطة وواضحة وبإيجاز. "
    "تقدر تجاوب عن: وقت وصول الطلب، الفرق بين العضوي والتقليدي، كيف يطلب، "
    "كيف يدفع، وكيف يتابع طلبه. "
    "إذا السؤال خارج نطاقك أو يحتاج تفاصيل من المزارع نفسه، "
    "ابدأ ردك بالكلمة [TRANSFER] ثم اعتذر بلطف."
)
FARMER_SYSTEM = (
    "أنت مساعد تطبيق فلاحي تساعد المزارع. جاوب بالعربية بإيجاز ووضوح. "
    "تقدر تجاوب عن: كيف يضيف منتج، كيف يقبل أو يرفض طلب، كيف يعمل عرض فلاش، "
    "وكيف يحدّث الأسعار. "
    "إذا السؤال خارج نطاقك، ابدأ ردك بالكلمة [TRANSFER] ثم اعتذر بلطف."
)

# Simple rule-based answers used only when no API key is set (demo fallback).
_DEMO_ANSWERS = {
    "buyer": {
        "وصل": "طلبك عادةً يوصل خلال 25–40 دقيقة حسب المسافة. تقدر تتابعه من شاشة تتبّع الطلب.",
        "عضوي": "العضوي مزروع بدون مبيدات كيماوية. التقليدي قد يستخدم مبيدات مسموحة. الاثنان طازجان ومن نفس اليوم.",
        "دفع": "تقدر تدفع كاش عند الاستلام، أو بالبطاقة، أو من المحفظة داخل التطبيق.",
    },
    "farmer": {
        "منتج": "لإضافة منتج: افتح (منتجاتي) ← (إضافة منتج)، واكتب أو احكي بصوتك اسم المنتج والسعر والكمية.",
        "طلب": "لقبول طلب: افتح (إدارة الطلبات)، اضغط على الطلب الجديد، ثم (قبول). تقدر بعدها تحدّث الحالة.",
        "عرض": "لعمل عرض فلاش: افتح (عرض فلاش)، حدّد المنتج والسعر المخفّض ومدة العرض، وسيصل إشعار لكل متابعيك.",
    },
}


def _demo_reply(message: str, role: str) -> dict:
    answers = _DEMO_ANSWERS.get(role, {})
    for key, ans in answers.items():
        if key in message:
            return {"reply": ans, "transfer_to_whatsapp": False, "source": "demo"}
    return {
        "reply": "[تحويل] هذا السؤال يحتاج المزارع مباشرة. سنحوّلك للواتساب.",
        "transfer_to_whatsapp": True,
        "source": "demo",
    }


def ask(message: str, role: str = "buyer", history: list | None = None) -> dict:
    """
    message  : the user's question (Arabic).
    role     : "buyer" or "farmer".
    history  : optional list of {"role": "user"/"assistant", "content": "..."}.
    returns  : {"reply", "transfer_to_whatsapp", "source"}.
    """
    role = role if role in ("buyer", "farmer") else "buyer"

    if not config.HAS_CLAUDE:
        return _demo_reply(message, role)

    # Real Claude call.
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    system = BUYER_SYSTEM if role == "buyer" else FARMER_SYSTEM
    messages = (history or []) + [{"role": "user", "content": message}]

    resp = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=400,
        system=system,
        messages=messages,
    )
    text = resp.content[0].text.strip()

    transfer = text.startswith("[TRANSFER]")
    if transfer:
        text = text.replace("[TRANSFER]", "").strip()

    return {"reply": text, "transfer_to_whatsapp": transfer, "source": "claude"}
