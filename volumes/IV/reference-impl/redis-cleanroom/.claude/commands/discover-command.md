---
description: Discover the behaviour of a single Redis command and produce a frozen spec artifact. Triggers the Observation pipeline.
argument-hint: <COMMAND-NAME>
allowed-tools: Task
---

You are running `/discover-command $1`.

Goal: produce a frozen `specs/<spec_id>.json` that conforms to the
spec-artifact schema, with every behaviour grounded by at least one probe.

Steps:

1. Normalise `$1` to a kebab-case `spec_id` (e.g., `SET` → `set`,
   `COMMAND DOCS` → `command-docs`).
2. Check `mcp__spec-store__list_specs`. If a frozen spec already exists
   for this id, abort with: `SPEC_ALREADY_FROZEN spec_id=<id>`.
3. Delegate to the **coordinator** subagent with this exact prompt
   (no prose elaboration; the coordinator owns the contract):

   ```
   FEATURE_DISCOVER spec_id=<id> command=$1 budget_usd=2.00
   Procedure:
     a) Spawn spec-extractor to draft per the behavioral-spec-extraction skill.
     b) Spawn spec-reviewer to refute the draft.
     c) Loop a)/b) until verdict=approve or 3 iterations exceeded.
     d) On approval, mcp__spec-store__freeze_spec.
   Forward only spec_id between subagents. Never paste probe transcripts
   or extractor reasoning into impl-team-bound prompts.
   ```

4. After the coordinator returns, print:

   ```
   DISCOVER_COMPLETE spec_id=<id> status=frozen iterations=<n>
   ```

   or, on failure:

   ```
   DISCOVER_FAILED spec_id=<id> reason=<short reason>
   ```

Note: this command never edits files directly. All file work happens
inside the spawned subagents; the coordinator is the only path between
them. See chapter 18 §6 for the full delegation tree.
