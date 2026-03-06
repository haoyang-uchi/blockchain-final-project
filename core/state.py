# core/state.py

from typing import Dict
from core.account import Account

class State:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    # fetches an account given an address
    def get_account(self, address: str) -> Account:
        if address not in self.accounts:
            self.accounts[address] = Account(address)
        return self.accounts[address]

    def update_account(self, address: str, energy_delta: int, coins_delta: int, nonce: int = None):
        account = self.get_account(address)
        account.energy_wh += energy_delta
        account.micro_coins += coins_delta
        if nonce is not None:
            account.nonce = nonce
