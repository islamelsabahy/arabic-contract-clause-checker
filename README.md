# arabic-contract-clause-checker

[![CI](https://github.com/islamelsabahy/arabic-contract-clause-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/islamelsabahy/arabic-contract-clause-checker/actions/workflows/ci.yml)

**EN** — A first-pass checklist reviewer for Arabic real estate contracts (sale and lease). It reads a plain-text contract, reports which standard clauses are **missing** (parties, price, delivery date, termination, governing law, ...) and flags **risky wording** (non-refundable payments, termination without notice, penalties with no cap, one-sided discretion, unfilled blanks). Rule-based, offline, Python 3.9+ with no dependencies. Arabic is normalised first, so diacritics, alef/ya/ta-marbuta spelling variants, prefixes like "لل", and Arabic-Indic digits do not hide a clause.

**AR** — أداة مراجعة أولية لعقود العقارات بالعربي (بيع وإيجار). بتقرأ نص العقد وتقولك أي البنود الأساسية **ناقصة** (الأطراف، الثمن، موعد التسليم، الفسخ، القانون الواجب التطبيق...) وتنبّه على **الصياغات الخطرة** (مبالغ لا ترد، فسخ بدون إنذار، غرامات بدون حد أقصى، قرارات بتقدير طرف واحد، فراغات لم تُملأ). بتشتغل أوفلاين من غير مكتبات، وبتوحّد الحروف والتشكيل والأرقام العربية قبل الفحص.

> **Not legal advice / ليست استشارة قانونية.** This is a keyword checklist. It cannot understand context, validity, or Egyptian law specifics, and it will miss problems and raise false alarms. Use it to prepare questions for a lawyer, never instead of one. / هي قائمة فحص بالكلمات المفتاحية فقط؛ اعرض أي عقد على محامٍ مختص.

## Use / الاستخدام

```bash
python -m contractcheck sample-data/sale_good.txt                  # exit 0, no findings
python -m contractcheck sample-data/sale_risky.txt --lang ar       # Arabic report, exit 1
python -m contractcheck sample-data/lease_risky.txt --kind lease
python -m contractcheck contract.txt --json --fail-on medium
```

The file must be UTF-8 text (export Word/PDF to text first). Exit code: `0` clean, `1` a finding at or above `--fail-on` (default `high`), `2` unreadable file.

```python
from contractcheck import analyze
report = analyze(open("contract.txt", encoding="utf-8").read(), kind="sale")
for f in report.findings:
    print(f.severity, f.kind, f.title("ar"), f.excerpts)
```

## What it looks for / ما الذي يفحصه

| Type | Examples |
|---|---|
| Missing clauses (sale, 14) | parties, property, price, payment schedule, delivery date, seller delay penalty, termination, warranty, registration, governing law, force majeure, notice address, date, signatures |
| Missing clauses (lease, 16) | rent, term, permitted use, deposit, rent increase, subletting, return of premises, termination notice, plus the common ones |
| Risky wording | non-refundable money, termination without notice/ruling, automatic termination, penalty with no figure or cap, broad waiver of rights, sole discretion of one party, open-ended delivery extension (sale), rent increase with no percentage (lease), unfilled blanks |

All rules are in [`contractcheck/rules.py`](contractcheck/rules.py): plain Arabic patterns plus an English and Arabic explanation and a suggested fix. Adding a rule is one entry; please add a test with it.

## Limits / حدود

- Keyword matching: a clause mentioned in passing counts as present; a clause worded unusually may be reported missing.
- Severity levels are judgement calls from common practice, not a legal ranking.
- The sample contracts are fictional and deliberately flawed.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Roadmap

- [ ] `.docx` input
- [ ] Per-clause "found at" excerpt for present clauses
- [ ] Mortgage and brokerage contract kinds

## License

MIT
