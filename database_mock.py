from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Account:
    account_id: str
    balance: float


MOCK_ACCOUNTS: dict[str, Account] = {
    "ACC-77": Account(account_id="ACC-77", balance=5000.0),
    "ACC-88": Account(account_id="ACC-88", balance=1200.0),
}


def get_account_balance(account_id: str) -> float | None:
    account = MOCK_ACCOUNTS.get(account_id)
    return account.balance if account else None
