#!/usr/bin/env python3
"""The exact refusal: what real counts a block system actually delivers.

`archscreen` bounds the real count of a degree-24 field from the archimedean
budget alone. That bound is sound and costs nothing, but it is an envelope:
measured per block system it equals the achievable set only a quarter of the
time, so three draws in four that it lets through are still impossible.

This module holds the other side. Complex conjugation is an involution in
24Tt; over a block system with b blocks of size s it fixes rho blocks, rho is
the number of real places of the degree-b subfield, and r is what it fixes
upstairs. The resulting (rho -> r) law is pure group theory, exact, and
already computed for all 25,000 labels in the block atlas. This is that law,
packed so a mill can ask it in a dict lookup.

Measured 2026-08-15 against the live board and the 35,139-row base bank:

    archimedean budget alone   refuses  59.4% of drawable pairs
    this walk                  refuses  88.6%

so of the draws the budget lets through, the walk refuses a further 71.9%.

TWO CHECKS BEFORE THIS WAS ALLOWED TO REFUSE ANYTHING

  1. Against the contest's own admissibility list, which owes the atlas
     nothing: for all 24,995 imprimitive labels the union of the walk's real
     counts equals exactly the set of signatures the contest admits for that
     label. No label where the walk misses an admissible signature, none
     where it invents one.
  2. Against work that actually happened: of the 26,856 recorded (base,
     degree-24 field) incidences in the base bank, the walk allows 26,829.
     The 27 it refuses are annotation defects, not atlas gaps, and one of
     them is the row already proved impossible on its own arithmetic
     (a totally imaginary base annotated with eight real places).

FAIL OPEN, ALWAYS. A label the atlas has not censused, a primitive label, or
a missing table means allow. Absence of a row is ignorance, not
impossibility, and a filter that refuses what it has not measured would
throw away exactly the work nobody has done yet.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import archscreen  # noqa: E402

TABLE_NAME = "walktable.json.gz"
_SEARCH = (
    os.environ.get("IGP24_WALKTABLE"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), TABLE_NAME),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                 TABLE_NAME),
)

_fwd = None          # (t, b, rho)          -> mask over r/2
_typed = None        # (t, b, baseT, rho)   -> mask over r/2
_bybase = None       # (b, baseT, rho)      -> mask over r/2, union of labels
_primitive = None
_loaded_from = None


def _mask_to_counts(mask: int) -> list:
    return [2 * i for i in range(13) if mask >> i & 1]


def load(path: str | None = None) -> bool:
    """Read the packed table. Returns False if none was found.

    Not finding one is survivable: every query then allows, and the caller
    still has the archimedean bound.
    """
    global _fwd, _typed, _bybase, _primitive, _loaded_from
    if _fwd is not None and path is None:
        return True
    for cand in ((path,) if path else _SEARCH):
        if not cand or not os.path.exists(cand):
            continue
        with gzip.open(cand, "rt") as fh:
            payload = json.load(fh)
        fwd: dict = {}
        typed: dict = {}
        bybase: dict = {}
        for t, b, baseT, rho, m in payload["rows"]:
            fwd[(t, b, rho)] = fwd.get((t, b, rho), 0) | m
            typed[(t, b, baseT, rho)] = typed.get((t, b, baseT, rho), 0) | m
            bybase[(b, baseT, rho)] = bybase.get((b, baseT, rho), 0) | m
        _fwd, _typed, _bybase = fwd, typed, bybase
        _primitive = set(payload.get("primitive", ()))
        _loaded_from = cand
        return True
    _fwd, _typed, _bybase, _primitive = {}, {}, {}, set()
    _loaded_from = None
    return False


def available() -> bool:
    load()
    return bool(_fwd)


def source() -> str | None:
    load()
    return _loaded_from


_label_cache = None


def _labels():
    global _label_cache
    if _label_cache is None:
        load()
        _label_cache = {k[0] for k in _fwd}
    return _label_cache


def known(t: int) -> bool:
    """Has the atlas censused this label with at least one block system?"""
    return t in _labels()


def reachable(t: int, base_deg: int, base_r1: int, base_type: int | None = None):
    """Real counts this block system delivers from a base of that signature.

    Returns None when the table cannot speak for this label, which the caller
    must read as "no opinion", never as "nothing".
    """
    load()
    if not _fwd or t not in _labels():
        return None
    if base_type is not None:
        m = _typed.get((t, base_deg, base_type, base_r1))
        if m is not None:
            return _mask_to_counts(m)
    m = _fwd.get((t, base_deg, base_r1))
    if m is None:
        # The label is censused and has no system of this shape and base
        # signature, so nothing is delivered. That is a refusal, not silence.
        return []
    return _mask_to_counts(m)


def allows(t: int, base_deg: int, base_r1: int, r: int,
           base_type: int | None = None) -> bool:
    """Can a base of this degree and signature put label t at real count r?

    False is a proof of no, drawn from group theory. True means the group
    permits it; the arithmetic still has to work out.
    """
    got = reachable(t, base_deg, base_r1, base_type)
    if got is None:
        return True
    return r in got


def signatures_for_base(base_deg: int, base_type: int, base_r1: int):
    """Every real count reachable from this base type, over all labels.

    The cheap prune for a mill that aims by base type rather than by label:
    a signature outside this set cannot be written from this base at all.
    """
    load()
    m = _bybase.get((base_deg, base_type, base_r1))
    if m is None:
        return None
    return _mask_to_counts(m)


def screen(t: int, base_deg: int, base_r1: int, r: int,
           base_type: int | None = None) -> bool:
    """The filter a mill should actually call: both refusals at once.

    The two are independent and both sound, and neither contains the other.
    The walk is far sharper wherever the atlas has censused the label, and it
    is silent on the five primitive labels and on anything uncensused, which
    is exactly where the archimedean budget still bites. Conjunction is the
    only form that keeps both.
    """
    return (archscreen.screen(r, base_deg, base_r1)
            and allows(t, base_deg, base_r1, r, base_type))


def cells_for_base(base_deg: int, base_r1: int, base_type: int | None = None):
    """Iterate the (label, real count) cells this base could write."""
    load()
    src = _typed if base_type is not None else _fwd
    for key, m in src.items():
        if base_type is not None:
            t, b, bt, rho = key
            if bt != base_type:
                continue
        else:
            t, b, rho = key
        if b != base_deg or rho != base_r1:
            continue
        for r in _mask_to_counts(m):
            yield t, r


if __name__ == "__main__":
    import sys
    if not load():
        print("no walk table found; searched:")
        for c in _SEARCH:
            print("   ", c)
        raise SystemExit(1)
    print("walk table: %s" % _loaded_from)
    print("labels censused: %d, primitive: %d" % (len(_labels()),
                                                  len(_primitive)))
    if len(sys.argv) == 5:
        t, d, r1, r = (int(x) for x in sys.argv[1:])
        print("label %d from a degree-%d base with %d real places reaches %s"
              % (t, d, r1, reachable(t, d, r1)))
        print("r=%d allowed: %s" % (r, allows(t, d, r1, r)))
