from pyperplan.ma.parse.lisp_parsers.domain_parser import *
from pyperplan.ma.parse.lisp_parsers.problem_parser import *

domain = DomainParser(Path("../../benchmarks/multi-agent/blocksworld/domain/domain.pddl")).parse_domain()
problem = ProblemParser(Path("../../benchmarks/multi-agent/blocksworld/problems/probBLOCKS-9-0.pddl"), domain)