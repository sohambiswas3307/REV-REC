"""Suggests an alternative payment method chain when the primary method
keeps failing, based on simple, explainable rules (deterministic — no ML
needed here, since a lookup table is more reliable and auditable than a
model for this sub-problem)."""

FALLBACK_CHAIN = {
    "card": ["upi", "netbanking", "wallet"],
    "netbanking": ["upi", "card"],
    "wallet": ["upi", "card"],
    "upi": ["card", "netbanking"],
}


def next_fallback_method(current_method: str, attempted_methods: list[str]) -> str | None:
    for candidate in FALLBACK_CHAIN.get(current_method, []):
        if candidate not in attempted_methods:
            return candidate
    return None


if __name__ == "__main__":
    print(next_fallback_method("card", ["card"]))
    print(next_fallback_method("card", ["card", "upi"]))
