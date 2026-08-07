---
spec_version: 0.4.1
---

# Typed evidence records

`itl-evidence/1.0` is a provider-neutral, canonical compact UTF-8 JSON data
record with a final LF. It records an observation claim; it is not a runner,
not an authority grant, and not proof that an external effect occurred.

Every record has exactly these fields: `format`, `lock_sha256`, `node_id`,
`state_revision`, `observer`, `locator`, `content_sha256`, `claim`, `verdict`,
and `caller_sanitized`. `lock_sha256` and a non-null `content_sha256` are lowercase
SHA-256 digests. `content_sha256` is always present and is either such a digest
or `null`; this single shape keeps canonical records deterministic.

The referenced lock MUST validate as `itl-workflow-lock/1.0` from its exact
bytes. `node_id` MUST name an enabled flattened node in that lock, and
`state_revision` MUST be a nonnegative integer. `observer` and `claim` are
caller-sanitized non-empty strings. `locator` is a safe relative portable
token/path (never absolute or traversing). The caller MUST set
`caller_sanitized` to `true`; this records a boundary declaration, not a
guarantee about an external source. The fixed verdict vocabulary is `observed`,
`not_observed`, `partial`, and `deferred`.

Unknown fields fail closed. Records MUST NOT contain authority, approval,
credentials, secrets, prompts, transcripts, or equivalents; those tokens also
fail in free-text fields. Evidence can support a
reviewable claim, but protected effects still require fresh authority and
independent observation appropriate to the effect.
