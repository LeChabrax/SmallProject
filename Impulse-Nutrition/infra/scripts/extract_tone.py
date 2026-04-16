#!/usr/bin/env python3
"""Regenerate `instagram_dm_mcp/personality.md` from the local DM archive.

Reads every `infra/data/conversations/*.json` produced by
`infra/scripts/download_conversations.py`, keeps only Antoine's own messages
(`is_sent_by_viewer == true`), and emits a fresh tone guide with real
statistics and anonymized examples.

Safe mode (default) : writes the result to
`instagram_dm_mcp/personality.md.generated`, leaving the existing file alone
so you can diff and merge manually. Pass `--overwrite` to replace
`personality.md` in place (the old file is backed up as
`personality.md.bak.YYYY-MM-DD`).

Usage
-----
    python3 infra/scripts/extract_tone.py --dry-run   # stats only, no file write
    python3 infra/scripts/extract_tone.py              # writes .generated sidecar
    python3 infra/scripts/extract_tone.py --overwrite  # replace personality.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "conversations"
PERSONALITY_PATH = ROOT / "instagram_dm_mcp" / "personality.md"

# Very common French stopwords — strip before vocab analysis.
STOPWORDS_FR = {
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "à", "au", "aux",
    "ce", "ces", "cet", "cette", "en", "est", "pour", "pas", "que", "qui",
    "quoi", "avec", "sur", "par", "sans", "dans", "pour", "sous", "ou", "où",
    "mais", "donc", "or", "ni", "car", "ta", "ton", "tes", "ma", "mon", "mes",
    "sa", "son", "ses", "lui", "leur", "leurs", "il", "elle", "ils", "elles",
    "on", "nous", "vous", "je", "tu", "me", "te", "se", "y", "en", "pas",
    "plus", "très", "si", "oui", "non", "bien", "fait", "faire", "être",
    "avoir", "a", "ai", "as", "ont", "avons", "avez", "eu", "être", "suis",
    "es", "est", "sommes", "êtes", "sont", "était", "étais", "étaient",
    "c'est", "cest", "cela", "ca", "ça", "aussi", "tout", "tous", "toutes",
    "même", "mêmes", "encore", "déjà", "peu", "beaucoup", "trop", "moins",
    "comme", "quand", "alors", "puis", "après", "avant", "entre", "jusqu",
    "vers", "depuis", "pendant", "moi", "toi",
}

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\u2700-\u27BF]+"
)
WORD_RE = re.compile(r"\b[a-zA-ZÀ-ÖØ-öø-ÿ']{3,}\b")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")


# -------------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------------


_METADATA_FILES = {"_index.json", "_progress.json"}


def _load_corpus() -> List[Dict[str, Any]]:
    """Return every `infra/data/conversations/*.json` as a list of dicts.

    Skips only the metadata sidecars (`_index.json`, `_progress.json`).
    Underscore-prefixed usernames (e.g. `_adeloise`) are valid and kept.
    """
    corpus: List[Dict[str, Any]] = []
    if not DATA_DIR.exists():
        return corpus
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name in _METADATA_FILES:
            continue
        try:
            with path.open() as f:
                corpus.append(json.load(f))
        except Exception as e:
            print(f"WARN could not parse {path.name}: {e}", file=sys.stderr)
    return corpus


def _sent_messages(corpus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return messages sent by Antoine (is_sent_by_viewer == true) with text."""
    out: List[Dict[str, Any]] = []
    for conv in corpus:
        statut = conv.get("statut_at_download", "")
        for msg in conv.get("messages", []):
            if not msg.get("is_sent_by_viewer"):
                continue
            text = (msg.get("text") or "").strip()
            if not text:
                continue
            out.append({**msg, "_conv_statut": statut,
                        "_conv_username": conv.get("username")})
    return out


# -------------------------------------------------------------------------
# Analyzers
# -------------------------------------------------------------------------


def _anonymize(text: str) -> str:
    """Replace @usernames and obvious first names with placeholders."""
    text = re.sub(r"@\w+", "{username}", text)
    # Simple heuristic for first names : "Salut Florine", "Hello Marc"
    text = re.sub(
        r"\b(Salut|Hello|Coucou|Hey|Yo|Bonjour|Bonsoir)\s+[A-ZÉÈÀÔÎ][a-zéèàôîûç]+\b",
        r"\1 {prenom}",
        text,
    )
    return text


def _length_stats(msgs: List[Dict[str, Any]]) -> Dict[str, Any]:
    chars = [len(m["text"]) for m in msgs]
    words = [len(m["text"].split()) for m in msgs]
    chars.sort()
    words.sort()

    def pct(arr: List[int], p: float) -> int:
        if not arr:
            return 0
        return arr[int(len(arr) * p)]

    return {
        "n": len(msgs),
        "char_median": pct(chars, 0.5),
        "char_p25": pct(chars, 0.25),
        "char_p75": pct(chars, 0.75),
        "char_max": chars[-1] if chars else 0,
        "word_median": pct(words, 0.5),
        "word_p25": pct(words, 0.25),
        "word_p75": pct(words, 0.75),
        "word_max": words[-1] if words else 0,
    }


def _emoji_stats(msgs: List[Dict[str, Any]], top_n: int = 20) -> List[Tuple[str, int]]:
    counter: Counter = Counter()
    for m in msgs:
        for match in EMOJI_RE.findall(m["text"]):
            for char in match:
                if char.strip():
                    counter[char] += 1
    return counter.most_common(top_n)


def _vocab_stats(msgs: List[Dict[str, Any]], top_n: int = 30) -> List[Tuple[str, int]]:
    counter: Counter = Counter()
    for m in msgs:
        for w in WORD_RE.findall(m["text"].lower()):
            if w in STOPWORDS_FR:
                continue
            counter[w] += 1
    return counter.most_common(top_n)


def _opening_stats(
    msgs: List[Dict[str, Any]], top_n: int = 15
) -> List[Tuple[str, int]]:
    counter: Counter = Counter()
    for m in msgs:
        text = m["text"].strip()
        if not text:
            continue
        tokens = text.split()[:3]
        if tokens:
            key = " ".join(tokens).lower().rstrip(".,!?")
            counter[key] += 1
    return counter.most_common(top_n)


def _closing_stats(
    msgs: List[Dict[str, Any]], top_n: int = 15
) -> List[Tuple[str, int]]:
    counter: Counter = Counter()
    for m in msgs:
        # Strip trailing emoji(s), then take last 3 words.
        text = EMOJI_RE.sub("", m["text"]).strip()
        if not text:
            continue
        tokens = text.split()[-3:]
        if tokens:
            key = " ".join(tokens).lower().rstrip(".,!?")
            counter[key] += 1
    return counter.most_common(top_n)


def _punct_stats(msgs: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = 0
    excl = 0
    quest = 0
    dot = 0
    ellipsis = 0
    for m in msgs:
        t = m["text"]
        total += len(t)
        excl += t.count("!")
        quest += t.count("?")
        dot += t.count(".")
        ellipsis += t.count("...")
    return {
        "excl_per_1k": round(excl * 1000 / max(total, 1), 2),
        "quest_per_1k": round(quest * 1000 / max(total, 1), 2),
        "dot_per_1k": round(dot * 1000 / max(total, 1), 2),
        "ellipsis_per_1k": round(ellipsis * 1000 / max(total, 1), 2),
    }


def _sentences_per_msg(msgs: List[Dict[str, Any]]) -> float:
    if not msgs:
        return 0.0
    total = sum(
        max(1, len([s for s in SENTENCE_SPLIT_RE.split(m["text"]) if s.strip()]))
        for m in msgs
    )
    return round(total / len(msgs), 2)


def _tutoiement_ratio(msgs: List[Dict[str, Any]]) -> float:
    if not msgs:
        return 0.0
    tu_re = re.compile(r"\b(tu|toi|tes|ton|ta|t'|t')\b", re.IGNORECASE)
    vous_re = re.compile(r"\b(vous|votre|vos)\b", re.IGNORECASE)
    tu_hits = 0
    vous_hits = 0
    for m in msgs:
        if tu_re.search(m["text"]):
            tu_hits += 1
        if vous_re.search(m["text"]):
            vous_hits += 1
    total = tu_hits + vous_hits
    return round(tu_hits / total, 3) if total else 1.0


def _classify_message(msg: Dict[str, Any]) -> str:
    """Rough classification for example bucketing."""
    text = msg["text"].lower()
    statut = (msg.get("_conv_statut") or "").lower()

    if re.search(r"\b[A-Z]{4,}\b", msg["text"]) and "code" in text:
        return "envoi_code"
    if any(w in text for w in ["taille", "saveur", "whey", "électrolyte", "preworkout", "flavor"]):
        return "negociation_produits"
    if any(w in text for w in ["toujours là", "nouvelles", "ça avance", "relance", "tjr"]):
        return "relance"
    if statut == "in-cold" or "première" in text or "premier" in text:
        return "premiere_approche"
    if any(w in text for w in ["super", "parfait", "nickel", "cool", "top"]):
        return "reponse_positive"
    return "autre"


def _pick_examples(
    msgs: List[Dict[str, Any]], per_category: int = 5
) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = {}
    for m in msgs:
        cat = _classify_message(m)
        buckets.setdefault(cat, []).append(_anonymize(m["text"]))
    # Pick `per_category` examples per bucket, favor medium-length ones.
    picked: Dict[str, List[str]] = {}
    for cat, items in buckets.items():
        items.sort(key=lambda t: abs(len(t) - 180))
        picked[cat] = items[:per_category]
    return picked


# -------------------------------------------------------------------------
# Markdown generation
# -------------------------------------------------------------------------


def _format_report(
    corpus: List[Dict[str, Any]], msgs: List[Dict[str, Any]]
) -> str:
    length = _length_stats(msgs)
    emojis = _emoji_stats(msgs)
    vocab = _vocab_stats(msgs)
    openings = _opening_stats(msgs)
    closings = _closing_stats(msgs)
    punct = _punct_stats(msgs)
    sent_per_msg = _sentences_per_msg(msgs)
    tutoiement = _tutoiement_ratio(msgs)
    examples = _pick_examples(msgs)

    first_date = min(
        (m.get("date_iso") for m in msgs if m.get("date_iso")),
        default="(unknown)",
    )
    last_date = max(
        (m.get("date_iso") for m in msgs if m.get("date_iso")),
        default="(unknown)",
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines: List[str] = []
    lines.append(f"# Instagram DM — Personnalité d'Antoine ({now})")
    lines.append("")
    lines.append(
        "> Auto-généré par `infra/scripts/extract_tone.py` à partir de "
        f"`infra/data/conversations/*.json`. Dernière régénération : {now}."
    )
    lines.append(
        "> Pour toute modification manuelle, éditer directement ce fichier et "
        "lancer le script avec `--overwrite` pour la prochaine passe."
    )
    lines.append("")
    lines.append("## 1. Vue d'ensemble")
    lines.append("")
    lines.append("- Tutoiement par défaut, ton chaleureux mais pro.")
    lines.append("- Signature longue : **Sportivement, Antoine** (sur les messages ≥ 3 phrases).")
    lines.append("- Emojis modérés — 0 à 2 par message en général. Favoris : voir §5.")
    lines.append("")
    lines.append("## 2. Corpus analysé")
    lines.append("")
    lines.append(f"- **{len(corpus)}** conversations téléchargées")
    lines.append(f"- **{len(msgs)}** messages envoyés (is_sent_by_viewer = true)")
    lines.append(f"- Période : **{first_date[:10]} → {last_date[:10]}**")
    lines.append("")
    lines.append("## 3. Patterns statistiques")
    lines.append("")
    lines.append("### Longueur (caractères)")
    lines.append(
        f"médiane **{length['char_median']}** · p25 {length['char_p25']} · "
        f"p75 {length['char_p75']} · max {length['char_max']}"
    )
    lines.append("")
    lines.append("### Longueur (mots)")
    lines.append(
        f"médiane **{length['word_median']}** · p25 {length['word_p25']} · "
        f"p75 {length['word_p75']} · max {length['word_max']}"
    )
    lines.append("")
    lines.append("### Ponctuation (par 1000 caractères)")
    lines.append(
        f"`!` {punct['excl_per_1k']} · `?` {punct['quest_per_1k']} · "
        f"`.` {punct['dot_per_1k']} · `...` {punct['ellipsis_per_1k']}"
    )
    lines.append("")
    lines.append(f"### Phrases par message : {sent_per_msg}")
    lines.append("")
    lines.append(
        f"### Tutoiement confirmé : **{int(tutoiement*100)} %** des messages "
        "contenant un pronom d'adresse utilisent `tu/toi/tes/ton/ta`"
    )
    lines.append("")
    lines.append("## 4. Top formules d'ouverture")
    lines.append("")
    for phrase, count in openings:
        lines.append(f"- `{phrase}` — {count}")
    lines.append("")
    lines.append("## 5. Top formules de clôture")
    lines.append("")
    for phrase, count in closings:
        lines.append(f"- `{phrase}` — {count}")
    lines.append("")
    lines.append("## 6. Top emojis")
    lines.append("")
    if emojis:
        line = "  ".join(f"{e} ({n})" for e, n in emojis)
        lines.append(line)
    else:
        lines.append("_(aucun emoji détecté)_")
    lines.append("")
    lines.append("## 7. Vocabulaire tic (top 30, hors stopwords FR)")
    lines.append("")
    lines.append(", ".join(f"`{w}`({n})" for w, n in vocab))
    lines.append("")
    lines.append("## 8. Exemples anonymisés par catégorie")
    lines.append("")
    category_titles = {
        "premiere_approche": "Première approche (In-cold)",
        "reponse_positive": "Réponse positive",
        "negociation_produits": "Négociation produits",
        "envoi_code": "Envoi de code",
        "relance": "Relance",
        "autre": "Autre",
    }
    for key, title in category_titles.items():
        items = examples.get(key) or []
        if not items:
            continue
        lines.append(f"### {title}")
        lines.append("")
        for ex in items:
            lines.append(f"> {ex}")
            lines.append("")

    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    corpus = _load_corpus()
    if not corpus:
        print(
            f"No conversations found in {DATA_DIR}. Run "
            "`infra/scripts/download_conversations.py` first.",
            file=sys.stderr,
        )
        return 1
    msgs = _sent_messages(corpus)
    print(f"Corpus : {len(corpus)} convs, {len(msgs)} sent messages")

    report = _format_report(corpus, msgs)

    if args.dry_run:
        print(report[:2000])
        print("... [truncated — --dry-run] ...")
        return 0

    if args.overwrite:
        if PERSONALITY_PATH.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            backup = PERSONALITY_PATH.with_suffix(f".md.bak.{stamp}")
            backup.write_text(PERSONALITY_PATH.read_text())
            print(f"Backed up previous personality → {backup.name}")
        PERSONALITY_PATH.write_text(report)
        print(f"Overwrote {PERSONALITY_PATH}")
    else:
        sidecar = PERSONALITY_PATH.with_suffix(".md.generated")
        sidecar.write_text(report)
        print(f"Wrote {sidecar} (safe mode). Review and merge manually, or rerun with --overwrite.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
