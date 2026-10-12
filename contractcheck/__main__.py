import argparse
import json
import sys

from .checker import analyze, render_text, to_dict


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="contractcheck", description="First-pass checklist review of an Arabic contract.")
    p.add_argument("file", help="UTF-8 text file with the contract")
    p.add_argument("--kind", choices=["sale", "lease"], default="sale")
    p.add_argument("--lang", choices=["en", "ar"], default="en", help="Language of the report")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    p.add_argument("--fail-on", choices=["high", "medium", "low", "none"], default="high",
                   help="Exit 1 when a finding at or above this severity exists (default: high)")
    args = p.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"Cannot read {args.file}: {exc}", file=sys.stderr)
        return 2

    report = analyze(text, args.kind)
    if args.json:
        print(json.dumps(to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(render_text(report, args.lang))
    if args.fail_on != "none" and report.at_least(args.fail_on):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
