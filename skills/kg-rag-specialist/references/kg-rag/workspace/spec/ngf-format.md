---
spec_version: 0.4.1
---

# Normative Grounded Framework format

A Normative Grounded Framework (NGF) is a Markdown document that separates
controlling requirements, sourced explanation, unapproved design, and observed
evidence. An NGF is documentation, not an execution mechanism, authority grant,
or substitute for an independently checked receipt.

## Document contract

An NGF MUST begin with one YAML mapping containing exactly these keys in this
order: `ngf_format`, `document_id`, `title`, `revision`, `status`,
`authority_class`, `source_manifest`, and `last_updated`.

`ngf_format` MUST equal `normative-grounded-framework/1.0`. `document_id` MUST
be a repository-unique lower-case identifier. `title` MUST be non-empty.
`revision` MUST be a semantic version. `status` MUST be one of `draft`,
`reviewed`, `superseded`, or `retired`. `authority_class` MUST be one of
`controlling-contract`, `applied-framework`, `methodology`, or `evidence`.
`source_manifest` MUST be a safe relative path to a source ledger.
`last_updated` MUST be an ISO 8601 calendar date.

A standalone NGF source ledger MUST use `ngf-source-ledger/1.0` and contain
exactly `schema` and `sources`. `sources` MUST be a non-empty array whose
entries use the provenance fields defined by
`schemas/ngf-source-ledger.schema.json`.
The KG-RAG Cookbook MAY instead use its unchanged
`kg-rag-source-ledger/1.0` contract, including `cookbook_version` and its
Cookbook-specific required source inventory.

Every level-two heading MUST begin with exactly one of these classifiers:

- `[Normative]` contains requirements controlled by this document.
- `[Explanatory]` contains sourced facts, interpretation, or examples.
- `[Proposed]` contains designs that have not become requirements or evidence.
- `[Observed]` contains attributable evidence already collected.

Requirements expressed by `MUST`, `MUST NOT`, `SHALL`, `SHALL NOT`, or
`REQUIRED` MUST occur only under `[Normative]` level-two sections. Lower-level
headings inherit the nearest level-two classifier and do not carry an
independent authority class.

Every NGF MUST contain `## [Normative] Proof limits` and
`## [Observed] Change history`. Proof limits MUST state what the document and
its associated artifacts do not establish. Change history MUST identify the
revision and date without turning an intention into an observation.

## Grounding and links

An external-source citation MUST use `[source:<id>]`, where `<id>` resolves to
exactly one entry in `source_manifest`. External addresses and copied source
bodies MUST NOT appear in an NGF. A source-ledger entry MUST distinguish
controlling local sources, external primary sources, and explanatory sources.

Markdown links MUST be relative, remain within the repository, contain no
traversal above the repository root, and resolve to regular files. Fragment
links are permitted only when the target heading exists. An NGF MUST NOT rely
on an external link as a control surface.

Grounding does not change authority. External standards and research support
explanation unless a controlling local contract explicitly adopts a stated
rule. Vendor-authored material remains explanatory even when it describes a
useful implementation pattern.

## Validation

A conforming validator MUST reject unknown frontmatter keys, duplicate keys,
an unclassified level-two heading, an invalid classifier, a requirement keyword
outside a normative section, an unknown source identifier, an unsafe or broken
relative link, an inline external address, or a missing proof-limit or change
history section.

Validation establishes structural conformance only. It MUST NOT claim factual
correctness, source availability beyond the ledger observation, runtime
behavior, result quality, or authority for a protected effect.

The canonical standalone validation interface is:

```sh
python3 scripts/validate_ngf.py --document path/to/document.ngf.md
```

The legacy KG-RAG suite interface remains:

```sh
python3 scripts/validate_ngf.py --check docs/kg-rag
```
