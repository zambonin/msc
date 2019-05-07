#!/usr/bin/env sage
#
# Toy example of the Oil-Vinegar signature scheme from Multivariate Public Key
# Cryptosystems (ISBN-10: 0387322299), pp. 66-69.

# parameters: number of oil and vinegar variables, and chosen finite field
o, v = 3, 3
n = o + v
k.<a> = GF(4)   # syntax enables the direct use of elements from the field

gen_names = lambda _str, qnt: [_str.format(d) for d in range(1, qnt + 1)]
# inject oil and vinegar variables
vars = gen_names('x{}', o) + gen_names('x{}v', v)

# perform multiplications by setting unknowns as field elements
A1 = PolynomialRing(k, names=vars)
A1.inject_variables()

# vector of variables
x = matrix(A1, 1, n, vars)

# coefficients of the quadratic monomials in F
Q1 = matrix(k, n, [
    0,    0,    0,    1,    a^2,  a^2,
    0,    0,    0,    1,    a,    1,
    0,    0,    0,    a^2,  a^2,  a^2,
    0,    0,    0,    0,    0,    a,    # wrong line on the book
    0,    0,    0,    0,    a^2,  1,
    0,    0,    0,    0,    0,    1,
])

Q2 = matrix(k, n, [
    0,    0,    0,    0,    a,    a,
    0,    0,    0,    1,    a^2,  a,
    0,    0,    0,    a,    1,    a^2,
    0,    0,    0,    1,    a,    1,
    0,    0,    0,    0,    0,    0,
    0,    0,    0,    0,    0,    1,
])

Q3 = matrix(k, n, [
    0,    0,    0,    a,    a,    0,
    0,    0,    0,    1,    0,    1,
    0,    0,    0,    a^2,  1,    a^2,
    0,    0,    0,    0,    a^2,  1,
    0,    0,    0,    0,    0,    1,    # missing line on the book
    0,    0,    0,    0,    0,    a,
])

# equations created by adding the variables
f1 = x * Q1 * x.T
f2 = x * Q2 * x.T
f3 = x * Q3 * x.T

# checkf1 = (
#     x1*x1v + a^2*x1*x2v + a^2*x1*x3v + x2*x1v + a*x2*x2v + x2*x3v
#     + a^2*x3*x1v + a^2*x3*x2v + a^2*x3*x3v + a*x1v*x3v
#     + a^2*x2v*x2v + x2v*x3v + x3v*x3v
# )
# checkf2 = (
#     a*x1*x2v + a*x1*x3v + x2*x1v + a^2*x2*x2v + a*x2*x3v + a*x3*x1v
#     + x3*x2v + a^2*x3*x3v + x1v*x1v + a*x1v*x2v + x1v*x3v + x3v*x3v
# )
# checkf3 = (
#     a*x1*x1v + a*x1*x2v + x2*x1v + x2*x3v + a^2*x3*x1v + x3*x2v
#     + a^2*x3*x3v + a^2*x1v*x2v + x1v*x3v + x2v*x3v + a*x3v*x3v
# )
#
# print f1 - checkf1, f2 - checkf2, f3 - checkf3

# inject variables for the trapdoor map
more_vars = gen_names('z{}', n)
A2 = PolynomialRing(k, names=more_vars)
A2.inject_variables()

z = matrix(A2, 1, n, more_vars)

# affine invertible map, or rather just an invertible square matrix
L = matrix(k, n, [
    1,    a^2,  a,    a,    0,    a^2,
    a^2,  a^2,  1,    1,    1,    a,
    1,    0,    1,    a^2,  1,    a^2,
    a,    a,    1,    a,    0,    1,
    a,    1,    a,    a^2,  0,    a^2,
    1,    1,    1,    a,    a,    0,
])

# compose L with F and add the pertinent variables
lf1 = z * L.T * Q1 * L * z.T
lf2 = z * L.T * Q2 * L * z.T
lf3 = z * L.T * Q3 * L * z.T

# checklf1 = (
#     z1*z1 + a^2*z1*z2 + a*z1*z3 + z1*z6 + a*z2*z2 + z2*z3 + a*z2*z4 + z2*z5
#     + a^2*z2*z6 + a^2*z3*z5 + z3*z6
# )
# checklf2 = (
#     z1*z1 + z1*z2 + a^2*z1*z3 + z1*z4 + a*z1*z6 + z2*z2 + a^2*z2*z4 + z2*z5
#     + a*z2*z6 + z3*z3 + a^2*z3*z4 + z3*z6 + a*z4*z4 + z5*z5 + z6*z6
# )
# checklf3 = (
#     a*z1*z1 + a*z1*z2 + a*z1*z4 + a^2*z1*z5 + z1*z6 + z2*z2 + a^2*z2*z6
#     + a^2*z3*z4 + a^2*z3*z6 + z4*z4 + z4*z6 + a*z5*z5 + a*z5*z6 + a*z6*z6
# )
#
# print lf1 - checklf1, lf2 - checklf2, lf3 - checklf3

# message and vinegar variables
M = vector(k, [a, 1, a^2])
V = vector(k, [a^2, a^2, 1])

# substitute the vinegar variables and set polynomials equal to the message
linear = (
    f1(x1, x2, x3, *V)[0, 0] - M[0],
    f2(x1, x2, x3, *V)[0, 0] - M[1],
    f3(x1, x2, x3, *V)[0, 0] - M[2]
)

# Groebner basis computation can be seen as a multivariate, non-linear
# generalization of Gaussian elimination for linear systems.
basis = ideal(linear).groebner_basis()
v_inv = vector(basis).subs({A1(v): 0 for v in vars[:o]})

# compute F^{-1}
preimage = vector(k, n, v_inv.list() + V.list())
# print preimage
# print f1(*preimage), f2(*preimage), f3(*preimage)

# apply L to the preimage and get the signature
signature = L.solve_right(preimage)
# print signature

# get message from signature
mprime = vector(A1, o, [lf1(*signature), lf2(*signature), lf3(*signature)])
assert mprime == M
