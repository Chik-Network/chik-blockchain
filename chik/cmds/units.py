from __future__ import annotations

# The rest of the codebase uses mojos everywhere.
# Only use these units for user facing interfaces.
units: dict[str, int] = {
    "chik": 10**12,  # 1 chik (XCK) is 1,000,000,000,000 mojo (1 trillion)
    "mojo": 1,
    "cat": 10**3,  # 1 CAT is 1000 CAT mojos
}
