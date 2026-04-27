---
name: behavioral-spec-extraction
description: Probe-Summarize-Refute procedure for deriving a frozen-quality behavioural spec from a black-box original system. Invoke when an Observation subagent needs to draft a new spec artifact.
---

# Behavioural Spec Extraction (Probe-Summarize-Refute)

This skill encodes the three-pass loop every spec-extractor follows. It
guarantees that no assertion in the resulting spec is ungrounded
(`probe_refs` array is non-empty) and that the spec has been
adversarially reviewed before it is frozen.

## When to use

Whenever a new spec id is needed (`/discover-command <name>` triggers
this) or whenever an existing spec is bumped due to a divergence
classified as `spec-gap`.

## Inputs

- `spec_id` — kebab-case identifier matching the schema regex.
- `target.feature` — human-readable feature name.
- `target.original_version` — version string of the pinned
  `original/redis-server`.

## Outputs

- `specs/<spec_id>.json` — validates against
  `volumes/IV/schemas/spec-artifact.schema.json`, status: `frozen`.
- `specs-raw/<spec_id>/probes.jsonl` — append-only probe log.
- `specs-raw/<spec_id>/review-probes.jsonl` — reviewer's counter-probes.
- `transcripts/observation/<spec_id>.md` — extractor reasoning.

## Pass 1 — Probe

Goal: collect enough black-box evidence that every behavioural assertion
you might want to make is grounded by at least one probe.

1. Start the original on a unique port. Always pass `--save '' --appendonly no`
   so probes do not pollute disk.
2. Always run `FLUSHDB` between independent probe groups so prior state
   cannot influence the next probe.
3. Probe the **happy path** first: simple inputs, expected success.
4. Probe **type errors**: pass an integer where a string is expected,
   pass an empty list, pass a list of one element where two are
   required.
5. Probe **boundary values**: 0, 1, -1, INT64_MIN, INT64_MAX, empty
   string, single-byte string, 512MB-1 string (Redis's value cap).
6. Probe **command-modifier interactions**: if the command takes
   options (e.g., `SET ... EX` / `PX` / `NX` / `XX`), probe every
   pair-wise combination plus the "all options" case.
7. Probe **state-dependent paths**: SET on existing vs non-existing;
   GET on TTL'd key just before and just after expiration.
8. Capture **wire bytes** when the response is a non-trivial RESP shape
   (arrays, nested arrays, NULLs, booleans). Use
   `printf '...' | nc -q1 127.0.0.1 $PORT | xxd`.

Each probe row in `probes.jsonl` MUST have a unique `P-NNN` id, the
exact command, captured output, exit code, and a timestamp.

## Pass 2 — Summarize

Goal: turn the probe log into a structured spec artifact.

1. Group probes by behaviour. A behaviour is "for inputs X, the output
   is Y under preconditions Z". Each behaviour cites every probe that
   demonstrates it (typically 2–6 probes).
2. Promote any probe that shows a side effect (TTL set, key deleted,
   counter incremented) into a `side_effects[]` entry.
3. Promote probes that hit error paths into `edge_cases[]` rather than
   `behaviors[]`.
4. Identify invariants — properties that hold across many behaviours.
   Examples: "GET after SET k v returns v" (lasting until DEL/EXPIRE).
   Each invariant cites probes that exercise it.
5. List **unprobed but suspected** behaviours under `open_questions[]`.
   These are explicitly NOT promised by the spec.

Validate the draft locally against
`volumes/IV/schemas/spec-artifact.schema.json` before invoking
`mcp__spec-store__write_spec`. The MCP server will validate again, but
catching errors locally saves a round-trip.

## Pass 3 — Refute

Goal: have the spec adversarially reviewed by `spec-reviewer` before
freezing.

1. Hand the draft (by id, never by content) to the coordinator.
2. The coordinator delegates to `spec-reviewer`, which constructs
   counter-probes for every assertion and runs them against
   `original/redis-server`.
3. If the reviewer returns `verdict: needs-revision`, the coordinator
   bounces back to `spec-extractor` with the refutation list. Repeat
   from Pass 1 for the affected behaviours only.
4. When the reviewer returns `verdict: approve`, the coordinator calls
   `mcp__spec-store__freeze_spec`. Implementation can now begin.

## Cost guidance

A typical RESP command spec costs ~$0.40–$1.20 to extract end-to-end
(roughly: extractor 60–120 probes × Sonnet, reviewer 20–40 counter-probes
× Sonnet, probe-runner Haiku). Configure
`ANTHROPIC_BUDGET_USD` accordingly per `/discover-command` invocation.

## Cross-references

- Schema: `volumes/IV/schemas/spec-artifact.schema.json`
- Subagent: `.claude/agents/spec-extractor.md`,
  `.claude/agents/probe-runner.md`, `.claude/agents/spec-reviewer.md`
- MCP: `mcp-servers/spec-store/`
- Chapter: `volumes/IV/chapters/chapter18_llm_specification_extraction.md`
