The open cells of degree 24, with the field each one needs

24,210 cells nobody has written, on 7,433 groups. Not one of them is
refused by group theory. The leftover is an arithmetic problem
throughout, and what sorts it is which tower a cell takes.

Where the list comes from
-------------------------

The contest admits 165,836 pairs of a group and a real-root count.
141,626 of them were named by the close of Stage 1. Every named cell
is on the admitted list, so the leftover is exactly the difference.

Those two inputs ship here:

  admitted_pairs.csv.gz   165,836 rows, "24T<n>,<r>"
  named_cells.txt.gz      141,626 lines, "<n>_<r>"

The address of each open cell comes from two exhaustive computations:

  the subfield lattice of all 25,000 transitive groups of degree 24,
  from a GAP block-system census

  the involution walk, packed as walktable.json.gz beside the reach
  screen: for each group, which base degree, base group and base
  signature delivers which real-root count

Rebuild it yourself, against your own name list if you have one:

  python3 build_worklist.py --igp24 <IGP24 dir> --site <site dir>

The files
---------

worklist.jsonl.gz
  One line per open cell. Fields: t (the 24T number), r (the
  real-root count), job, and the bases.

    {"t":243,"r":0,"job":"quadratic","base_degree":12,
     "bases":[[41,12]],"w":[12],"other_base_degrees":[2,4,6,8]}

  bases are [base group, base real places] at base_degree.
  w is how many of the base's real places need a negative radicand.

    {"t":565,"r":24,"job":"other-tower","base_degrees":[2,4,8],
     "bases_by_degree":{"2":[[1,2]],"4":[[2,4]],"8":[[5,8]]}}

worklist.json
  The same cells keyed by group then real-root count, with every base
  flattened to [base degree, base group, base real places]. One fetch,
  under a megabyte, for a browser or a one-line lookup.

summary.json
  The counts, and the definition of each job.

The three jobs
--------------

quadratic       11,736 cells on 4,275 groups. The group has a subfield
                of degree 12, so the last step is a square root and
                its kernel is elementary abelian automatically. Get a
                base of the named group with the named number of real
                places, adjoin a square root, and aim the radicand
                negative at w of those places.

                r = 24 - 4s - 2w, where s counts the complex places of
                the base and w the real places where the radicand is
                negative. Equivalently r = 2(rho - w) for a base with
                rho real places, so w = rho - r/2.

other-tower     12,470 cells on 3,155 groups. No degree-12 subfield,
                so no square root reaches these. Every one permits a
                base of degree 2, 3, 4, 6 or 8, carrying a step of
                degree 24 over that base degree. Cells reachable from
                a degree-2 base number 9,822, from degree 4 7,469,
                from degree 8 7,325, from degree 6 4,331, from degree
                3 2,746; a cell often appears in more than one.

                The step is not a quadratic, so its kernel is not
                abelian for free. That is the part nobody here has
                written, and it is where a new construction pays.

no-opinion      4 cells on 3 groups. These sit on primitive groups,
                which have no proper subfield at all, so the screen
                has nothing to say. That is ignorance, not a refusal.

What a listed base claims
-------------------------

Permitted by group theory, and nothing more.

Complex conjugation is an involution in the degree-24 group. Over a
block system it fixes as many blocks as the subfield has real places,
which fixes what it can fix upstairs. That law is exact and it is a
refusal: a base absent from a cell's list cannot write that cell,
whatever the arithmetic does.

The allow direction is weaker. A base in the list means the group does
not forbid the cell. It does not say a base field of that group and
signature exists, that you can find one, or that the radicand can be
aimed. That is arithmetic and this list does not settle it.

The screen fails open. A group it has not censused, and the five
primitive groups 24T7817, 24T10255, 24T24680, 24T24999, 24T25000, get
no opinion rather than a refusal. A filter that refused what it had
not measured would throw away exactly the work nobody has done yet.

Cells are open as of the Stage 1 close, 15 August 2026. Stage 2 has
not started. This is not the official organizer score, and no group
name in the published field table is a certified Galois-group
computation.

Same files: https://github.com/jonwashburn/galois
Pages: https://recognitionphysics.org/igp24/worklist/
