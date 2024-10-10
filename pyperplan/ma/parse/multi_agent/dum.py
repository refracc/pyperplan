import os
from pathlib import Path

from pyperplan.ma.parse.multi_agent import MultiAgentDomainsConverter

domain = Path("../../../../benchmarks/multi-agent/blocksworld/domain/domain.pddl")

converter = MultiAgentDomainsConverter(domain)
print(converter.locate_domains())