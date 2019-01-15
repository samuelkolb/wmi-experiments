import json
import os

from pysmt import shortcuts as smt

from pywmi import import_domain
from pywmi.domain import import_density
from pywmi.parse import smt_to_nested, nested_to_smt
from pywmi import XsddEngine



def load(path, file_name, domain_real):
    wmi_problem = {}

    path = os.path.join(*path)
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path,file_name)) as f:
        flat = json.load(f)

    domain = {}
    variables = flat.pop("domain")
    var_types = { v["name"]:v["type"] for v in variables }
    variables = list(var_types.keys())

    domain["variables"] = variables
    domain["var_types"] = var_types
    domain["var_domains"] = {str(v):domain_real for  v in domain["var_types"] if domain["var_types"][v]=="real"}
    flat["domain"] = domain

    domain = import_domain(flat["domain"])

    query = nested_to_smt(flat["queries"][0]["formula"])
    queries = [query]

    evidence = flat["queries"][0]["evidence"]
    evidence = ["(=(var real {}) (const real {}))".format(k,v) for k,v in evidence.items()][0] #only works for one evidence point
    evidence = nested_to_smt(evidence)
    support = nested_to_smt(flat["support"])
    support = smt.And(support, evidence)

    weight = nested_to_smt(flat["weight"])

    return domain, queries, support, weight



def main(path, file_name, domain_real):
    domain, queries, support, weight = load(path, file_name, domain_real)
    return XsddEngine(domain, support, weight).compute_probability(queries[0], collapse=True)



FILE_NAME = "steps2_iteration1.txt"
PATH = ["res", "srn"]
DOMAIN = [100.0, 100.0]
if __name__ == "__main__":
    main(PATH, FILE_NAME, DOMAIN)
