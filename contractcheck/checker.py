from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .rules import CLAUSES, RISKS, SEVERITY_ORDER

_TASHKEEL = re.compile("[ً-ٰٟۖ-ۭ]")
_TRANS = str.maketrans(
    {
        "ـ": None,  # tatweel
        "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
        "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه",
        **{chr(0x0660 + i): str(i) for i in range(10)},   # Arabic-Indic digits
        **{chr(0x06F0 + i): str(i) for i in range(10)},   # Eastern Arabic-Indic digits
        "٪": "%",
    }
)


def normalize(text: str) -> str:
    """Strip diacritics and tatweel, unify alef/ya/ta-marbuta forms and digits, lower-case Latin."""
    text = _TASHKEEL.sub("", text).translate(_TRANS).lower()
    return re.sub(r"[ \t ]+", " ", text).strip()


def _compile(pattern: str) -> "re.Pattern[str]":
    return re.compile(normalize(pattern))


_CLAUSE_RE = {c.id: [_compile(p) for p in c.patterns] for c in CLAUSES}
_RISK_RE = {r.id: _compile(r.pattern) for r in RISKS}
_SPLIT = re.compile(r"[\n؛;]+|(?<=[^.])\.\s+|\?\s+|؟\s*")


@dataclass(frozen=True)
class Finding:
    kind: str               # "missing" or "risk"
    id: str
    severity: str
    title_en: str
    title_ar: str
    tip_en: str
    tip_ar: str
    excerpts: Tuple[str, ...] = ()
    count: int = 0

    def title(self, lang: str) -> str:
        return self.title_ar if lang == "ar" else self.title_en

    def tip(self, lang: str) -> str:
        return self.tip_ar if lang == "ar" else self.tip_en


@dataclass
class Report:
    contract_kind: str
    findings: List[Finding] = field(default_factory=list)
    clauses_found: List[str] = field(default_factory=list)
    clauses_checked: int = 0

    def worst(self) -> int:
        return max((SEVERITY_ORDER[f.severity] for f in self.findings), default=0)

    def at_least(self, severity: str) -> List[Finding]:
        floor = SEVERITY_ORDER[severity]
        return [f for f in self.findings if SEVERITY_ORDER[f.severity] >= floor]


def _sentences(text: str) -> List[Tuple[str, str]]:
    """Return (original, normalised) pairs, dropping empty sentences."""
    out = []
    for raw in _SPLIT.split(text):
        raw = raw.strip()
        if raw:
            out.append((raw, normalize(raw)))
    return out


def analyze(text: str, kind: str = "sale", max_excerpts: int = 3) -> Report:
    """Review contract text. ``kind`` is ``"sale"`` or ``"lease"``."""
    if kind not in ("sale", "lease"):
        raise ValueError("kind must be 'sale' or 'lease'")
    norm_all = normalize(text)
    sentences = _sentences(text)
    paragraphs = [(raw.strip(), normalize(raw)) for raw in text.split("\n") if raw.strip()]
    report = Report(contract_kind=kind)

    for clause in CLAUSES:
        if kind not in clause.kinds:
            continue
        report.clauses_checked += 1
        if any(rx.search(norm_all) for rx in _CLAUSE_RE[clause.id]):
            report.clauses_found.append(clause.id)
        else:
            report.findings.append(
                Finding("missing", clause.id, clause.severity, clause.en, clause.ar, clause.tip_en, clause.tip_ar)
            )

    for risk in RISKS:
        if kind not in risk.kinds:
            continue
        units = paragraphs if risk.scope == "paragraph" else sentences
        hits = [orig for orig, norm in units if _RISK_RE[risk.id].search(norm)]
        if hits:
            report.findings.append(
                Finding("risk", risk.id, risk.severity, risk.en, risk.ar, risk.tip_en, risk.tip_ar,
                        tuple(h[:240] for h in hits[:max_excerpts]), len(hits))
            )

    report.findings.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.kind != "risk", f.id))
    return report


def to_dict(report: Report) -> Dict:
    return {
        "contract_kind": report.contract_kind,
        "clauses_checked": report.clauses_checked,
        "clauses_found": report.clauses_found,
        "findings": [
            {"kind": f.kind, "id": f.id, "severity": f.severity, "title_en": f.title_en, "title_ar": f.title_ar,
             "tip_en": f.tip_en, "tip_ar": f.tip_ar, "count": f.count, "excerpts": list(f.excerpts)}
            for f in report.findings
        ],
        "disclaimer": DISCLAIMER_EN,
    }


DISCLAIMER_EN = "Automated first-pass review. Not legal advice: have a qualified lawyer review the contract."
DISCLAIMER_AR = "مراجعة آلية أولية وليست استشارة قانونية. اعرض العقد على محامٍ مختص."


def render_text(report: Report, lang: str = "en") -> str:
    ar = lang == "ar"
    lines = []
    head = "فحص عقد" if ar else "Contract review"
    kind = {"sale": "بيع" if ar else "sale", "lease": "إيجار" if ar else "lease"}[report.contract_kind]
    found = len(report.clauses_found)
    lines.append(f"{head} ({kind}): {found}/{report.clauses_checked} " + ("بند موجود" if ar else "expected clauses found"))
    if not report.findings:
        lines.append("لا توجد ملاحظات." if ar else "No findings.")
    labels = {"high": "عالي" if ar else "HIGH", "medium": "متوسط" if ar else "MEDIUM", "low": "منخفض" if ar else "LOW"}
    for f in report.findings:
        tag = ("ناقص" if ar else "MISSING") if f.kind == "missing" else ("خطر" if ar else "RISK")
        lines.append(f"[{labels[f.severity]}] [{tag}] {f.title(lang)}")
        for ex in f.excerpts:
            lines.append(f"    > {ex}")
        if f.count > len(f.excerpts):
            lines.append(f"    ... (+{f.count - len(f.excerpts)})")
        lines.append(f"    - {f.tip(lang)}")
    lines.append("")
    lines.append(DISCLAIMER_AR if ar else DISCLAIMER_EN)
    return "\n".join(lines)
