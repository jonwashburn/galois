\\ Check one published degree-24 row against the polynomial itself.
\\ PARI 2.13 or later. Every claim below is rechecked from the coefficients;
\\ nothing is taken from the row except what it asserts.
\\
\\ Usage, from verify_rows.py, which fills these in per row:
\\   gp -q -D parisize=1500000000 row.gp
\\
\\ What is NOT checked here: the Galois group. polgalois stops at degree 11,
\\ so naming 24Tn needs the published labeller and the class-rate table, and
\\ that is a separate run. Everything else a row claims is checked here.

{
  g = Polrev(eval(Str("[" COEFFS "]")));
  if (poldegree(g) != 24, print("FAIL degree ", poldegree(g)); quit(1));
  h = g / content(g);
  if (pollead(h) < 0, h = -h);
  if (!polisirreducible(h), print("FAIL reducible"); quit(1));

  r = polsturm(h);
  if (r != WANT_R, print("FAIL signature ", r, " claimed ", WANT_R); quit(1));

  \\ polredabs is canonical, so a row claiming it must already be its own
  \\ canonical form. This is the check that makes matching coefficients mean
  \\ the same field.
  if (WANT_REDUCED == "polredabs",
    R = polredabs(h);
    if (R != h, print("FAIL not polredabs-canonical"); quit(1));
  );

  \\ An undetermined row claims nothing about the discriminant, so there is
  \\ nothing here to reproduce. It must also claim nothing about maximality,
  \\ and it must not carry an nfdisc it says it does not have.
  if (WANT_DISC_AXIS == "undetermined",
    if (WANT_NFDISC != "",
      print("FAIL undetermined row carries an nfdisc"); quit(1));
    print("PASS irreducible degree 24, polsturm ", r,
          ", ", WANT_REDUCED, ", disc undetermined");
    quit(0);
  );

  d = poldisc(h);
  F = factor(d, PBOUND);
  co = 1;
  for (i = 1, matsize(F)[1], if (F[i,1] > PBOUND, co = co * F[i,1]^F[i,2]));
  if (Str(co) != WANT_COFACTOR,
    print("FAIL cofactor ", co, " claimed ", WANT_COFACTOR); quit(1));

  \\ The discriminant axis is exactly the question of whether that cofactor
  \\ is trivial: with no unfactored part left, the order is provably maximal.
  uncond = (co == 1 || co == -1);
  if (uncond && WANT_DISC_AXIS != "unconditional",
    print("FAIL axis understated"); quit(1));
  if (!uncond && WANT_DISC_AXIS == "unconditional",
    print("FAIL axis overstated: cofactor ", co); quit(1));

  if (WANT_NFDISC != "",
    D = nfdisc(h);
    if (Str(D) != WANT_NFDISC,
      print("FAIL nfdisc ", D, " claimed ", WANT_NFDISC); quit(1));
  );

  print("PASS irreducible degree 24, polsturm ", r,
        ", ", WANT_REDUCED, ", disc ", WANT_DISC_AXIS);
  quit(0);
}
