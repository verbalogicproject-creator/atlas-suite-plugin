---
name: project-atlas
description: Build, refresh, validate, inspect, or query an agent-first deterministic Project Atlas and its four-file orientation hub. Use for repository orientation, bounded task context, architecture and impact maps, handoffs, completion evidence, or Project/Five-Atlas workflows.
---

# Project Atlas

Use the paired DKG framework as the only writer, compiler, and resolver.
Project Atlas is a projection over source; source, tests, receipts, and current
human decisions retain stronger authority.

1. Read `references/contract.md`, repository instructions, Git state, manifests,
   architecture, commands, tests, evidence, and current-status documentation.
2. Open the menu with `../../scripts/atlas`, or inspect commands with
   `../../scripts/atlas menu --choice 7`.
3. Build the combined five-Atlas hub only when a build is authorized:
   `../../scripts/atlas atlas build --source <root> --state-root <state> --output <bundle>`.
4. Request bounded task context with
   `../../scripts/atlas atlas context "<task>" --output <bundle> --budget-tokens 1800`.
5. Validate with `../../scripts/atlas atlas check --output <bundle>` and inspect
   direct static impact with `../../scripts/atlas atlas impact <path> --output <bundle>`.
6. Treat `project-atlas.json` as canonical compiled context. Read `index.html`
   first for the concise map, then inspect selected source files in order.
7. Report degraded capabilities, stale evidence, omitted context, and proof
   limits. Context chooses what to read; it does not grant authority.

Use `atlas run --flags project` only for the isolated Project child snapshot.
Source annotation remains preview-only until a separate exact approval names
the target files. Network access, models, plugin installation, publication,
deployment, commits, and active source promotion require separate authority.
