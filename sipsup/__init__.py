"""sipsup — a minimal, transparent, local-first SipSup.

Four pillars, one module each:
  harness  → sipsup/runtime + sipsup/gateway  (scaffolding around the raw LLM)
  loop     → sipsup/loop                      (observe → reason → act → repeat)
             sipsup/graph                     (opt-in structure around the loop — extends this pillar)
  memory   → sipsup/memory                    (procedural / semantic / episodic)
  ops      → sipsup/ops + evals/              (trace → eval → gate → release)
"""

__version__ = "0.1.6"
