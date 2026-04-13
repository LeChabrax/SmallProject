"""DM classification helpers extracted from `run_campaign.py` and
`qualify_conversations.py` (which had identical copies).

`classify_last_message` returns one of:
    "send"   : safe to send a campaign message (last DM is from us or is a
               short positive acknowledgement)
    "flag"   : the influencer is waiting for an answer (contains a question
               marker or a polite request)
    "review" : ambiguous — manual review required
"""

from __future__ import annotations

# Markers that signal the influencer is waiting for a response.
QUESTION_SIGNALS = [
    "?",
    "peux-tu", "tu peux", "pourrais-tu", "pourras-tu",
    "est-ce que", "est ce que",
    "quand", "comment", "pourquoi", "qui", "où", "quel", "quelle",
    "c'est quoi", "c est quoi",
    "tu sais", "savez-vous",
    "avez-vous", "as-tu", "aurais-tu",
    "j'attends", "j attends", "en attente",
    "dites-moi", "dis-moi",
]

# Short neutral / positive acknowledgements — safe to ignore.
OK_SIGNALS = [
    "ok", "okay", "oki", "oké",
    "merci", "merci !", "merci beaucoup",
    "super", "parfait", "nickel", "cool", "top",
    "reçu", "bien reçu", "c'est bon", "c est bon",
    "noté", "entendu",
    "👍", "👏", "🙏", "❤️", "😊", "🥰",
    "d'accord", "d accord",
    "pas de souci", "pas de problème",
    "avec plaisir",
]


def classify_last_message(text: str, is_from_us: bool) -> str:
    """Classify the last DM of a thread.

    Args:
        text: last message text (may be empty).
        is_from_us: True if the last message was sent by us (Antoine).

    Returns:
        "send" | "flag" | "review"
    """
    if is_from_us:
        return "send"

    text_lower = (text or "").lower().strip()

    if len(text_lower) <= 60:
        for sig in OK_SIGNALS:
            if sig in text_lower:
                return "send"

    for sig in QUESTION_SIGNALS:
        if sig in text_lower:
            return "flag"

    if len(text_lower) > 60:
        return "review"

    return "review"
