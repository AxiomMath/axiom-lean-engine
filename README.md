# AXLE

**Ax**iom **L**ean **E**ngine - Python client and CLI for the AXLE Lean verification API.

Homepage: https://axle.axiommath.ai/

## Announcements

<details open>
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

## Documentation

- [Installation Guide](docs/installation.md)
- [Python API Reference](docs/python-api.md)
- [CLI Reference](docs/cli-reference.md)
- [Examples](examples/)
