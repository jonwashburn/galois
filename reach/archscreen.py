#!/usr/bin/env python3
"""Archimedean budget screen: refuse a (base, demanded real count) draw
before a field is built.

Law S-1600. Let K have degree 24 and r real places, and write

    D = (24 - r) / 2

for its number of complex places. Suppose K is imprimitive with blocks of
size p over a subfield F of degree d = 24/p. Let F have r1 real places and
c = (d - r1)/2 complex places. Every place of F carries p degrees of K, so:

  * a complex place of F lies under p complex places of K,
  * a real place v of F lies under p - 2*k_v real and k_v complex places,
    where 0 <= k_v <= floor(p/2).

Summing,

    D = p*c + sum over real v of k_v,     0 <= k_v <= floor(p/2)

and therefore

    p*c  <=  D  <=  p*c + r1*floor(p/2).                        (*)

Both sides of (*) are necessary conditions on the pair (F, r), so a draw
outside the interval cannot land whatever else is true, and refusing it is
sound. The left inequality caps how imaginary the base may be; the right
one is the floor, and it is the half nobody was using: real places of the
base cannot be spent away through an odd fibre, so an odd block size forces
r >= r1.

DIRECTIONS THIS MODULE IS ALLOWED TO BE USED IN
  REJECT  is sound. Both bounds are necessary, so a refused pair is
          genuinely unreachable.
  ACCEPT  proves nothing. The interval is an upper envelope on what the
          fibre can contribute, not the achievable set; the block kernel
          can narrow it to a single point. Never report an accepted pair
          as reachable.
  INVERT  is refuted. Reading an observed column back into a bound on the
          tower is N-route-igp24-column-step-does-not-bound-the-base-degree
          -20260815. Do not infer block size or base degree from a column.

Pure integer arithmetic. No pari, no data files, no imports. Mills import
this rather than copying it, so the screen has one definition.
"""
from __future__ import annotations

DEGREE = 24

# Base degree -> block size p = 24 / d, for the divisors a base can have.
BLOCK_SIZE = {d: DEGREE // d for d in (2, 3, 4, 6, 8, 12, 24)}

ACCEPT = "accept"
CAP = "cap"          # D < p*c: base is too imaginary for the demanded r
FLOOR = "floor"      # D > p*c + r1*floor(p/2): base is too real
BAD_BASE = "bad_base"
BAD_DEMAND = "bad_demand"


class Verdict:
    """Outcome of one screen call.

    Truthy exactly when the pair survives, so `if screen(...)` reads right.
    """

    __slots__ = ("ok", "reason", "lo", "hi", "shortfall", "block_size")

    def __init__(self, ok, reason, lo=None, hi=None, shortfall=None,
                 block_size=None):
        self.ok = ok
        self.reason = reason
        self.lo = lo
        self.hi = hi
        self.shortfall = shortfall
        self.block_size = block_size

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        return ("Verdict(%s, %s, window=[%s,%s], D=%s, p=%s)"
                % (self.ok, self.reason, self.lo, self.hi, self.shortfall,
                   self.block_size))


def window(base_deg: int, base_r1: int):
    """The interval of complex-place counts D that this base can produce.

    Returns (lo, hi, block_size), or None if the base is not usable.
    """
    p = BLOCK_SIZE.get(base_deg)
    if p is None:
        return None
    if base_r1 < 0 or base_r1 > base_deg or (base_deg - base_r1) % 2:
        return None
    c = (base_deg - base_r1) // 2
    lo = p * c
    hi = p * c + base_r1 * (p // 2)
    return lo, hi, p


def screen(demanded_r: int, base_deg: int, base_r1: int) -> Verdict:
    """Can a degree-24 field with `demanded_r` real places sit over this base?

    Answers only the archimedean question. A False is a proof of no; a True
    is the absence of one reason to say no.
    """
    if demanded_r < 0 or demanded_r > DEGREE or demanded_r % 2:
        return Verdict(False, BAD_DEMAND)
    w = window(base_deg, base_r1)
    if w is None:
        return Verdict(False, BAD_BASE)
    lo, hi, p = w
    d = (DEGREE - demanded_r) // 2
    if d < lo:
        return Verdict(False, CAP, lo, hi, d, p)
    if d > hi:
        return Verdict(False, FLOOR, lo, hi, d, p)
    return Verdict(True, ACCEPT, lo, hi, d, p)


def reachable_counts(base_deg: int, base_r1: int) -> list:
    """Every demanded real count this base is not refused for, descending.

    This is the form a mill wants: hand it a base, get the rungs worth
    aiming at.
    """
    w = window(base_deg, base_r1)
    if w is None:
        return []
    lo, hi, _ = w
    out = []
    for d in range(lo, hi + 1):
        r = DEGREE - 2 * d
        if 0 <= r <= DEGREE:
            out.append(r)
    return sorted(out, reverse=True)


def admissible(demanded_r: int, bases) -> list:
    """Filter an iterable of basebank rows down to those not refused.

    Each row needs `deg` and `r1`; everything else is carried through.
    """
    keep = []
    for b in bases:
        if screen(demanded_r, int(b["deg"]), int(b["r1"])):
            keep.append(b)
    return keep


# The named corollaries, kept as assertions rather than prose so that a
# change to the window silently breaking one of them fails here first.
def _self_consistency() -> None:
    # An imaginary quadratic subfield forces r = 0.
    assert reachable_counts(2, 0) == [0]
    # r = 24 forces every proper subfield to be totally real.
    for d in (2, 3, 4, 6, 8, 12):
        for r1 in range(0, d + 1):
            if (d - r1) % 2:
                continue
            if screen(24, d, r1):
                assert r1 == d, (d, r1)
    # On eight blocks of three (base degree 8, p = 3), r is between r1 and
    # 3*r1: odd fibre cannot spend a real place.
    for r1 in (0, 2, 4, 6, 8):
        got = reachable_counts(8, r1)
        assert got == [] or (min(got) >= r1 and max(got) <= 3 * r1), (r1, got)
    # A cubic subfield carrying a complex place holds r to 8 or lower.
    assert max(reachable_counts(3, 1)) <= 8
    # Degree-24 "base" is the field itself: r must equal r1.
    for r1 in range(0, 25, 2):
        assert reachable_counts(24, r1) == [r1]


_self_consistency()


if __name__ == "__main__":
    print("archscreen: self-consistency holds")
    for d in (2, 3, 4, 6, 8, 12):
        for r1 in range(d + 1):
            if (d - r1) % 2:
                continue
            print("  base deg=%2d r1=%2d  p=%2d  reachable r: %s"
                  % (d, r1, BLOCK_SIZE[d],
                     reachable_counts(d, r1) or "none"))
