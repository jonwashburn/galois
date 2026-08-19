Degree-24 number fields: the published table


What this is

fields.jsonl is one JSON object per row, schema in fields.schema.json. Each
row is an irreducible degree-24 polynomial over the rationals together with
everything we can currently certify about the field it defines. A cell is a
Galois group and a real-root count taken together; the table carries more
than one row per cell where a second witness earned a stronger certification
than the first.

Nothing in a row has to be taken on trust. verify_rows.py recomputes every
claim from the coefficients alone and is described at the bottom of this file.


The four axes, and what each one costs to earn

label_axis      exact or chebotarev. A chebotarev row names the group from
                Frobenius cycle types against the class-rate table and carries
                the primes used and the margin in nats. A margin below 5 is
                not published. exact means an independent exact computation
                agreed, which is far more expensive and is reserved for
                headline rows.

reduced         polredabs, polredbest, or raw. polredabs is canonical: two
                fields agree if and only if their polredabs polynomials agree,
                so a canonical row can be matched against any other table
                without further work. polredbest is a genuine reduction but
                not canonical, so equal fields can still look different.

disc_axis       unconditional when the polynomial discriminant factored
                completely below disc_pbound, so the order is provably
                maximal and nfdisc is the field discriminant outright.
                conditional when a cofactor survived the sieve; the cofactor
                is in the row, and the discriminant is correct provided that
                cofactor is squarefree. undetermined when the factorization
                did not finish at all. An undetermined row states nothing
                about the discriminant and carries no nfdisc. It is a fact
                about our computation, not about the field.

maximal_axis    certified, bounded, or unknown, tracking disc_axis exactly:
                the question of whether the order is maximal is the question
                of whether that cofactor is trivial.

The axes are independent. A row can be canonical with an undetermined
discriminant, or have an unconditional discriminant without an exact label.
Read the one you need rather than treating the row as certified or not.


Where the undetermined rows come from

A small number of polynomials have discriminants that resist factoring. That
is a hard problem in integer factorization and not a matter of running longer
on more cores; raising the budget by an order of magnitude on 192 cores moved
some of them and left others exactly where they were. Those rows are
published rather than dropped, because several hundred cells are witnessed by
no other polynomial in the table, and a table that silently omits them
reports less than was actually established while looking cleaner for it.


What is not in here

The Galois group is the one claim the verifier cannot recheck, because
polgalois stops at degree 11. Naming 24Tn takes the published labeller and
the class-rate table, which is a separate run against the same polynomial.
The verifier says so rather than passing over it.

cells.txt on the site is the names-only contest snapshot. It is a different
object and is not this table.


Rechecking the table

  python3 verify_rows.py --fields fields.jsonl --sample 400 --workers 150

Every row is handed to PARI with only its coefficients. The script recomputes
degree and irreducibility, polsturm against the published real-root count,
polredabs against the published polynomial where the row claims canonical
form, the unfactored part of the discriminant under the published prime bound
against the published cofactor, the axis that part implies in both directions,
and nfdisc where the row states one. It also recomputes sha256 of the
coefficients and refuses any row shipped under an identifier that is not its
own, which is what catches a changed coefficient on a row that makes no
discriminant claim.

A row that outruns the budget is reported as unchecked, which is neither a
pass nor a fail.

  python3 verify_rows.py --fields fields.jsonl --sample 400 --mutate

This is the verifier's own test. It corrupts one asserted field per row and
every row must be rejected. A checker that has never rejected anything has
not been shown to reject anything, so run this before believing the first
command. Measured on this table: 400 of 400 real rows reproduce with none
unchecked, and 400 of 400 corrupted rows are rejected across all five
corruption kinds.


Other files

  fields.jsonl.gz      the whole table, one download
  by-group/            a hundred groups per file, so a lookup does not cost
                       the whole table; by-group/index.json says which file
                       answers which group
  summary.json         the counts, checkable without parsing the table
  MANIFEST.json        sha256 and byte count of each file above

DOI registration waits on a named go.
