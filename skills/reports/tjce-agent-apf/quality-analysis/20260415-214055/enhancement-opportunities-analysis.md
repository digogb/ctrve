# Enhancement Opportunities — tjce-agent-apf

Scanner: **DreamBot** (creative edge-case & experience innovation lens)
Target: `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf`
Date: 2026-04-15

---

## Agent Understanding

`tjce-agent-apf` is a deterministic Function Point analyst for TJCE judicial software projects, applying IFPUG CPM 4.3.1. Its primary users are the TJCE metrics manager and delivery-responsible developers who need auditable, traceable counts tied to US/RN identifiers, with a fast-path for "Correcao em Garantia" (PF = 0). Its key assumptions: requirement artifacts already exist at canonical paths (`user-stories.md`, `business-rules.md`, `data-model.md`), the user speaks Portuguese, the analyst reasoning is always step-by-step, and complexity never comes from judgment — only from the matrix via `calculate-fp.py`.

---

## User Journeys

### 1. The First-Timer (developer who has never counted PF)
**Narrative:** A junior dev wraps a small TJCE feature and is told to "run the APF agent." They invoke it with no preparation.

- **Entry friction:** The agent silently expects `user-stories.md` / `business-rules.md` / `data-model.md`. If missing, it emits a terse block message pointing at `tjce-agent-requirements` and stops. The first-timer is never told WHY those three files exist, what a DER or RLR is, or that they can bail out cleanly. There is no "quero aprender" path.
- **Mid-flow:** SKILL.md is densely technical ("ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF"). A newcomer has no glossary, no worked example, and no safe ground to ask "o que significa RLR?".
- **Exit:** Even after a successful count, the agent dumps two MD files. No onboarding tooltip, no "o que fazer com esses numeros agora" (submit to the gestor? append to contract? compare to previous delivery?).
- **Bright spot:** The "Pergunte, nao assuma" principle would engage the newcomer gently — **if** it were actually triggered before launching into technical classification.

### 2. The Expert (seasoned APF analyst)
**Narrative:** Knows IFPUG cold, already has a mental inventory of functions, just wants to crank through a count.

- **Entry friction:** Must wait through sequential reading of 3 artifacts even when they already know the function list. There is no "paste your function inventory and classify" mode.
- **Mid-flow:** Every function triggers a scripted step 1-6. No batch-classify option. No shortcut to "classificar lote: [{tipo, der, rlr/alr}...]".
- **Exit:** Happy with the auditable output. Likely frustrated by pacing.
- **Bright spot:** `calculate-fp.py` is CLI-accessible and composable — the expert could bypass the agent entirely and still be IFPUG-conformant.

### 3. The Confused User (wrong intent)
**Narrative:** Invokes the agent thinking it will also generate the user-stories. Or believes "PF" means "Pull Request".

- **Friction:** Prerequisite check blocks with "utilize a skill `tjce-agent-requirements`" but does not offer to chain into it or hand off context. Dead end.
- **No soft-gate:** The agent never pauses to ask "qual seu objetivo nesta sessao?" before diving into file reads.

### 4. The Edge-Case User
**Narrative:** Delivery mixes new features AND a warranty correction. Or delivery has functions spanning two TJCE systems (some ALI, some AIE depending on perspective).

- **Friction #1 — Mixed delivery:** SKILL.md treats Garantia as a binary fast-path. No flow handles "parte Garantia + parte nova contagem".
- **Friction #2 — Cross-system AIE boundary:** The prompts do not help the user decide which is the "application in count" when a single delivery touches systems A and B. No tie-breaking heuristic.
- **Friction #3 — Re-count after scope change:** No mechanism to diff against a previous `contagem-detalhada.md` and report delta PF (crucial for contract amendments).
- **Friction #4 — Changes to an existing ALI:** IFPUG distinguishes initial count vs. enhancement count (CFP — Counting for enhancement Project). SKILL.md only speaks of "nova contagem" or "Garantia". No enhancement mode (added DER, deleted RLR) which is actually the most common TJCE scenario.

### 5. The Hostile Environment
**Narrative:** `calculate-fp.py` missing, Python 3.8 only, or `data-model.md` exists but is empty.

- The SKILL says "se `calculate-fp.py` nao pode ser executado, pedir ao usuario que rode localmente" — good graceful fallback for missing Python. But:
  - No check that `python3` resolves. If it is `python` only, the script quietly fails.
  - `data-model.md` missing is handled; `data-model.md` present-but-empty is not.
  - No schema check on `user-stories.md` — a malformed stories file yields zero US-NNN matches and triggers a cryptic "nenhuma funcao encontrada" later.
- The validator emits exit 2 with a Portuguese message for parse failure — good — but `validate-fp-sources.py` exits **0** at the end of `main()` after validation (bug: it calls `sys.exit(0 if result["valid"] else 1)` correctly, confirmed).

### 6. The Automator (CI / another skill)
**Narrative:** Pipeline builds a release and wants a headless PF count as a contract artifact.

- **Strong:** Explicit `--headless` / `-H` contract, exit codes, JSON output, Garantia shortcut via `garantia` arg.
- **Gaps:**
  - No way to pass `--project-name`, `--delivery-name`, `--responsible`, `--tdi` as flags. The artifact template has `{nome}` / `{data}` / `{responsavel}` placeholders that headless mode must fill — unclear contract for where these come from (env? config? args?).
  - Headless VAF falls back to 1.00 with a warning note — good — but no way to inject `--tdi 35` at invocation.
  - JSON shape is described ("total PF brutos, PF ajustado, VAF, contagem por tipo, pendentes, is_garantia") but not fixed with a schema. Consumers will guess field names.
  - No machine-readable **input** contract: an automator who already has the function inventory cannot feed `functions.json` directly; the agent insists on reading three MD files.

---

## Headless Assessment

**Level: Easily adaptable.** The agent is already 70% headless-ready. The remaining friction is in input contract flexibility, not interaction removal.

**What could auto-resolve today:**
- File reading, function inventory, complexity classification, PF math, artifact writing — all fully deterministic given the three input artifacts.
- Garantia fast-path — already trivially headless.

**What needs explicit input even in headless:**
- Project/delivery name, responsible name, date override
- TDI value (currently forced to 1.00 fallback)
- Scope hint when the data model implies multiple possible "applications in count"

**Suggested invocation contract:**
```
tjce-agent-apf --headless \
  --project "SAJ-Modulo-Execucao" \
  --delivery "Sprint 42" \
  --responsible "Nome Sobrenome" \
  --tdi 35 \
  --output-dir _bmad-output/apf-sprint42 \
  --json
```
Plus an optional `--functions-json <path>` that bypasses MD reading and feeds a pre-built inventory, unlocking pipeline and other-agent chaining.

Output (JSON schema):
```json
{
  "pf_brutos": 0, "pf_ajustado": 0.0, "vaf": 1.0, "tdi": 35,
  "por_tipo": {"ALI": {"qtde": 0, "pf": 0}, ...},
  "pendentes": 0, "is_garantia": false,
  "artefatos": {"contagem": "...", "resumo": "..."}
}
```

---

## Key Findings

### HIGH-OPPORTUNITY

**H1. Missing Enhancement Count mode (CFP) — most common TJCE scenario absent**
Area: SKILL.md, count-capability.md
Observation: TJCE deliveries are overwhelmingly incremental — adding a DER to an existing ALI, a new EE on an existing ALI, a changed RN. IFPUG CPM 4.3.1 defines this as an Enhancement Count with distinct rules (count only changed/added/deleted function points). The agent only models "new count" vs "Garantia". An enhancement treated as a new count inflates PF — a contractual integrity issue.
Suggestion: Add an `enhancement` entry point (or arg `--tipo enhancement`) that requires a baseline `contagem-detalhada.md` reference, asks per-function whether each is ADDED / CHANGED / DELETED / UNCHANGED, and computes CFP per CPM 4.3.1 formula. Artifact gets a Delta section.

**H2. No "quick-win" / "paste function inventory" mode for experts**
Area: count-capability.md Passo 1-4
Observation: Experts who already know the inventory must still wait for the three-file ingest flow. This is ceremony, not value.
Suggestion: Offer an explicit Mode: **Lote Direto** where the user provides a table/JSON of `{nome, tipo, der, rlr/alr, fonte_us_rn}` and the agent skips Passo 1-3, runs classification + validation + artifact generation. Great candidate for three-mode architecture: Guided / Yolo / Autonomous.

**H3. Intent-before-ingestion violated**
Area: SKILL.md On Activation
Observation: Agent immediately checks prerequisites and blocks if files missing, before understanding user intent. A user with a Garantia task is forced past the prerequisite gate unnecessarily (Garantia relaxes them, but the gate runs first).
Suggestion: Reorder activation to: greet → ask "contagem nova, enhancement, ou correcao em garantia?" → THEN apply the appropriate prerequisite set. Implement soft-gate elicitation at this decision point.

**H4. Delta against previous count is unsupported**
Area: capability gap
Observation: Contract addendums require "what changed since last count". No diff capability exists.
Suggestion: Add a lightweight capability `DIFF` that reads two `contagem-detalhada.md` and emits `delta-apf.md`: functions added, removed, reclassified (with before→after), net PF delta. Pairs perfectly with H1.

### MEDIUM-OPPORTUNITY

**M1. Function-level explain-on-demand advertised but not discoverable**
Area: count-capability.md Interactive Mode
Observation: The capability mentions "mostrar o raciocinio funcao por funcao ao usuario quando ele pedir 'explique esta contagem'" — but the user is never told this invitation exists.
Suggestion: After writing artifacts, emit: "Quer que eu explique alguma funcao especifica? Responda com o ID (ex: FT-001) ou 'todas'."

**M2. Ambiguity capture is all-or-nothing**
Area: Headless ambiguity handling
Observation: Headless marks `CLASSIFICACAO PENDENTE` and exits 1. Interactive "pausa apos 3 ambiguidades" is arbitrary and silent until trigger.
Suggestion: Maintain a visible running tally ("2 classificacoes ambiguas acumuladas") and implement capture-don't-interrupt: accept user's out-of-scope comments about a function and stash them in a `notas.md` sidecar.

**M3. No glossary or worked example for newcomers**
Area: references/
Observation: No `glossario-ifpug.md` or `exemplo-contagem-tjce.md`. Newcomers depend entirely on external IFPUG docs.
Suggestion: Add `references/glossario.md` (DER, RLR, ALR, ALI/AIE/EE/SE/CE in plain Portuguese with TJCE examples) plus `references/exemplo-contagem.md` (a fully worked Sprint example). Link from SKILL.md.

**M4. Parallel review lenses never used before final output**
Area: Passo 7
Observation: Artifacts are written straight to disk. No skeptic / double-count-hunter review pass, despite the domain being exactly where a second-pair-of-eyes matters (double counting is principle #3).
Suggestion: Before writing final artifacts, fan out a "double-count hunter" sub-agent over the inventory + a "missing-function hunter" that cross-checks user-stories.md against the function list. Add a 1-paragraph review summary to `resumo-apf.md`.

**M5. TDI elicitation is a missed structured moment**
Area: Passo 6
Observation: "Se o usuario nao fornece TDI, pedir avaliacao das 14 caracteristicas" — but no structured form is offered. User has to remember what the 14 are.
Suggestion: Present the 14 GSC as a numbered checklist with 0-5 scoring and one-line TJCE-contextual descriptions. Output the TDI summary table into `resumo-apf.md`.

**M6. Dual-output opportunity for downstream LLM agents**
Area: artifact design
Observation: `contagem-detalhada.md` is human-first. A downstream agent (e.g., pricing, sprint-planning) has to re-parse tables.
Suggestion: Also emit `apf-distillate.json` — compact machine contract with function list, classifications, totals. Point `bmad-distillator` at it or produce directly.

**M7. No prerequisites recovery beyond "vai usar outra skill"**
Area: SKILL.md prerequisite gate
Observation: Dead-end when requirements missing.
Suggestion: Offer: "(a) invocar tjce-agent-requirements agora, (b) classificar em modo preliminar a partir de uma descricao narrativa com aviso 'contagem nao-auditavel', (c) cancelar". Option (b) preserves momentum for experts who want a back-of-envelope.

### LOW-OPPORTUNITY

**L1. `python3` vs `python` portability**
Area: capability Passo 4
Observation: Hardcoded `python3`. Windows / some venvs alias to `python`.
Suggestion: Probe once at activation; use the resolved name.

**L2. JSON schema for headless output unpinned**
Area: Headless Contract
Suggestion: Pin the schema inline in SKILL.md or reference it from a JSON Schema file in `references/`.

**L3. Date/project placeholders in artifacts**
Area: Passo 7 templates
Observation: `{nome}`, `{data}`, `{responsavel}` are placeholders with no stated resolution rule.
Suggestion: Define resolution order (args > config > user prompt > system defaults).

**L4. `validate-fp-sources.py` does not detect duplicate function IDs**
Area: script
Observation: Two rows with `FT-001` would both pass validation. Given principle #3 (no double count), this is a thematic gap even if technically different from source validation.
Suggestion: Add dup-ID detection; optionally also duplicate function-name + same ALR pattern warning.

**L5. No visible progress in long counts**
Area: capability Passo 3/4
Suggestion: Emit "classificando FT-007 de 24..." in interactive mode for deliveries with >10 functions.

---

## Top Insights

1. **The enhancement count blind spot (H1) is the single biggest product risk.** TJCE deliveries are almost never greenfield; treating every delivery as a new full count silently inflates PF, which could create contract disputes. This is the opportunity that would transform the agent's real-world value the most.

2. **The agent has an elegant deterministic core (matrices + scripts) but a rigid entry funnel.** Adding a mode router at activation (new / enhancement / garantia / lote / diff) would quadruple its addressable scenarios with tiny code surface.

3. **Headless is 80% there but hobbled by soft input contract.** Pinning the JSON output schema and allowing `--functions-json` input would let this agent become a callable primitive for other TJCE skills — exactly the composable-by-design pattern that makes BMad ecosystems powerful.

---

## Facilitative Patterns Check

| Pattern | Present? | Value if Added |
|---|---|---|
| Soft Gate Elicitation | Partial — "Pergunte, nao assuma" principle exists but no concrete soft-gate language in capability flow | **Medium-high** — natural fit at intent routing and "mais alguma funcao?" moments |
| Intent-Before-Ingestion | **Missing** — prerequisites checked before intent | **High** — see H3 |
| Capture-Don't-Interrupt | **Missing** — ambiguities block or halt | **Medium** — see M2 |
| Dual-Output | **Missing** — only human MD | **Medium** — see M6 |
| Parallel Review Lenses | **Missing** | **Medium** — see M4 |
| Three-Mode Architecture | Partial — headless + interactive exist; no Yolo-style "just do it with smart defaults" | **High** — Lote Direto mode (H2) essentially is this |
| Graceful Degradation | Present for missing data-model and missing Python; absent for empty/malformed artifacts | **Low-medium** — see hostile environment |

The two patterns whose absence matters most for this specific agent: **Intent-Before-Ingestion** (fix flow ordering) and **Three-Mode Architecture** (add expert fast-path). Together they remove the most friction for real users.
