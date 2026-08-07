# Claude Code marketplace descriptor

This directory contains a provider-neutral marketplace descriptor for Atlas
Suite Plugin.

The descriptor is intentionally a distribution record, not an installation
receipt. It does not install the plugin, publish it to a hosted marketplace,
enable a connector, require an Anthropic/OpenAI account, or authorize any
protected effect.

Provider-neutral rules:

- no `policy.products` gate;
- no provider-specific runtime field is required to use the skills;
- source points to the public Git repository;
- runtime flags declare no provider account, model provider, or network use at
  skill execution time;
- installation remains an explicit user action in the target host.

Hosts that only accept the canonical local marketplace shape may translate the
git source into a local `source.path` after cloning the repository. That
translation is host-specific and must preserve the same policy and provider
neutrality.
