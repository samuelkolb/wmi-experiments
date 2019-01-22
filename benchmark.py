import pysmt.shortcuts as smt
from pywmi import Domain
from pywmi.smt_print import pretty_print

"""
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

        var disjunction = termList.fold(build.`val`(false)) { cumulative, new ->
            cumulative.or(new)
        }

        for(i in 0 until terms) {
            for(j in i + 1 until terms) {
                disjunction = disjunction.and(termList.get(i).not().or(termList.get(j).not()))
            }
        }

        return bounds.and(disjunction);

"""


def generate_mutual_exclusive(n):
    domain = Domain.make([], ["x"] + ["x{}".format(i) for i in range(n)], [(0, 1) for _ in range(n + 1)])

    base_lower_bound = 0.13
    base_upper_bound = 0.89
    step = 0.01
    x = domain.get_symbol("x")
    variables = domain.get_symbols(domain.real_vars)[1:]

    bounds = (x >= base_lower_bound) & (x <= base_upper_bound)
    for i in range(n):
        bounds &= variables[i] >= base_lower_bound + (i + 1) * step
        bounds &= variables[i] <= base_upper_bound - (i + 1) * step

    terms = [x <= v for v in variables]
    disjunction = smt.Or(*terms)
    for i in range(n):
        for j in range(i + 1, n):
            disjunction &= ~terms[i] | ~terms[j]

    return domain, bounds & disjunction


def main():
    domain, formula = generate_mutual_exclusive(5)
    print(domain.real_vars)
    print(pretty_print(formula))


if __name__ == "__main__":
    main()
