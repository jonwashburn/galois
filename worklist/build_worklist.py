#!/usr/bin/env python3
"""Turn the leftover from a count into a worklist with an address.

The pages already say how many cells are open and that the leftover is two
piles. Neither tells a reader which cells those are, nor what any one of them
needs. Both are already computed and sitting in two files:

  valid_pairs.csv          the 165,836 (label, real-root count) pairs the
                           contest admits
  fields/cells.txt         the 141,626 cells held at the Stage 1 close
  SUBFIELD_LATTICE.jsonl   every subfield of every one of the 25,000 degree-24
                           transitive groups, from an exhaustive GAP census
  walktable.json.gz        for each label, which base degree, base group and
                           base signature delivers which real-root count

Subtracting the second from the first gives the open cells. Joining those
against the last two gives, per open cell, the shape of the field that would
write it: the degree of the base, the transitive group of the base, and how
many real places that base needs.

That join is the whole point. A reader who wants to close a cell does not need
our count of the leftover, they need the address of one cell and the field to
stand it on.

WHAT A ROW DOES AND DOES NOT CLAIM

Every base listed is permitted by group theory alone: complex conjugation is
an involution in the degree-24 group, and over a block system it fixes a
number of blocks equal to the number of real places of the subfield. That law
is exact and it is a refusal, not a construction. A listed base means the
group does not forbid the cell. Whether a base field of that shape exists, and
whether the radicand can be aimed, is arithmetic and is not settled here.

The table fails open. A label the census has not reached, and the five
primitive labels that have no proper subfield at all, get `no-opinion` rather
than a refusal. Absence of a row is ignorance.

  python3 build_worklist.py --igp24 <IGP24> --site <rs-website>/public/igp24
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

# r = 2 * (rho - w): a base with rho real places and w of them where the
# radicand is negative leaves 2(rho - w) real roots upstairs. Written out on
# the page as r = 24 - 4s - 2w with s the complex places of the base.
BLOCK_SIZE_FOR_QUADRATIC = 12


def read_admissible(path: Path) -> set[tuple[int, int]]:
    out = set()
    with path.open() as fh:
        for row in csv.DictReader(fh):
            out.add((int(row["label"].removeprefix("24T")), int(row["r"])))
    return out


def read_named(path: Path) -> set[tuple[int, int]]:
    out = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        t, r = line.split("_")
        out.add((int(t), int(r)))
    return out


def read_subfields(path: Path) -> tuple[dict[int, list[int]], set[int]]:
    """label -> the degree-12 subfield groups it has, plus the primitive set."""
    twelves: dict[int, list[int]] = {}
    primitive: set[int] = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        t = rec["t"]
        if rec.get("primitive"):
            primitive.add(t)
        twelves[t] = sorted({
            sub for deg, sub in rec.get("sub", ())
            if deg == BLOCK_SIZE_FOR_QUADRATIC
        })
    return twelves, primitive


def read_walk(path: Path) -> tuple[dict, set[int], set[int]]:
    """(label, r) -> {base degree: [[base group, base real places], ...]}."""
    payload = json.loads(gzip.open(path, "rt").read())
    reach: dict[tuple[int, int], dict[int, set[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(set))
    censused: set[int] = set()
    for t, b, base_t, rho, mask in payload["rows"]:
        censused.add(t)
        for i in range(13):
            if mask >> i & 1:
                reach[(t, 2 * i)][b].add((base_t, rho))
    return reach, censused, set(payload.get("primitive", ()))


def classify(t, r, reach, twelves, censused, primitive_walk, primitive_sub):
    """One open cell, one job, and the bases that job would stand on."""
    if t not in censused or t in primitive_walk or t in primitive_sub:
        return "no-opinion", {}
    towers = reach.get((t, r), {})
    if not towers:
        # The label is censused and no block system of any shape delivers this
        # real-root count. Group theory refuses the whole tower route here.
        return "construction", {}
    if BLOCK_SIZE_FOR_QUADRATIC in towers:
        return "quadratic", towers
    return "other-tower", towers


def build(igp24: Path, site: Path, out: Path) -> dict:
    admissible = read_admissible(igp24 / "valid_pairs.csv")
    named = read_named(site / "fields/cells.txt")
    stray = named - admissible
    twelves, primitive_sub = read_subfields(
        igp24 / "ops/address_map/SUBFIELD_LATTICE.jsonl")
    reach, censused, primitive_walk = read_walk(
        site / "tools/reach/walktable.json.gz")

    open_cells = sorted(admissible - named)
    jobs = Counter()
    labels_by_job = defaultdict(set)
    base_hist = Counter()
    other_degrees = Counter()
    # The browser payload: every open cell keyed by label then real-root count,
    # with every base the group permits as [base degree, base group, base real
    # places]. Under a megabyte, so one fetch answers every question the page
    # asks and the reader is never waiting on us.
    browser: dict[str, dict[str, list]] = {}
    no_opinion: list[list[int]] = []
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt") as fh:
        for t, r in open_cells:
            job, towers = classify(t, r, reach, twelves, censused,
                                   primitive_walk, primitive_sub)
            jobs[job] += 1
            labels_by_job[job].add(t)
            row = {"t": t, "r": r, "job": job}
            if job == "quadratic":
                bases = sorted(towers[BLOCK_SIZE_FOR_QUADRATIC])
                row["base_degree"] = BLOCK_SIZE_FOR_QUADRATIC
                row["bases"] = [[bt, rho] for bt, rho in bases]
                row["w"] = sorted({rho - r // 2 for _, rho in bases
                                   if rho - r // 2 >= 0})
                other = sorted(b for b in towers
                               if b != BLOCK_SIZE_FOR_QUADRATIC)
                if other:
                    row["other_base_degrees"] = other
                base_hist[len(bases)] += 1
            elif job == "other-tower":
                row["base_degrees"] = sorted(towers)
                row["bases_by_degree"] = {
                    str(b): [[bt, rho] for bt, rho in sorted(v)]
                    for b, v in sorted(towers.items())
                }
                for b in towers:
                    other_degrees[b] += 1
            elif job == "construction":
                row["has_degree_12_subfield"] = bool(twelves.get(t))
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")

            if job == "no-opinion":
                no_opinion.append([t, r])
            else:
                browser.setdefault(str(t), {})[str(r)] = [
                    [b, bt, rho] for b, v in sorted(towers.items())
                    for bt, rho in sorted(v)
                ]

    payload = {
        "what": "Every open degree-24 cell, with every base the group permits.",
        "row": "label -> real-root count -> "
               "[[base degree, base group, base real places], ...]",
        "claim": "A listed base is permitted by group theory alone. It means "
                 "the group does not forbid the cell. Whether a base field of "
                 "that shape exists, and whether the radicand can be aimed, "
                 "is arithmetic and is not settled here.",
        "fails_open": True,
        "no_opinion": no_opinion,
        "cells": browser,
    }
    (out.parent / "worklist.json").write_text(
        json.dumps(payload, separators=(",", ":")) + "\n")

    summary = {
        "what": "Every open degree-24 cell, with the shape of field that "
                "would write it. A listed base is permitted by group theory; "
                "the arithmetic is not settled here.",
        "admissible_pairs": len(admissible),
        "named_cells": len(named),
        "named_not_admissible": len(stray),
        "open_cells": len(open_cells),
        "jobs": {
            "quadratic": jobs["quadratic"],
            "other-tower": jobs["other-tower"],
            "construction": jobs["construction"],
            "no-opinion": jobs["no-opinion"],
        },
        "labels_with_an_open_cell": len(browser) + len({t for t, _ in no_opinion}),
        "labels_per_job": {k: len(v) for k, v in sorted(labels_by_job.items())},
        "quadratic_bases_per_cell": {
            "min": min(base_hist) if base_hist else None,
            "max": max(base_hist) if base_hist else None,
            "median": _median(base_hist),
        },
        "other_tower_cells_per_base_degree": dict(sorted(other_degrees.items())),
        "job_meanings": {
            "quadratic": "A degree-12 base of a stated signature and group "
                         "puts this cell in reach of one square root. Pile "
                         "one: a computer.",
            "other-tower": "No degree-12 base reaches this real-root count, "
                           "but a base of another degree does. Pile one in "
                           "spirit, a different tower in practice.",
            "construction": "No block system of any shape delivers this "
                            "real-root count. Pile two: a different "
                            "construction, not a wider walk.",
            "no-opinion": "Primitive or not censused. The screen fails open, "
                          "so this is ignorance and not a refusal.",
        },
        "fails_open": True,
    }
    return summary


def _median(hist: Counter) -> int | None:
    if not hist:
        return None
    flat = sorted(hist.elements())
    return flat[len(flat) // 2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--igp24", type=Path, required=True)
    ap.add_argument("--site", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    out = args.out or (args.site / "worklist/worklist.jsonl.gz")
    summary = build(args.igp24, args.site, out)
    (out.parent / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
