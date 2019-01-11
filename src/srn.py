import json
import os

from pywmi import import_domain


def load():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "res", "srn", "steps3_iteration1.txt")) as f:
        flat = json.load(f)

    variables = []
    types /
    print(flat["domain"])


    domain = import_domain(flat["domain"])
    print(domain)
    print(flat.keys())

if __name__ == "__main__":
    load()