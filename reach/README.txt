Reach screen for degree 24

You give a base field's degree and how many real places it has.
The tool returns which real-root counts upstairs that base can
possibly write, and, if you name a group, whether that pair is
allowed.

A refusal is a proof of no, from group theory. An allow means
the group permits it; the arithmetic still has to work out.

Need: Python 3. No PARI, no GAP, no network.

  python3 reach.py --deg 12 --r1 12
  python3 reach.py --deg 12 --r1 12 --label 10301 --r 24

The walk table ships beside this file:

  walktable.json.gz

SHA-256

  ad86d39070edd3ba75d2e5326f73a2b6613ee35aecc7de1300913a962f488fab

The table fails open. A primitive or uncensused label returns
no opinion, never a refusal. The five primitive labels are
24T7817, 24T10255, 24T24680, 24T24999, 24T25000.

Measured against the contest's own admissibility list, which
owes the table nothing: on all 24,995 imprimitive labels the
union of its real counts equals exactly the signatures the
contest admits. No label where it misses an admissible
signature, none where it invents one.

Of 26,856 recorded base-and-field incidences it allows 26,829.
The 27 refusals are annotation defects.

It refuses 88.6 percent of drawable pairs. The archimedean
bound alone refuses 59.4 percent. Of the draws that bound
lets through, the walk refuses a further 71.9 percent.

The decoy that simply allows every even count refuses on
11,636 of 11,647 labels where the walk refuses on zero.

Same files: https://github.com/jonwashburn/galois
