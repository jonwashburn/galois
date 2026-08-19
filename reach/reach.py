#!/usr/bin/env python3
"""Ask what a base can write, or what a target cell needs, before any field.

Two directions, and most people want the second one.

  python3 reach.py --deg 12 --r1 12                    what this base writes
  python3 reach.py --deg 12 --r1 12 --label 10301 --r 24  is this pair allowed
  python3 reach.py --label 10879 --r 8                 what this cell needs

The third form is the inverse. Give it a cell nobody has and it lists every
base the group permits: the degree of the base, its transitive group, and how
many real places it needs. That is the question a person with a target asks;
the first form only helps someone who already owns a base.

A refusal is a proof of no, from group theory. An allow means the group
permits it; the arithmetic still has to work out. Uncensused and primitive
labels fail open: the tool reports no opinion rather than a refusal.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archscreen  # noqa: E402
import walkscreen  # noqa: E402


def inverse(label: int, r: int) -> int:
    """What a target cell needs: every base the group permits."""
    bases = walkscreen.bases_for_cell(label, r)
    if bases is None:
        print("no opinion on 24T%d (uncensused or primitive), so nothing is "
              "refused here" % label)
        return 0
    if not bases:
        print("24T%d at r=%d: no block system of any shape delivers this "
              "real-root count" % (label, r))
        return 0
    print("24T%d at r=%d needs one of these bases:" % (label, r))
    print("%-12s  %-12s  %-13s  %-8s  %s"
          % ("base degree", "base group", "real places", "complex", "step on top"))
    for deg, base_t, rho in bases:
        print("%-12d  %-12s  %-13s  %-8d  degree %d"
              % (deg, "%dT%d" % (deg, base_t), "%d of %d" % (rho, deg),
                 (deg - rho) // 2, 24 // deg))
    if any(deg == 12 for deg, _, _ in bases):
        w = {rho - r // 2 for deg, _, rho in bases if deg == 12}
        print("\nA degree-12 base finishes this with one square root. "
              "r = 24 - 4s - 2w, so the radicand must be negative at "
              "%s of the base's real places."
              % " or ".join(str(x) for x in sorted(w) if x >= 0))
    else:
        print("\nNo degree-12 base reaches this cell, so a square root will "
              "not finish it. The step on top is not a quadratic and its "
              "kernel is not abelian for free.")
    print("\nPermitted by group theory only. Whether such a base exists, and "
          "whether the radicand can be aimed, is arithmetic.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--deg", type=int, help="degree of the base")
    ap.add_argument("--r1", type=int, help="real places of the base")
    ap.add_argument("--label", type=int, help="24T number, 1 to 25000")
    ap.add_argument("--r", type=int, help="real-root count aimed at upstairs")
    ap.add_argument("--type", type=int, dest="base_type", help="optional base type")
    args = ap.parse_args()

    if args.deg is None and (args.label is None or args.r is None):
        ap.error("give --deg and --r1 for what a base writes, "
                 "or --label and --r for what a cell needs")

    if not walkscreen.load(os.path.join(HERE, "walktable.json.gz")):
        print("no walk table next to this file", file=sys.stderr)
        return 2

    if args.deg is None:
        return inverse(args.label, args.r)
    if args.r1 is None:
        ap.error("--deg needs --r1, the number of real places of the base")

    arch = archscreen.reachable_counts(args.deg, args.r1)
    print("archimedean envelope: %s" % (arch or "none"))

    if args.label is None:
        got = walkscreen.signatures_for_base(args.deg, args.base_type or 0, args.r1)
        if args.base_type is None:
            # union over types: walk the by-base table via reachable on a dummy
            # is wrong; print the published compact table instead
            compact = os.path.join(HERE, "reach_by_base.json")
            rows = json.loads(open(compact).read())["by_base"]
            row = next((x for x in rows if x["deg"] == args.deg and x["r1"] == args.r1), None)
            if row is None:
                print("walk: no censused label delivers anything from this base")
            else:
                print("walk, union over labels: %s" % row["reachable_r"])
                print("labels per r: %s" % row["labels_per_r"])
        else:
            print("walk for that base type: %s" % (got if got is not None else "no opinion"))
        return 0

    reached = walkscreen.reachable(args.label, args.deg, args.r1, args.base_type)
    if reached is None:
        print("walk: no opinion on 24T%d (uncensused or primitive)" % args.label)
        return 0
    print("walk for 24T%d: %s" % (args.label, reached if reached else "nothing"))
    if args.r is not None:
        ok = walkscreen.screen(args.label, args.deg, args.r1, args.r, args.base_type)
        print("r=%d allowed: %s" % (args.r, "yes" if ok else "no"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
