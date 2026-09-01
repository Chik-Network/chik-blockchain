from __future__ import annotations

from chik.server.start_service import Service
from chik.solver.solver import Solver
from chik.solver.solver_api import SolverAPI
from chik.solver.solver_rpc_api import SolverRpcApi

SolverService = Service[Solver, SolverAPI, SolverRpcApi]
