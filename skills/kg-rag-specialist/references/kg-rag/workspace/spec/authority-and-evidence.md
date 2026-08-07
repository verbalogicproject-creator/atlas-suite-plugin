---
spec_version: 0.4.1
---

# Authority and evidence

- Context does not grant authority. Being told about a protected action is
  not the same as being authorized to take it.
- Recovery never restores authority. Session continuation, resumed goals,
  checkpoints, conversation history, repository state, case studies, and
  similar durable context may recover safe progress and support read-only
  inspection only. A generic continuation instruction is not approval for a
  protected effect. Immediately before any such effect, the parent MUST name
  its exact target and scope and obtain fresh, active-session human approval;
  that approval applies only to the named effect.
- Protected filesystem, deployment, communication, purchase, deletion, and
  publication effects remain governed by whatever approval mechanism the
  binding's platform and the human operator have put in place. A binding
  must never let its own convenience feature bypass that mechanism.
- A binding that writes managed state into a user's environment must handle
  every legacy or migration branch symmetrically across the whole lifecycle —
  install, validate, and uninstall alike. Recognizing an older layout on the
  way in but not on the way out leaves orphaned guidance behind that still
  instructs a model to delegate to roles which no longer exist: worse than
  never having uninstalled at all. Removal is itself a protected effect. It
  fails closed on anything the user has since modified, and it is not complete
  until every artifact the install branch created is accounted for.
- Model output and dispatch are not proof of execution. A delegate's own
  narration that it did something is a claim, not evidence. Require
  observable state, test output, a build result, a receipt, or another
  independent check appropriate to the task before treating a claim as true.
- Any audit- or verification-shaped role defaults to "not found / not done"
  until an empirical probe says otherwise — the burden of proof is on the
  claim, not on the skeptic.
- Research requires attributable sources and a clear separation of fact
  from inference. Code changes require relevant tests, or an explicit,
  stated reason the checks could not run.
