import os

from pywmi.__main__ import get_engine
from pywmi.domain import Density

from pydora.experiment import Experiment, Result, Parameter, derived
import pysmt.shortcuts as smt


class VolumeExperiment(Experiment):
    problem = Parameter(str, None, "The problem filename")
    solver = Parameter(str, None, "The solver")
    volumes = Result(list, None, "The calculated volume")

    @derived
    def filename(self):
        problem = self["problem"]
        if problem.startswith("xor") and "." not in problem:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "xor", f"generated_{problem}.json")
        elif problem.startswith("mutex") and "." not in problem:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "mutex", f"generated_{problem}.json")

    @derived
    def n(self):
        problem = self["problem"]
        if problem.startswith("xor") and "." not in problem:
            return int(problem.split("_")[-1])
        elif problem.startswith("mutex") and "." not in problem:
            return int(problem.split("_")[-1])
        return -1

    def run_internal(self):
        density = Density.import_from(self["filename"])
        solver = get_engine(self["solver"], density.domain, density.support, density.weight)
        if not density.queries or (len(density.queries) == 1 and density.queries[0] == smt.TRUE()):
            self["volumes"] = [solver.compute_volume()]
        else:
            self["volumes"] = [solver.compute_probabilities(density.queries)]


VolumeExperiment.enable_cli()
