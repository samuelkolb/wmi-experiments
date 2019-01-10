import pywmi
import pysmt.shortcuts as smt


def get_problem():
    domain = pywmi.Domain.make([], ["x", "y"], [(-1, 1), (-1, 1)])
    x, y = domain.get_symbols(["x", "y"])
    formula = (x >= 0) & (x <= y) & (y <= 1)
    return domain, formula, smt.Real(1)


def rejection():
    domain, formula, weight = get_problem()
    return pywmi.RejectionEngine(domain, formula, weight, 100000).compute_volume()


def xadd():
    domain, formula, weight = get_problem()
    return pywmi.XaddEngine(domain, formula, weight).compute_volume()


def main():
    methods = [("rejection", rejection), ("XADD", xadd)]
    for name, method in methods:
        print("Running {} engine".format(name))
        try:
            result = method()
            print("\tObtained {}".format(result))
        except Exception as e:
            print("\tFailed ({})".format(e))


if __name__ == "__main__":
    main()
