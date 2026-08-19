Degree-24 Galois labeller

label_degree24.py names the transitive group of a degree-24 polynomial
from its Frobenius cycle types, scored against a class-rate table of
all 25,000 groups. The signature is a real-root count, taken directly.

This is Chebotarev evidence with a margin, not a proof. Magma's
GaloisGroup and Oscar's Fieker-Kluners route return certificates.
This tool returns a name and a margin, on free software, in seconds.

Need: PARI/GP 2.13 or later, Python 3, and the class-rate table.

  export IGP24_SHAPE_LAWS=/path/to/shape_laws_24T.jsonl
  python3 label_degree24.py polys.txt --primes 1000 --min-margin 5

Each input line is integer coefficients, constant term first, comma
or space separated, or a JSON object with polynomial_coefficients.

Accept at 5 nats or more. Refuse below that rather than guess. Two
groups with the same cycle-type law are a tie at any prime count;
the honest output is that short list.

The table ships beside this file, gzipped to 2,849,148 bytes:

  curl -O https://recognitionphysics.org/igp24/labeller/shape_laws_24T.jsonl.gz
  gunzip shape_laws_24T.jsonl
  export IGP24_SHAPE_LAWS=$PWD/shape_laws_24T.jsonl

SHA-256 of the download, which is reproducible because it is written
with no timestamp and no embedded filename:

  ff40f2d32e81315879f52db6100c2111884b55d5b009a5a048b7eb9649f41510

and of the 41,460,118 bytes it expands to:

  b201ae4963ada8eb3496c6f1a866348d0f9180018ae29ef9fbdc77aca614086b

Calibration, already measured:

  100 of 100 organizer-labelled fields correct, winner ahead by
  at least 19 nats at 1,000 primes.
  77 of 77 planted-wrong-group inputs returned the planted group.
  Separates all 87 pairs that share a base group but not a label.
  At 300 primes every row was still correct; one margin fell to 0.76.

The nine polynomials of the published 12T11 file labelled in 1.30 s,
thinnest margin 229.9 nats.
