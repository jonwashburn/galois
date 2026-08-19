#!/usr/bin/env python3
"""Name the cell a degree-24 polynomial lands on: 24T label and signature.

Reads polynomials, writes the cell. Nothing else is needed: not the base it was
built over, not the element adjoined, not the relation module, not a Galois
closure, not the organizer. The polynomial alone decides.

How it works. Modulo a prime that divides neither the leading coefficient nor
the discriminant, the degrees of the irreducible factors are the cycle type of
a Frobenius element of the Galois group acting on the 24 roots, and Chebotarev
says each cycle type turns up at exactly the frequency of its conjugacy class.
So a few thousand small primes measure the group's class distribution, and that
distribution is compared against all 25,000 transitive groups of degree 24. The
likeliest is the answer. The signature is a real-root count, taken directly.

Verified on 100 fields the organizer has labelled for us: 100 of 100 correct,
scoring every group with no construction data, the winner ahead of the next
best by at least 19 nats. Fed data planted from a deliberately wrong group it
returns that wrong group, 77 of 77, so the answer tracks the evidence. It
separates all 87 pairs that share a base group but not a label.

Prerequisite: the class-rate table at /tmp/shape_laws_24T.jsonl, built once by
shape_law_shard.g and reusable forever, since it is a fact about the groups.

Input is one polynomial per line, either bare rational or integer coefficients
lowest degree first, or JSON with a `polynomial_coefficients` field. Bad primes
are rejected by the squarefree degree-24 factorisation itself, avoiding a huge
discriminant computation on fractional search forms. Output is JSON per line
with the label, the real-root count, and the margin over the runner-up.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

LAWCACHE = Path(os.environ.get(
    "IGP24_SHAPE_LAWS", "/tmp/shape_laws_24T.jsonl"
))
# 1000 primes wins every gate row by at least 19 nats; 300 still gets them all
# but one row came down to 0.76, too thin to run a factory on.
DEFAULT_PRIMES = 1000
# A margin this size has never yet accompanied a wrong answer, but the gate had
# 100 rows, so treat a thinner win as unlabelled rather than as a guess.
MIN_MARGIN = 5.0


def load_laws() -> dict[int, dict[str, float]]:
    if not LAWCACHE.exists():
        sys.exit("missing %s; build it with shape_law_shard.g" % LAWCACHE)
    laws = {}
    for line in LAWCACHE.open():
        if line.strip():
            rec = json.loads(line)
            laws[rec["t"]] = rec["law"]
    return laws


def read_polys(path):
    out = []
    src = sys.stdin if path == "-" else open(path)
    for n, line in enumerate(src):
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            rec = json.loads(line)
            cf = rec.get("polynomial_coefficients", "")
            key = rec.get("id", rec.get("polynomial_sha256", str(n)))
        else:
            cf, key = line, str(n)
        cf = cf.strip().strip("[]")
        if cf:
            # The coefficients become a PARI vector, so they have to be
            # comma-separated by the time they get there. A space-separated
            # line is otherwise read as one arithmetic expression and reported
            # as a degree failure, which looks like a bad polynomial rather
            # than a bad format.
            if "," not in cf:
                cf = ",".join(cf.split())
            out.append((key, cf))
    return out


def measure(polys, nprimes, pmax, parisize):
    """Factorisation shapes over many primes, plus the real-root count.

    Factoring a degree-24 polynomial modulo small primes needs very little
    stack, so the default is small on purpose: an oversized parisize times a
    worker per core is how this silently dies on a loaded box, and PARI aborts
    the whole input file on error, which then looks like every remaining
    polynomial having no usable primes rather than like a resource failure.
    Each row is wrapped so one bad polynomial cannot take the rest with it.
    """
    lines = [f"default(parisize,{parisize});", "default(breakloop,0);"]
    for key, cf in polys:
        lines.append(f'print("P {key}");')
        lines.append(f"iferr(g=Polrev([{cf}]);"
                     'if(poldegree(g)!=24,print("SKIP degree"),'
                     # Do not compute poldisc merely to skip bad primes. For a
                     # rational defining polynomial that creates a huge
                     # primitive integer and turns a seconds-long shard into
                     # an hour-long one. Primitive normalization itself is
                     # cheap; the expensive part was poldisc. Factor the
                     # primitive integer directly and admit a prime exactly
                     # when the factorisation is squarefree and still degree
                     # 24. This is the discriminant gate by definition.
                     'h=g/content(g);if(pollead(h)<0,h=-h);lc=pollead(h);'
                     'print("S ",polsturm(h));n=0;'
                     f'forprime(p=3,{pmax},if(n>={nprimes},break);'
                     'if(lc%p==0,next);fa=factormod(h,p);ok=1;dg=0;'
                     'for(j=1,#fa[,2],if(fa[j,2]!=1,ok=0;break);'
                     'dg=dg+poldegree(fa[j,1]));if(!ok||dg!=24,next);'
                     'n=n+1;print("T ",vecsort(vector(#fa[,1],j,'
                     'poldegree(fa[j,1])))))),E,print("ERR ",E));')
    lines.append("quit;")
    # One script file per process. A fixed path lets concurrent workers on the
    # same box overwrite each other between write and read, and the symptom is
    # not an error: each worker labels whichever polynomials the last writer
    # happened to want, or reports every row as never having reached PARI.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".gp", prefix="lab24_", delete=False
    ) as fh:
        fh.write("\n".join(lines))
        script = fh.name
    try:
        proc = subprocess.run(
            ["gp", "-q", script],
            capture_output=True, text=True, timeout=None
        )
    finally:
        Path(script).unlink(missing_ok=True)
    if proc.returncode != 0:
        sys.exit("gp failed (exit %d): %s" % (
            proc.returncode, (proc.stderr or proc.stdout or "")[-1500:]))
    out, cur = {}, None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("P "):
            cur = line[2:]
            out[cur] = {"shapes": Counter(), "real_roots": None,
                        "error": None}
        elif cur is None:
            continue
        elif line.startswith("S "):
            out[cur]["real_roots"] = int(line[2:])
        elif line.startswith("T "):
            out[cur]["shapes"]["".join(c for c in line[2:]
                                       if c.isdigit() or c == ",")] += 1
        elif line.startswith("ERR ") or line.startswith("SKIP"):
            out[cur]["error"] = line
    if not out and proc.stderr:
        sys.exit("gp failed: " + proc.stderr[-1500:])
    return out


def identify(
    shapes: Counter, laws
) -> tuple[int | None, float, int | None, int, list[tuple[float, int]]]:
    scored = []
    for t, law in laws.items():
        ll = 0.0
        for shape, c in shapes.items():
            rate = law.get(shape, 0.0)
            if rate <= 0.0:
                ll = None
                break
            ll += c * math.log(rate)
        if ll is not None:
            scored.append((ll, t))
    if not scored:
        return None, 0.0, None, 0, []
    scored.sort(reverse=True)
    margin = (scored[0][0] - scored[1][0]) if len(scored) > 1 else float("inf")
    runner = scored[1][1] if len(scored) > 1 else None
    return scored[0][1], margin, runner, len(scored), scored


def tied_at_top(scored, tol: float = 1e-9) -> list[int]:
    """Every group the evidence cannot tell apart from the best one.

    A margin of exactly zero is not weak evidence, it is a pair of groups whose
    cycle-type distributions agree, so no number of primes separates them. The
    field is still a real field with a real label; what is unknown is only which
    member of the tie it carries. Naming the whole tie turns a refusal into a
    short list, and a short list is enough when only one member of it carries a
    cell that is open.
    """
    if not scored:
        return []
    top = scored[0][0]
    return [t for ll, t in scored if top - ll <= tol]


def class_margin(scored, tol: float = 1e-9) -> float:
    """How far the tied-at-top block stands above everything outside it.

    `margin` compares the best two groups, so it reads 0 whenever the top two
    are inseparable, and that says nothing about whether the block is the right
    one. A reader working at reduced depth can put a wrong inseparable pair on
    top and still report margin 0, which looks exactly like a settled tie.

    This is the quantity that means what margin is used for: the evidence
    separating the answer, tie or not, from the first group it is not tied
    with. It is what a caller must consult before deciding a shallow read is
    enough.
    """
    if not scored:
        return 0.0
    top = scored[0][0]
    inside = {t for ll, t in scored if top - ll <= tol}
    for ll, t in scored:
        if t not in inside:
            return top - ll
    return float("inf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="file of polynomials, or - for stdin")
    ap.add_argument("-o", "--out", default="-")
    ap.add_argument("--primes", type=int, default=DEFAULT_PRIMES)
    ap.add_argument(
        "--pmax", type=int, default=50_000_000,
        help="largest Frobenius prime admitted to the gate",
    )
    ap.add_argument("--min-margin", type=float, default=MIN_MARGIN)
    ap.add_argument(
        "--emit-candidates", type=int, default=0, metavar="K",
        help="on a refusal, list up to K groups tied at the top score",
    )
    ap.add_argument(
        "--emit-shapes", action="store_true",
        help="include the measured factorisation-shape histogram in each receipt",
    )
    ap.add_argument("--parisize", type=int, default=256_000_000,
                    help="PARI stack per worker; small on purpose, see measure()")
    args = ap.parse_args()

    laws = load_laws()
    polys = read_polys(args.input)
    data = measure(polys, args.primes, args.pmax, args.parisize)

    sink = sys.stdout if args.out == "-" else open(args.out, "w")
    named = thin = 0
    for key, _ in polys:
        d = data.get(key)
        if not d or not d["shapes"]:
            why = (d or {}).get("error") or (
                "polynomial never reached PARI, which aborts the whole input "
                "file on a resource failure" if d is None else "no usable primes")
            sink.write(json.dumps({"id": key, "label": None, "why": why}) + "\n")
            continue
        t, margin, runner, surv, scored = identify(d["shapes"], laws)
        confident = t is not None and margin >= args.min_margin
        named += confident
        thin += t is not None and not confident
        cm = class_margin(scored)
        receipt = {
            "id": key, "label": t if confident else None,
            "real_roots": d["real_roots"],
            "cell": ("24T%d.%d" % (t, d["real_roots"])) if confident else None,
            "margin": None if margin == float("inf") else round(margin, 2),
            "class_margin": None if cm == float("inf") else round(cm, 2),
            "runner_up": runner, "groups_surviving": surv,
            "primes": sum(d["shapes"].values()),
            "pmax": args.pmax,
        }
        if args.emit_candidates and not confident:
            receipt["tied"] = tied_at_top(scored)[:args.emit_candidates]
        if args.emit_shapes:
            receipt["factorisation_shapes"] = dict(sorted(d["shapes"].items()))
        sink.write(json.dumps(receipt) + "\n")
    if sink is not sys.stdout:
        sink.close()
    print("labelled %d of %d; %d refused for a thin margin"
          % (named, len(polys), thin), file=sys.stderr)


if __name__ == "__main__":
    main()
