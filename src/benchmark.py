import argparse
import os

import pysmt.shortcuts as smt

from pywmi import Domain
from pywmi.domain import Density


def make_domain(n):
    return Domain.make([], ["x"] + ["x{}".format(i) for i in range(n)], [(0, 1) for _ in range(n + 1)])


def flip_domain(domain: Domain):
    return Domain(list(reversed(domain.variables)), domain.var_types, domain.var_domains)


def make_distinct_bounds(domain):
    base_lower_bound = 0.13
    base_upper_bound = 0.89
    step = 0.01
    variables = domain.get_symbols(domain.real_vars)

    bounds = smt.TRUE()
    for i in range(len(variables)):
        bounds &= variables[i] >= base_lower_bound + i * step
        bounds &= variables[i] <= base_upper_bound - i * step

    return bounds


"""
    fun generateXor(terms: Int) : BoolXADD {
        val baseLb = 0.13
        val baseUb = 0.89
        val step = 0.01

        var bounds = build.test("x >= $baseLb").and(build.test("x <= $baseUb"))
        (0 until terms).forEach {
            val lb = build.test("c$it >= " + (baseLb + it * step))
            val ub = build.test("c$it <= " + (baseUb - it * step))
            bounds = bounds.and(lb.and(ub))
        }

        val termList = ArrayList<BoolXADD>()
        (0 until terms).forEach { termList.add(build.test("x <= c$it")) }

        val xor = termList.fold(build.`val`(false)) { cumulative, new ->
            cumulative.xor(new)
        }

        return bounds.and(xor)
    }

"""


def generate_xor(n):
    domain = make_domain(n)
    symbols = domain.get_symbols(domain.real_vars)
    x, symbols = symbols[0], symbols[1:]
    bounds = make_distinct_bounds(domain)
    terms = [x <= v for v in symbols]
    xor = smt.FALSE()
    for term in terms:
        xor = (xor | term) & ~(xor & term)

    return Density(flip_domain(domain), bounds & xor, smt.Real(1.0))


def generate_mutual_exclusive(n):
    domain = make_domain(n)

    symbols = domain.get_symbols(domain.real_vars)
    x, symbols = symbols[0], symbols[1:]

    bounds = make_distinct_bounds(domain)

    terms = [x <= v for v in symbols]
    disjunction = smt.Or(*terms)
    for i in range(n):
        for j in range(i + 1, n):
            disjunction &= ~terms[i] | ~terms[j]

    return Density(flip_domain(domain), bounds & disjunction, smt.Real(1.0))


def generate_click_graph(n):
    """
    Real: sa (=similarityAll), b_ij (=b(i, j)), i=0, ..., n
    Bool: s_i (=sim(i)), cl_ij (=cl(i, j)), c_ij (=clicks(i, j)), i=0, ..., n
    """
    domain = Domain.make(
        # Boolean
        ["s_{}".format(i) for i in range(n)]
        + ["cl_{}{}".format(i, j) for i in range(n) for j in (0, 1)]
        + ["c_{}{}".format(i, j) for i in range(n) for j in (0, 1)]
        + ["aux_{}{}".format(i, j) for i in range(n) for j in (0, 1)],
        # Real
        ["sa"]
        + ["b_{}{}".format(i, j) for i in range(n) for j in (0, 1)],
        real_bounds=(0, 1)
    )
    s = [domain.get_symbol("s_{}".format(i)) for i in range(n)]
    cl = [[domain.get_symbol("cl_{}{}".format(i, j)) for j in (0, 1)] for i in range(n)]
    c = [[domain.get_symbol("c_{}{}".format(i, j)) for j in (0, 1)] for i in range(n)]
    aux = [[domain.get_symbol("aux_{}{}".format(i, j)) for j in (0, 1)] for i in range(n)]
    sa = domain.get_symbol("sa")
    b = [[domain.get_symbol("b_{}{}".format(i, j)) for j in (0, 1)] for i in range(n)]

    support = smt.And([
        smt.Iff(cl[i][0], c[i][0] & aux[i][0])
        & smt.Iff(cl[i][1], (c[i][1] & s[i] & aux[i][0]) | (c[i][1] & ~s[i] & aux[i][1]))
        for i in range(n)])

    one = smt.Real(1)
    zero = smt.Real(0)
    t = lambda c: smt.Ite(c, one, zero)
    w_s = [smt.Ite(s_i, t(sa >= 0) * t(sa <= 1), one) for s_i in s]
    w_aux = [smt.Ite(aux[i][j], t(b[i][j] >= 0) * t(b[i][j] <= 1), one) for i in range(n) for j in (0, 1)]

    weight = smt.Times(*(w_s + w_aux))
    return Density(domain, support, weight)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem_name", choices=["xor", "mutex", "click"])
    parser.add_argument("-n", "--size", type=str)
    parser.add_argument("-w", "--output_file", default=None)
    args = parser.parse_args()

    if ":" in args.size:
        first, last = args.size.split(":", 1)
        sizes = range(int(first), int(last) + 1)
    else:
        sizes = [int(args.size)]

    for size in sizes:
        if args.problem_name == "xor":
            density = generate_xor(size)
        elif args.problem_name == "mutex":
            density = generate_mutual_exclusive(size)
        elif args.problem_name == "click":
            density = generate_click_graph(size)
        else:
            raise ValueError("No problem with name {}".format(args.problem_name))

        default_name = "generated_{}_{}.json".format(args.problem_name, size)
        if args.output_file and os.path.exists(args.output_file):
            if os.path.isfile(args.output_file):
                output_file = args.output_file
            else:
                output_file = os.path.join(args.output_file, default_name)
        else:
            output_file = default_name

        density.to_file(output_file)


if __name__ == "__main__":
    main()
