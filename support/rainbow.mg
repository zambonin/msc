// Implementation of the Rainbow signature scheme from Multivariate Public Key
// Cryptosystems (ISBN-10: 0387322299), pp. 88-90. Direct adaptation of Magma
// code from the Ph.D. thesis of A. Petzoldt, but simplified to run in a single
// file without writing variables to the disk.

F<w> := GaloisField(17);
param := [20, 10];

u := #param - 1;
v := [param[1]];
for i := 1 to u do
  v[i + 1] := v[i] + param[i + 1];
end for;
n := v[u + 1];
m := n - v[1];


function affine_map(ring)
  base_ring := BaseRing(ring);
  while not IsFinite(base_ring) do
    base_ring := BaseRing(base_ring);
  end while;

  order := Rank(ring);
  mat := Random(GeneralLinearGroup(order, base_ring));

  return [ ring.i ^ mat + Random(base_ring) : i in [1..order] ];
end function;


function keygen(: uov := false)
  if uov then
    assert u eq 1;
  end if;

  PX<[x]> := PolynomialRing(F, n);
  PY<[y]> := PolynomialRing(PX, n);
  PZ<[z]> := PolynomialRing(PY, m);

  T := affine_map(PX);
  if uov then
    id := Identity(GeneralLinearGroup(m, F));
    S := [ PZ.i ^ id : i in [1..m] ];
  else
    S := affine_map(PZ);
  end if;

  Q := [ PY!Random(F) : _ in [1..m] ];
  for l := 1 to u do
    for k := v[l] - v[1] + 1 to v[l + 1] - v[1] do
     // cross-vinegar
      for i := 1 to v[l] do
        for j := 1 to v[l + 1] do
          Q[k] +:= Random(F) * PY.i * PY.j;
        end for;
      end for;

      // linear
      Q[k] +:= &+[ Random(F) * PY.i : i in [1..v[l + 1]] ];
    end for;
  end for;

  QT := [ Evaluate(Q_i, T) : Q_i in Q ];
  P := [ MonomialCoefficient(Evaluate(S_i, QT), 1) : S_i in S ];

  return <S, Q, T>, P;
end function;


function sign(sk, msg: fix := false)
  S, Q, T := Explode(sk);
  msg_space := VectorSpace(F, m);
  sig_space := VectorSpace(F, n);

  M_S := Matrix(F, JacobianMatrix(S));
  c_S := msg_space!([ MonomialCoefficient(S_i, 1) : S_i in S ]);
  _, inv_S, _ := IsConsistent(Transpose(M_S), msg_space!(msg) - c_S);

  rest_variables := [ Parent(Q[1]).i : i in [(v[1] + 1)..n] ];
  repeat
    if fix then
      preimage := [ i : i in [1..v[1]] ] cat rest_variables;
    else
      preimage := [ Random(F) : _ in [1..v[1]] ] cat rest_variables;
    end if;
    newQ := [ Evaluate(Q_i, preimage) : Q_i in Q ];

    for i := 2 to u + 1 do
      oil_space := VectorSpace(F, v[i] - v[i - 1]);
      oil_range := [(v[i - 1] + 1 - v[1])..(v[i] - v[1])];

      M_Q := Matrix(F,
        Submatrix(JacobianMatrix(newQ), oil_range, [i + v[1] : i in oil_range])
      );
      c_Q := oil_space!([ MonomialCoefficient(newQ[j], 1) : j in oil_range ]);

      solutions := oil_space!([ inv_S[k] : k in oil_range ]);
      truth, inv_Q, _ := IsConsistent(Transpose(M_Q), solutions - c_Q);
      if not truth then
        break;
      end if;

      for j := v[i - 1] + 1 to v[i] do
        preimage[j] := inv_Q[j - v[i - 1]];
      end for;
      newQ := [ Evaluate(Q_i, preimage) : Q_i in newQ ];
    end for;
  until truth;

  M_T := Matrix(F, JacobianMatrix(T));
  c_T := sig_space!([ MonomialCoefficient(T_i, 1) : T_i in T ]);
  _, signature, _ := IsConsistent(Transpose(M_T), sig_space!(preimage) - c_T);

  return signature;
end function;


function verify(pk, message, signature)
  sig := ElementToSequence(signature);
  return ElementToSequence(message) eq [ Evaluate(pk_i, sig) : pk_i in pk ];
end function;

sk, pk := keygen(: uov := true);
S, Q, T := Explode(sk);

o1 := v[2] - v[1];
iterations := 16;
assert o1 lt iterations;

// grab some signatures (in this case we're signing but they are public data)
msgs := [];
sigs := [];
for i := 1 to iterations do
  message := [ Random(F) : _ in [1..m] ];
  signature := sign(sk, message: fix := true);
  if verify(pk, message, signature) then
    Append(~msgs, message);
    Append(~sigs, signature);
  end if;
end for;

// recover matrix + vector parts of affine transformation T
sig_space := VectorSpace(F, n);
M_T := Matrix(F, JacobianMatrix(T));
c_T := sig_space!([ MonomialCoefficient(T_i, 1) : T_i in T ]);

// obtain T^(-1)
invMT := M_T^(-1);
invCT := -c_T * Transpose(invMT);

// sanity check of the inverse affine
truth, pre, _ := IsConsistent(Transpose(invMT), sig_space!(sigs[1]) - invCT);
assert truth;

// choose o1 random pairs of signatures, subtract them and check for linear
// independence to build a basis
repeat
  repeat
    rand := [ Random(1, #sigs - 1) : _ in [1..m] ];
    minus := [ sigs[i] - sigs[i + 1] : i in rand ];
  until IsIndependent(minus);

  id := ScalarMatrix(F, n, 1);
  for i -> vec in minus do
    id[i + v[1]] := vec;
  end for;
  newTmat := Transpose(id);
until IsInvertible(newTmat);

// reconstruct T as T'
TRing := Parent(T[1]);
newT := [ TRing.i ^ newTmat : i in [1..n] ];

// take the public key and compose it with T' to get an equivalent central map
// and confirm that it is Oil-Vinegar
newF := [ Evaluate(pk_i, newT) : pk_i in pk ];
zero := ZeroMatrix(F, o1, o1);
for poly in newF do
  // TODO does not work for finite fields of characteristic 2
  sbf := SymmetricBilinearForm(poly);
  assert Submatrix(sbf, v[1] + 1, v[1] + 1, o1, o1) eq zero;
end for;

// invert T' and confirm that the public key remains the same
newTmatInv := newTmat^(-1);
newTinv := [ TRing.i ^ newTmatInv : i in [1..n] ];
newPK := [ Evaluate(i, newTinv) : i in newF ];
assert newPK eq pk;

fake := sign(<sk[1], newF, newTinv>, msgs[1]: fix := true);
assert verify(pk, msgs[1], fake);
