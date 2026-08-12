"""
Case Processing Service
=======================
Rule-based extraction from Indian Kanoon judgment text.
Each extractor is isolated for future LLM replacement.
"""

import re


def process_judgment(text: str) -> dict:
    if not text or len(text.strip()) < 50:
        return _empty()
    return {
        "case_facts":      extract_facts(text),
        "legal_issues":    extract_issues(text),
        "arguments":       extract_arguments(text),
        "court_reasoning": extract_reasoning(text),
        "final_decision":  extract_decision(text),
        "acts_sections":   extract_acts_sections(text),
        "judges":          extract_judges(text),
    }


# ── Acts & Sections ───────────────────────────────────────────────────────────

def extract_acts_sections(text: str) -> str:
    """
    Extract Acts, Sections, Articles mentioned in the judgment.
    Returns comma-separated string.
    """
    found = set()

    patterns = [
        # Section 302 of the Indian Penal Code / Section 302 IPC
        r"[Ss]ection[s]?\s+\d+[A-Za-z]?(?:\s*(?:and|,|&)\s*\d+[A-Za-z]?)*(?:\s+of\s+(?:the\s+)?[A-Z][A-Za-z\s,]+(?:Act|Code|Rules?|Regulations?)\s*,?\s*\d{0,4})?",
        # Article 14, Article 21 of the Constitution
        r"Article[s]?\s+\d+[A-Za-z]?(?:\s*(?:and|,|&)\s*\d+[A-Za-z]?)*(?:\s+of\s+(?:the\s+)?Constitution)?",
        # Order XX Rule 18 CPC
        r"Order\s+[IVXLCDM\d]+\s+Rule\s+\d+[A-Za-z]?",
        # Named Acts: Indian Penal Code, 1860 / Arbitration and Conciliation Act, 1996
        r"(?:the\s+)?[A-Z][A-Za-z\s&,]+(?:Act|Code|Ordinance|Rules?|Regulations?)\s*,?\s*\d{4}",
        # Short forms
        r"\b(?:IPC|CrPC|CPC|IEA|NDPS|POCSO|PMLA|IT Act|GST Act|RTI Act|MV Act)\b",
    ]

    for pat in patterns:
        for m in re.finditer(pat, text):
            val = m.group(0).strip().rstrip(".,;:")
            val = re.sub(r"\s+", " ", val)
            if 3 < len(val) < 120:
                found.add(val)

    # Deduplicate: remove entries that are substrings of longer entries
    sorted_found = sorted(found, key=len, reverse=True)
    deduped = []
    for item in sorted_found:
        if not any(item in longer for longer in deduped):
            deduped.append(item)

    return ", ".join(sorted(deduped)[:40])


# ── Judges ────────────────────────────────────────────────────────────────────

def extract_judges(text: str) -> str:
    # IK text has "Bench: Name1, Name2" near the top
    m = re.search(r"Bench\s*:\s*([^\n]+)", text[:3000], re.IGNORECASE)
    if m:
        return m.group(1).strip()[:250]
    m = re.search(r"(?:BEFORE|CORAM)\s*:?\s*([^\n]+)", text[:3000], re.IGNORECASE)
    if m:
        return m.group(1).strip()[:250]
    # HON'BLE MR. JUSTICE ...
    names = re.findall(
        r"HON'?BLE\s+(?:MR\.?|MS\.?|MRS\.?)?\s*(?:JUSTICE|J\.)\s+([A-Z][A-Za-z\s\.]+?)(?=\n|,|and\b)",
        text[:3000], re.IGNORECASE
    )
    if names:
        return "; ".join(n.strip() for n in names[:4])
    return ""


# ── Facts ─────────────────────────────────────────────────────────────────────

def extract_facts(text: str) -> str:
    # Try labelled section first
    section = _extract_section(text, [
        r"(?:BRIEF\s+)?FACTS?\s+OF\s+(?:THE\s+)?CASE",
        r"STATEMENT\s+OF\s+FACTS?",
        r"BACKGROUND",
        r"BRIEF\s+FACTS?",
        r"FACTS?",
    ])
    if section:
        return section[:2000]

    # Fallback: paragraphs after the header block (skip first ~500 chars of title/bench)
    body = text[500:] if len(text) > 500 else text
    paras = [p.strip() for p in body.split("\n\n") if len(p.strip()) > 100]
    # Take first 4 substantive paragraphs
    return "\n\n".join(paras[:4])[:2000]


# ── Issues ────────────────────────────────────────────────────────────────────

def extract_issues(text: str) -> str:
    section = _extract_section(text, [
        r"ISSUES?\s+(?:RAISED|INVOLVED|FOR\s+(?:CONSIDERATION|DETERMINATION))",
        r"QUESTIONS?\s+(?:OF\s+LAW|BEFORE\s+(?:THE\s+)?COURT)",
        r"POINTS?\s+(?:FOR\s+)?DETERMINATION",
        r"ISSUES?",
    ])
    if section:
        return section[:1500]

    # Heuristic: sentences with "whether", "question", "issue"
    sents = _sentences_with(text, ["whether ", "the question ", "the issue ", "question before"])
    if sents:
        return "\n".join(sents[:8])[:1500]
    return ""


# ── Arguments ─────────────────────────────────────────────────────────────────

def extract_arguments(text: str) -> str:
    section = _extract_section(text, [
        r"ARGUMENTS?\s+(?:OF|BY|FOR)\s+(?:THE\s+)?(?:PARTIES|APPELLANT|PETITIONER|PLAINTIFF|RESPONDENT)",
        r"SUBMISSIONS?\s+(?:OF|BY|FOR)",
        r"CONTENTIONS?\s+(?:OF|BY|FOR)",
        r"ARGUMENTS?",
        r"SUBMISSIONS?",
        r"CONTENTIONS?",
    ])
    if section:
        return section[:2000]

    # Heuristic: sentences with submission/argument keywords
    sents = _sentences_with(text, [
        "submitted that", "argued that", "contended that",
        "urged that", "counsel for", "learned counsel",
        "on behalf of the appellant", "on behalf of the respondent",
    ])
    return "\n".join(sents[:12])[:2000]


# ── Court Reasoning ───────────────────────────────────────────────────────────

def extract_reasoning(text: str) -> str:
    section = _extract_section(text, [
        r"COURT'?S?\s+(?:REASONING|ANALYSIS|OBSERVATIONS?)",
        r"REASONING\s+AND\s+ANALYSIS",
        r"ANALYSIS\s+AND\s+DISCUSSION",
        r"DISCUSSION",
        r"ANALYSIS",
        r"OBSERVATIONS?",
    ])
    if section:
        return section[:2500]

    sents = _sentences_with(text, [
        "we hold", "we find", "we are of the view", "we are of the opinion",
        "the court holds", "the court finds", "the court observes",
        "in our view", "in our opinion", "it is clear that",
        "it is well settled", "it is established",
        "we agree", "we disagree", "we note that",
    ])
    return "\n".join(sents[:15])[:2500]


# ── Final Decision ────────────────────────────────────────────────────────────

def extract_decision(text: str) -> str:
    section = _extract_section(text, [
        r"(?:FINAL\s+)?ORDER",
        r"CONCLUSION",
        r"RESULT",
        r"OPERATIVE\s+PART",
        r"DISPOSED?\s+OF",
    ])
    if section:
        return section[:1000]

    # Sentences with outcome keywords
    sents = _sentences_with(text, [
        "appeal is allowed", "appeal is dismissed", "appeal is partly allowed",
        "petition is allowed", "petition is dismissed",
        "writ is allowed", "writ is dismissed",
        "suit is decreed", "suit is dismissed",
        "accordingly", "in the result", "for the reasons",
        "the appeal stands", "the petition stands",
        "we allow", "we dismiss", "we set aside",
        "is hereby", "are hereby",
    ])
    if sents:
        return "\n".join(sents[:6])[:1000]

    # Last 600 chars of judgment often has the order
    return text[-700:].strip()[:700]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_section(text: str, header_patterns: list, max_chars: int = 2500) -> str:
    """
    Find a labelled section in the text.
    Looks for a header line matching any pattern, then captures text until
    the next all-caps header or end of text.
    """
    combined = "|".join(f"(?:{p})" for p in header_patterns)
    # Match header at start of line (possibly with surrounding whitespace)
    full_pat = rf"(?:^|\n)\s*(?:{combined})\s*\n(.*?)(?=\n\s*[A-Z][A-Z\s]{{4,}}\s*\n|\Z)"
    m = re.search(full_pat, text, re.IGNORECASE | re.DOTALL)
    if m:
        captured = m.group(1).strip()
        captured = re.sub(r"\n{3,}", "\n\n", captured)
        return captured[:max_chars]
    return ""


def _sentences_with(text: str, keywords: list) -> list:
    """Return sentences containing any of the keywords."""
    sentences = re.split(r"(?<=[.!?])\s+|\n", text)
    result = []
    seen = set()
    for s in sentences:
        s = s.strip()
        if len(s) < 30:
            continue
        s_lower = s.lower()
        if any(kw in s_lower for kw in keywords):
            if s not in seen:
                seen.add(s)
                result.append(s)
    return result


def _empty() -> dict:
    return {
        "case_facts":      "",
        "legal_issues":    "",
        "arguments":       "",
        "court_reasoning": "",
        "final_decision":  "",
        "acts_sections":   "",
        "judges":          "",
    }
