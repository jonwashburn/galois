Degree 24, what it taught, and the tools that use it

This repository is the source release that sits next to
https://recognitionphysics.org/igp24/

The pages say what the degree taught. These files let you act on it
without writing to us. If you have a method and no machines, write
jon@recognitionphysics.org and we will run it. You keep the credit.

Stage 1 of the IGP24 contest is closed. Stage 2 has not started.
This is not a scorecard.

Three tools
-----------

reach/
  You give a base field's degree and how many real places it has.
  The screen returns which real-root counts that base can write.
  A refusal is a proof of no, from group theory. No field is built.
  Need: Python 3.

    python3 reach/reach.py --deg 12 --r1 12
    python3 reach/reach.py --deg 12 --r1 12 --label 10301 --r 24

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

  Start        https://recognitionphysics.org/igp24/
  What we found https://recognitionphysics.org/igp24/structure/
  Tools        https://recognitionphysics.org/igp24/tools/
  Help         https://recognitionphysics.org/igp24/help/

Recognition Physics Institute, Austin.
jon@recognitionphysics.org
