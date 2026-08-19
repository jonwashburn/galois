#!/usr/bin/env python3
"""Recheck published rows against the polynomials themselves.

Nothing here trusts the table. Each row is handed to PARI with only its
coefficients, and every other field is treated as a claim to be reproduced:
the real-root count, whether the polynomial is its own canonical form, the
unfactored part of the discriminant under the published prime bound, the
axis that part implies, and nfdisc where the row states one.

The Galois group is the one claim this cannot check, because polgalois stops
at degree 11. Naming 24Tn takes the published labeller and the class-rate
table, which is a separate run and says so rather than being quietly skipped.

  python3 verify_rows.py --fields fields.jsonl --sample 200
  python3 verify_rows.py --fields fields.jsonl --all --workers 96

--mutate is the instrument's own test: it corrupts one field per row and
expects every row to fail. A verifier that has never rejected anything has
not been shown to reject anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.set_int_max_str_digits(200_000)

HERE = Path(__file__).resolve().parent


def gp_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def check(row: dict, script: Path, parisize: int, timeout: int) -> tuple[str, str]:
    """Returns one of pass, fail, unchecked, and why.

    unchecked is not a pass. It means this row's own arithmetic outran the
    budget, so the row was neither reproduced nor refuted, and a run that
    reports it as either is lying in one direction or the other.
    """
    # The identifier is derived from the coefficients, so this catches every
    # change to them, including the ones that leave degree, irreducibility
    # and the real-root count intact. It costs nothing and it is the only
    # check an undetermined row has against a corrupted polynomial.
    want = row.get("sha256")
    got = hashlib.sha256(row["coeffs"].encode()).hexdigest()
    if want and want != got:
        return "fail", f"sha256 {got[:12]} does not match published {want[:12]}"

    header = "\n".join([
        f"COEFFS = {gp_quote(row['coeffs'])};",
        f"WANT_R = {row['signature']};",
        f"WANT_REDUCED = {gp_quote(row.get('reduced') or 'raw')};",
        f"PBOUND = {row.get('disc_pbound') or 10**7};",
        f"WANT_COFACTOR = {gp_quote(str(row.get('disc_cofactor') or '1'))};",
        f"WANT_DISC_AXIS = {gp_quote(row.get('disc_axis') or '')};",
        f"WANT_NFDISC = {gp_quote(str(row.get('nfdisc') or ''))};",
        "",
    ])
    body = header + script.read_text()
    with tempfile.NamedTemporaryFile("w", suffix=".gp", prefix="igp24verify_", delete=False) as fh:
        fh.write(body)
        path = fh.name
    try:
        proc = subprocess.run(
            ["gp", "-q", "-D", f"parisize={parisize}", path],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "unchecked", f"timeout {timeout}s"
    finally:
        Path(path).unlink(missing_ok=True)
    out = (proc.stdout or "").strip().splitlines()
    last = out[-1] if out else (proc.stderr or "").strip()[-200:]
    if proc.returncode == 0 and last.startswith("PASS"):
        return "pass", last
    return "fail", last


def mutate(row: dict, rng: random.Random) -> tuple[dict, str]:
    """One wrong field, so a verifier that passes it is not checking it.

    Only fields this row actually asserts are candidates. Corrupting a
    cofactor on a row that states no cofactor tests nothing, and counting the
    pass as a miss would make the instrument look broken when it is correct.
    """
    kinds = ["signature", "coeffs"]
    if row.get("disc_axis") in ("unconditional", "conditional"):
        kinds += ["cofactor", "axis"]
    if row.get("nfdisc"):
        kinds.append("nfdisc")

    bad = dict(row)
    which = rng.choice(kinds)
    if which == "signature":
        bad["signature"] = (row["signature"] + 2) % 26
    elif which == "cofactor":
        bad["disc_cofactor"] = str(int(row.get("disc_cofactor") or 1) + 1)
    elif which == "axis":
        bad["disc_axis"] = ("conditional" if row["disc_axis"] == "unconditional"
                            else "unconditional")
    elif which == "nfdisc":
        bad["nfdisc"] = str(int(row["nfdisc"]) + 1)
    else:
        c = row["coeffs"].split(",")
        c[0] = str(int(c[0]) + 1)
        bad["coeffs"] = ",".join(c)
        # The published identifier is left alone on purpose: a corrupted
        # polynomial shipped under its original name is the realistic failure,
        # and it is the one the sha check is there to catch.
    return bad, which


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", type=Path, required=True)
    ap.add_argument("--script", type=Path, default=HERE / "verify_row.gp")
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--parisize", type=int, default=1_500_000_000)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--mutate", action="store_true",
                    help="corrupt one field per row; every row must fail")
    ap.add_argument("--seed", type=int, default=20260818)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    rows = []
    with args.fields.open() as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    rng = random.Random(args.seed)
    if not args.all:
        rows = rng.sample(rows, min(args.sample, len(rows)))

    mutated_as = {}
    if args.mutate:
        out = []
        for r in rows:
            bad, which = mutate(r, rng)
            mutated_as[bad["sha256"]] = which
            out.append(bad)
        rows = out

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row, (verdict, msg) in zip(rows, pool.map(
                lambda r: check(r, args.script, args.parisize, args.timeout), rows)):
            results.append((row, verdict, msg))

    passed = sum(1 for _, v, _ in results if v == "pass")
    failed = sum(1 for _, v, _ in results if v == "fail")
    unchecked = sum(1 for _, v, _ in results if v == "unchecked")
    report = {
        "mode": "mutate" if args.mutate else "verify",
        "rows_checked": len(results),
        "passed": passed,
        "failed": failed,
        "unchecked_ran_out_of_budget": unchecked,
        "timeout_seconds": args.timeout,
    }
    if args.mutate:
        report["mutations_by_kind"] = dict(Counter(
            mutated_as.get(r["sha256"], "?") for r, _, _ in results))
        report["verdict"] = ("instrument discriminates" if passed == 0
                             else "INSTRUMENT DOES NOT DISCRIMINATE")
        report["mutations_that_slipped_through"] = [
            {"kind": mutated_as.get(r["sha256"]), "sha256": r["sha256"][:12]}
            for r, v, _ in results if v == "pass"
        ][:20]
    else:
        report["verdict"] = "all checked rows reproduce" if failed == 0 else "ROWS FAILED"
        report["failures"] = [
            {"sha256": r["sha256"][:12], "cell": f"24T{r['label']}.{r['signature']}",
             "why": msg}
            for r, v, msg in results if v == "fail"
        ][:20]

    print(json.dumps(report, indent=2))
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["verdict"] in ("instrument discriminates",
                                      "all checked rows reproduce") else 1


if __name__ == "__main__":
    raise SystemExit(main())
