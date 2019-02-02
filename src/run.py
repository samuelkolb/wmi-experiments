from argparse import ArgumentParser

from autodora.trajectory import product
from autodora.runner import CommandLineRunner
from autodora.sql_storage import SqliteStorage
from experiment import VolumeExperiment


def main():
    parser = ArgumentParser()
    parser.add_argument("problem")
    args = parser.parse_args()

    if args.problem == "xor":
        problem_dict = {"problem": [f"xor_{i}" for i in range(1, 21)]}
        solver_dict = {"solver": [
            "xadd:moriginal",
            "xadd:mresolve",
            "rej:n1000000",
            "n-xsdd:blatte",
            "n-xsdd:brej.100000.1",
            "n-xsdd:brej.100000",
        ]}

        trajectory = VolumeExperiment.explore("xor", product(problem_dict, solver_dict))

        storage = SqliteStorage()
        storage.remove("xor")
        CommandLineRunner(trajectory, storage, 3, timeout=60).run()
    elif args.problem == "mutex":
        problem_dict = {"problem": [f"mutex_{i}" for i in range(1, 21)]}
        solver_dict = {"solver": [
            "xadd:moriginal",
            "xadd:mresolve",
            "rej:n1000000",
            "n-xsdd:blatte",
            "n-xsdd:brej.100000.1",
            "n-xsdd:brej.100000",
        ]}

        trajectory = VolumeExperiment.explore("mutex", product(problem_dict, solver_dict))

        storage = SqliteStorage()
        # storage.remove("mutex")
        CommandLineRunner(trajectory, storage, timeout=60).run()


if __name__ == "__main__":
    main()
