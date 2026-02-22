#!/usr/bin/env python3
"""Basic example: Verify a Lean proof."""

import asyncio

from axle import AxleClient


async def main() -> None:
    """Demonstrate basic proof verification."""
    # The formal statement (what we want to prove)
    statement = """
import Mathlib

theorem add_comm_example (a b : Nat) : a + b = b + a := by sorry
"""

    # The candidate proof
    proof = """
import Mathlib

theorem add_comm_example (a b : Nat) : a + b = b + a := by
  exact Nat.add_comm a b
"""

    async with AxleClient() as client:
        # Verify the proof
        result = await client.verify_proof(
            formal_statement=statement,
            content=proof,
            environment="lean-4.28.0",
        )

        print(f"Proof valid: {result.okay}")

        if not result.okay:
            print("Errors:")
            for msg in result.tool_messages.errors:
                print(f"  - {msg}")
            for msg in result.lean_messages.errors:
                print(f"  - {msg}")


if __name__ == "__main__":
    asyncio.run(main())
