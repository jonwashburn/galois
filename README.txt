Degree 24, what it taught, and the tools that use it

This repository is the source release that sits next to
https://recognitionphysics.org/igp24/

The pages say what the degree taught. These files let you act on it
without writing to us. If you have a method and no machines, write
jon@recognitionphysics.org and we will run it. You keep the credit.

Stage 1 of the IGP24 contest is closed. Stage 2 has not started.
This is not a scorecard.

Start here: the open cells
--------------------------

worklist/
  Every cell nobody has written, with the shape of field that would
  write it. 24,210 cells on 7,433 groups. Not one of them is refused
  by group theory, so the leftover is arithmetic throughout.

    worklist/worklist.jsonl.gz   one line per open cell
    worklist/worklist.json       the same, keyed by group then count
    worklist/summary.json        the counts, and what each job means

  Each row names every base the group permits, as
  [base degree, base group, base real places]. The split:

    11,736 cells on 4,275 groups   one square root over a degree-12
                                   base. The group has a subfield of
                                   degree 12, so the kernel of the
                                   last step is elementary abelian
                                   for free. Pick a base of the named
                                   group and real-place count, then
                                   aim the radicand.

    12,470 cells on 3,155 groups   a tower of another degree. No
                                   degree-12 subfield, so no square
                                   root finishes it. Every one still
                                   permits a base of degree 2, 3, 4,
                                   6 or 8, carrying a step of degree
                                   24 over that on top. The step is
                                   not a quadratic, so its kernel is
                                   not abelian for free. That is the
                                   part nobody here has written.

         4 cells on 3 groups       no opinion. Primitive groups have
                                   no proper subfield, so the screen
                                   has nothing to say and says
                                   nothing. Ignorance, not refusal.

  A listed base is permitted by GROUP THEORY ONLY. It means the group
  does not forbid the cell. It does not say a base field of that
  group and signature exists, that you can find one, or that the
  radicand can be aimed. The refusal direction is the sound one: a
  base absent from the list cannot write the cell.

  Rebuild it against your own name list rather than trusting ours:

    python3 worklist/build_worklist.py --igp24 <dir> --site <dir>

  The two inputs ship here. admitted_pairs.csv.gz is the 165,836
  pairs of a group and a real-root count the contest admits.
  named_cells.txt.gz is the 141,626 cells held at the Stage 1 close,
  as <group>_<count> per line. Every named cell is on the admitted
  list, so the leftover is exactly the difference.

Three tools
-----------

reach/
  Both directions of the same table.

  What a base can write. You give a base field's degree and how many
  real places it has; the screen returns which real-root counts that
  base can write. A refusal is a proof of no, from group theory. No
  field is built. Need: Python 3.

    python3 reach/reach.py --deg 12 --r1 12
    python3 reach/reach.py --deg 12 --r1 12 --label 10301 --r 24

  What a target cell needs. This is the direction most people want,
  because you usually have a cell rather than a base.

    python3 reach/reach.py --label 243 --r 0

  prints every base the group permits, with the degree of the step
  that sits on top and, in the degree-12 case, how many real places
  need a negative radicand.

  The walk table ships beside the script (712,213 bytes):

    reach/walktable.json.gz
    SHA-256 ad86d39070edd3ba75d2e5326f73a2b6613ee35aecc7de1300913a962f488fab

label/
  A degree-24 polynomial in. A group name and a real-root count out,
  with a margin. Chebotarev evidence, not a proof. Accept at 5 nats
  or more. Need: Python 3 and PARI/GP 2.13 or later.

    gunzip -k label/shape_laws_24T.jsonl.gz
    export IGP24_SHAPE_LAWS=$PWD/label/shape_laws_24T.jsonl
    python3 label/label_degree24.py polys.txt --primes 1000 --min-margin 5

aim/
  One worked compile: a totally real 12T11 base, signature 24, nine
  degree-24 polynomials. Need: PARI/GP 2.13 or later.

    gp -q aim/worked-12t11.gp

The pages
---------

  Start          https://recognitionphysics.org/igp24/
  What we found  https://recognitionphysics.org/igp24/structure/
  Open cells     https://recognitionphysics.org/igp24/worklist/
  Tools          https://recognitionphysics.org/igp24/tools/
  Dead ends      https://recognitionphysics.org/igp24/dead-ends/
  Help           https://recognitionphysics.org/igp24/help/

Recognition Physics Institute, Austin.
jon@recognitionphysics.org
