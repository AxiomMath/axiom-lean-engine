# AXLE

**Ax**iom **L**ean **E**ngine - Python client and CLI for the AXLE Lean verification API.

Homepage: https://axle.axiommath.ai/

## Recent Announcements

<details open>
<summary><strong>July 29, 2026 - v1.6.0</strong></summary>

This update ships three sets of features. First, a new tool, [`extract_proof_states`](https://axle.axiommath.ai/v1/docs/tools/extract_proof_states), for proof state analysis in bulk. Second, better support for "find-the-answer"-style problems, e.g. problems where the candidate solution must provide an explicit answer in addition to the formal proof; you can read more about such problems [here](https://axle.axiommath.ai/v1/docs/tools/verify_proof#find-the-answer-problems). Third, various fine-tuned efficiency improvements that customize elaboration to skip unnecessary work. Most users can ignore these settings, but instructions are available on the [troubleshooting page](https://axle.axiommath.ai/v1/docs/troubleshooting/#slow-lean-execution). See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details.

</details>

<details>
<summary><strong>July 15, 2026 - v1.5.0</strong></summary>

New `LeanTimeout`/`LeanResourceExceeded` exceptions, `names`/`indices` selection on `check` and `extract_decls`/`extract_theorems` (to skip elaboration for faster runs), and new fields and options (`unfolded_type_hash`, `verify_negation`, `verbosity`). See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details.

</details>

<details>
<summary><strong>July 1, 2026 - v1.4.0</strong></summary>

This update comes with two notable changes and a variety of additional features:

- **`ignore_imports` now defaults to `true`** — on an import mismatch, AXLE substitutes the default header and reuses the cached environment.
- In turn, **`ignore_imports=false` no longer errors: it now processes your imports as written**. However, note that this is much slower and may cause issues if a dependency is missing. See [Import Mismatches](https://axle.axiommath.ai/v1/docs/troubleshooting/#import-mismatches).
- **Reworked `okay` and `tool_messages`** — `check` now reports `sorry`/axiom/unsafe findings as warnings (not errors), and `repair_proofs` reports failed repairs as errors. See [Interpreting the `okay` field](https://axle.axiommath.ai/v1/docs/troubleshooting/#interpreting-the-okay-field).

Also: opaque support in `merge`/`extract_decls`, a `disprove` fix, and Lean 4.30/4.31. See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for more details.

</details>

<details>
<summary><strong>June 24, 2026 - 📣 AXLE @ ICML 2026</strong></summary>

We're presenting AXLE at the **3rd AI for Math Workshop** at **ICML 2026** in Seoul, as a contributed talk. Come find our poster and say hi! Read the technical report on [arXiv](https://arxiv.org/abs/2606.26442).

</details>

<details>
<summary><strong>June 3, 2026 - v1.3.0</strong></summary>

Support for all declaration kinds, a reworked `repair_proofs`, link shortening, and broader MCP support. See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details and other changes.

### Highlights:
- **All declaration kinds:** A new `theorems_only` option lets most tools select over **every** declaration kind — definitions, opaques, instances, and more — not just theorems and lemmas. Set it to `false` to opt in.
- **Reworked `repair_proofs`:** New passes, stacked repairs, and clearer messages for failed repairs.
- **Tool updates:** Changes and new options for `verify_proof`, `merge`, `extract_decls`, and `sorry2lemma`.
- **Link shortening:** Short, shareable links to requests.
- **MCP web support:** The [`axiom-axle-mcp`](https://pypi.org/project/axiom-axle-mcp/) server now works with Claude web, desktop, and mobile.

</details>

<details>
<summary><strong>April 15, 2026 - v1.2.0</strong></summary>

New `extract_decls` tool for extracting all declaration kinds, and corresponding updates to `extract_theorems`. Users using `extract_theorems` (which will be deprecated in a future update) should migrate to `extract_decls`. See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details.

</details>

<details>
<summary><strong>April 8, 2026 - v1.1.1</strong></summary>

Default option changes, a Lean version bump, and bug fixes.

### Highlights:
- **Default options changed:** `autoImplicit` is now set to `true` by default, matching standard Lean behavior.
- **Lean 4.29.0:** Added the latest stable Lean release.
- **Timeout bug fix:** Fixed a bug where requests were prematurely preempted. Requests now properly max out at the 15-minute maximum timeout.

See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details and other changes.

</details>

[Past announcements](#past-announcements)

## Documentation

- [Installation Guide](docs/installation.md)
- [Python API Reference](docs/python-api.md)
- [CLI Reference](docs/cli-reference.md)
- [Examples](examples/)

## Citing AXLE

To cite AXLE, please cite the [technical report](https://arxiv.org/abs/2606.26442):

```bibtex
@misc{xin2026axle,
  title={AXLE: A Cloud Infrastructure for Lean 4 Theorem Proving Utilities},
  author={Xin, Jimmy and Schneidman, Alex and Cummins, Chris and Ram, Karun and Ganesh, Srihari and Limperg, Jannis},
  year={2026},
  eprint={2606.26442},
  archivePrefix={arXiv},
  primaryClass={cs.LO},
  url={https://arxiv.org/abs/2606.26442},
}
```

## Past Announcements

<details>
<summary><strong>April 1, 2026 - v1.1.0</strong></summary>

🎉 After mass feedback from the public, we're excited to announce that AXLE is switching from Lean to Rocq. The new name will be **AXRE** (Axiom Rocq Engine). All existing Lean proofs will be automatically translated using GPT-2. 🚀

### Notable API changes:
- `document_messages` has been removed from `extract_theorems`. To replicate old behavior, run the `content` field of the resulting documents through the `check` tool.
- Lean messages now include end positions across all tools, changing the format from `-:4:38: ...` to `-:4:38-4:43: ...`.

### Performance improvements:
- Reworked the Lean worker pool for faster responses, no environment warm-up time, and more secure containers.
- Improved the worker scaling pipeline to decrease delays when all worker slots are busy or offline. In the worst case, users should expect no more than a 2-3 minute delay before more worker capacity spins up.

See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details and other changes.

</details>

<details>
<summary><strong>March 11, 2026 - v1.0.1</strong></summary>

New documentation pages, increased rate limits, and bug fixes. See the [changelog](https://axle.axiommath.ai/v1/docs/changelog/) for details.

</details>

<details>
<summary><strong>March 6, 2026</strong></summary>

### Lean Zulip Thread

Join the discussion, ask questions, and share feedback on the [Lean Zulip](https://leanprover.zulipchat.com/#narrow/channel/113486-announce/topic/Axiom.20Lean.20Engine/with/577609358).

### Higher Rate Limits
Rate limits were unintentionally too restrictive:

- API key users: increased to 20 active requests (up from 4)
- Anonymous users: increased to 10 active requests (up from 1)
- Max timeout: increased to 15 minutes (up from 5 minutes)

**Users with an API key should regenerate their key to apply the new limits.**

</details>

<details>
<summary><strong>March 5, 2026 - v1.0.0</strong></summary>

### AXLE Public Release
We're excited to release AXLE to the public! AXLE provides proof verification and manipulation primitives we've used across all of our research efforts, including training AI models and AxiomProver's 12/12 on Putnam 2025.

[Playground](https://axle.axiommath.ai) | [API docs](https://axle.axiommath.ai/v1/docs/) | [Why we built AXLE](https://axiommath.ai/territory/releasing-axle) | [Request more capacity](https://forms.gle/CdLKu45tEsRXtFQ29) | axle@axiommath.ai

</details>
