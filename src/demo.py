import traceback

import pywmi
import pysmt.shortcuts as smt
from pywmi import XsddEngine


def get_problem():
    domain = pywmi.Domain.make([], ["x", "y"], [(-1.0, 1.0), (-1.0, 1.0)])
    x, y = domain.get_symbols(["x", "y"])
    formula = (x >= 0.0) & (x <= y) & (y <= 1.0)
    return domain, formula, smt.Real(1.0)


def rejection():
    domain, formula, weight = get_problem()
    return pywmi.RejectionEngine(domain, formula, weight, 100000).compute_probability(domain.get_symbol("x") <= 0.5)


def xadd():
    domain, formula, weight = get_problem()
    return pywmi.XaddEngine(domain, formula, weight).compute_probability(domain.get_symbol("x") <= 0.5)


def xsdd():
    domain, formula, weight = get_problem()
    return XsddEngine(domain, formula, weight, repeated=True).compute_probabilities([domain.get_symbol("x") <= 0.5, domain.get_symbol("x") <= 1.0])


def main():
    methods = [("rejection", rejection), ("XADD", xadd), ("XSDD", xsdd)]
    for name, method in methods:
        print("Running {} engine".format(name))
        try:
            result = method()
            print("\tObtained {}".format(result))
        except Exception as e:
            print("\tFailed ({})".format(e))
            traceback.print_exc()


if __name__ == "__main__":
    main()
