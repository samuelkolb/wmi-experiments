import argparse
import os

import pysmt.shortcuts as smt
from pywmi import Domain
from pywmi.domain import Density
from pywmi.smt_print import pretty_print


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
        xor = smt.Xor(xor, term)

    return flip_domain(domain), bounds & xor, smt.Real(1.0)


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

    return flip_domain(domain), bounds & disjunction, smt.Real(1.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem_name", choices=["xor", "mutex"])
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
            domain, formula, weight = generate_xor(size)
        elif args.problem_name == "mutex":
            domain, formula, weight = generate_mutual_exclusive(size)
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

        Density(domain, formula, weight).export_to(output_file)


if __name__ == "__main__":
    main()
