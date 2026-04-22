# Execution Efficiency Analysis — tjce-agent-apf

## Assessment

The agent is compact, stateless, and structurally efficient: a single capability (`count-capability.md`) is loaded on-demand via routing, keeping SKILL.md lean, and the pre-pass found zero sequential/dependency issues. There is no multi-source delegation, no subagent chain, and no memory-loading concern. The main opportunities are tactical: batching the three prerequisite existence checks at activation and batching the per-function `calculate-fp.py` invocations in Step 4, both currently expressed as sequential loops.

## Key Findings

### Finding 1 — Prerequisite checks not batched (Medium)

- **File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/SKILL.md:46-54`
- **Current pattern:** The "Prerequisite Check" section lists three independent file existence verifications (`user-stories.md`, `business-rules.md`, `data-model.md`) as a bulleted list without instruction to check them in a single batched tool call. A naive LLM reader is likely to issue three sequential Read/Glob calls.
- **Efficient alternative:** Add an explicit directive: "Verify all three artifacts in a single batched tool call (parallel Globs or a single `ls`/Glob pattern covering the requirements and architecture dirs)." Then branch on the combined result.
- **Estimated savings:** 2 round-trips per activation (~2-4s latency, minor token overhead per extra tool call).

### Finding 2 — `calculate-fp.py` invoked per-function in a sequential loop (Medium)

- **File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/references/count-capability.md:91-99` (Passo 4)
- **Current pattern:** The example shows one `python3 scripts/calculate-fp.py ...` call per function ("# etc. para cada funcao"). For a realistic count with 10-30+ functions, this implies 10-30+ sequential Bash invocations — each paying Python startup cost (~100-200ms) and a tool round-trip.
- **Efficient alternative:** Two options, pick one:
  1. **Batch in one Bash call:** Instruct the agent to compose all calculations into a single shell invocation (e.g., heredoc feeding a loop, or a single python process reading a JSON/CSV of functions). This collapses N round-trips + N Python startups into 1.
  2. **Extend `calculate-fp.py` to accept a batch input file** (e.g., `--batch functions.json`) so one invocation processes the full catalog.
- **Estimated savings:** For a 20-function count, ~19 saved tool round-trips and ~19 × ~150ms saved Python startup ≈ 3-6s plus meaningful token savings from avoided tool-call overhead.

### Finding 3 — Step ordering is strictly sequential but steps 2 and 3 are independent (Low)

- **File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/references/count-capability.md:62-89` (Passo 2 and Passo 3)
- **Current pattern:** Passo 2 (Data Functions classification) and Passo 3 (Transactional Functions classification) are presented sequentially. They both consume the same three input artifacts already read in Passo 1 and do not depend on each other's output (only Passo 4's calculations consume both).
- **Efficient alternative:** State explicitly that Passo 2 and Passo 3 are independent and may be reasoned about in a single pass / parallel cognitive stream, with Passo 4 (script calls) batched across both. This is more a prose/framing improvement than a tool-batching gain since both steps are pure reasoning.
- **Estimated savings:** Minimal at tool-call level; mainly clarity and slightly shorter reasoning.

### Finding 4 — Script invocations use relative path `scripts/...` (Low, correctness-adjacent)

- **File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/references/count-capability.md:94-96, 108`
- **Current pattern:** `python3 scripts/calculate-fp.py ...` and `python3 scripts/validate-fp-sources.py ...` assume CWD is the skill root. In an agent Bash session where CWD may differ, calls can fail, prompting retry cycles (silent efficiency loss).
- **Efficient alternative:** Use `{skill-root}/scripts/...` or an absolute-path template resolved at activation. Eliminates failure-and-retry round-trips.
- **Estimated savings:** Probabilistic — avoids 1-2 failed-call round-trips on runs where CWD is unexpected.

## Optimization Opportunities

- **Batch-mode script (structural):** If `calculate-fp.py` grew a `--batch` input mode (JSON array of `{type, der, rlr_or_alr, id}` objects → JSON array of `{id, complexity, pf}`), Passo 4 becomes one call regardless of function count, and the catalog write in Passo 7 becomes a simple JSON→markdown projection. Biggest single efficiency win available.
- **Combined prerequisite + load in one pass:** At activation, a single parallel Read batch could: read config files (`config.yaml`, `config.user.yaml`), verify artifact existence via a Glob, and — if routing to CONTAGEM — read the three requirement artifacts. This collapses three logical phases into one parallel tool-call block.
- **Validation-and-calculation fusion:** Passo 5 (`validate-fp-sources.py`) and Passo 4 (`calculate-fp.py`) are independent after the catalog is drafted. They could be invoked in a single batched Bash message rather than serially.

## What's Already Efficient

- **On-demand reference loading:** Only `count-capability.md` is loaded, and only when the CONTAGEM capability is triggered. SKILL.md stays small. (`SKILL.md:60-64`)
- **Fast-path short-circuit:** "Correcao em Garantia" bypasses all reading, inventory, script calls, and validation — writes two trivial artifacts and stops. Excellent early-exit design. (`count-capability.md:20-47`)
- **Prerequisite gating before expensive work:** The agent refuses to proceed to counting when requirement artifacts are missing, preventing wasted downstream computation. (`SKILL.md:46-56`)
- **Deterministic script offload:** Complexity classification is delegated to `calculate-fp.py` rather than relying on LLM reasoning, which is both correct and token-efficient. (`count-capability.md:91-101`)
- **Stateless single-capability design:** No memory files, no subagent delegation, no multi-source fan-out — the agent correctly avoids patterns it doesn't need. Pre-pass confirms zero dependency issues.
- **Headless contract is explicit:** Exit codes, ambiguity handling, and JSON stdout are all specified, preventing retry/clarification loops in automated use. (`SKILL.md:68-74`, `count-capability.md:192-198`)
