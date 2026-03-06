# core/state.py

from typing import Dict
from core.account import Account

# for the grid address, I took the alphabet number position of the first letter
# in each of our CNETs
GRID_ADDRESS = "0x000000000000000000000000000000034811"

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

    # applies a trade against the grid. push = true (selling) push = false (buying)
    # might convert push into an enum later
    def apply_trade(self, user_address: str, energy_amount: int, settlement_amount: int, push: bool, fee: int, miner_address: str):
        user = self.get_account(user_address)
        grid = self.get_account(GRID_ADDRESS)
        miner = self.get_account(miner_address)
        
        # user is selling energy to the grid
        if push:
            user.energy_wh -= energy_amount
            user.coins_micro += settlement_amount
            grid.energy_wh += energy_amount
            grid.coins_micro -= (settlement_amount + fee)
        else: # user is buying energy from the grid
            user.energy_wh += energy_amount
            user.coins_micro -= (settlement_amount + fee)
            grid.energy_wh -= energy_amount
            grid.coins_micro += settlement_amount
            
        miner.coins_micro += fee
