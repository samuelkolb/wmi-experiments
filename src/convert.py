import os
from argparse import ArgumentParser

from pywmi import nested_to_smt, Domain, Density


def convert_queries(filename, out_filename=None):
    if not os.path.isfile(filename):
        for f in os.listdir(filename):
            if os.path.isfile(f):
                f = os.path.join(filename, f)
                convert_queries(f, out_filename)
        return

    domain = Domain.make([f"A_{i}" for i in range(4)], [f"x_{i}" for i in range(4)], real_bounds=(-100, 100))
    support = None
    weight = None
    queries = []
    with open(filename) as ref:
        for line in ref:
            if not support:
                support = nested_to_smt(line)
            elif not weight:
                weight = nested_to_smt(line)
            else:
                parts = line.split(",")
                queries.append(nested_to_smt(parts[0]))
    density = Density(domain, support, weight, queries)
    if out_filename:
        if os.path.exists(out_filename) and not os.path.isfile(out_filename):
            out_filename = os.path.join(out_filename, os.path.basename(filename))
        density.to_file(out_filename)


def main():
    parser = ArgumentParser()
    parser.add_argument("type")
    parser.add_argument("filename")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()
    if args.type == "queries":
        convert_queries(args.filename, args.output)


if __name__ == '__main__':
    main()
