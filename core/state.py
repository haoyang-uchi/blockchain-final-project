# core/state.py

from typing import Dict
from core.account import Account

# address generated when the grid wallet was created and it's stored in grid_wallet.json
GRID_ADDRESS = "86d7f9a234c7db9475060831b6a5d2a4b0853c7ba3666d93a9a8e4a3a0636e0e233297aba2250a4e5448f580cd8cd922b8445f5e05492beda2c6a2ffbed9496d"


class State:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.active_grid_rate = None

    # fetches an account given an address
    def get_account(self, address: str) -> Account:
        if address not in self.accounts:
            self.accounts[address] = Account(address)
        return self.accounts[address]

    def update_account(
        self, address: str, energy_delta: int, coins_delta: int, nonce: int = None
    ):
        account = self.get_account(address)
        account.energy_wh += energy_delta
        account.micro_coins += coins_delta
        if nonce is not None:
            account.nonce = nonce

    # applies a trade against the grid
    # push = true (selling) push = false (buying)
    def apply_trade(
        self,
        user_address: str,
        energy_amount: int,
        settlement_amount: int,
        push: bool,
        fee: int,
        miner_address: str,
    ):
        user = self.get_account(user_address)
        grid = self.get_account(GRID_ADDRESS)
        miner = self.get_account(miner_address)

        # user is selling energy to the grid
        if push:
            user.energy_wh -= energy_amount
            user.coins_micro += settlement_amount
            grid.energy_wh += energy_amount
            grid.coins_micro -= settlement_amount + fee
        else:  # user is buying energy from the grid
            user.energy_wh += energy_amount
            user.coins_micro -= settlement_amount + fee
            grid.energy_wh -= energy_amount
            grid.coins_micro += settlement_amount

        miner.coins_micro += fee

    def copy(self):
        new_state = State()
        for address, account in self.accounts.items():
            new_acc = Account(address)
            new_acc.energy_wh = account.energy_wh
            new_acc.micro_coins = account.micro_coins
            new_acc.nonce = account.nonce
            new_state.accounts[address] = new_acc
            
        new_state.active_grid_rate = self.active_grid_rate
        return new_state