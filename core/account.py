# core/account.py

class Account:
    def __init__(self, address: str):
        self.address = address
        self.energy_wh = 0
        self.micro_coins = 0
        self.nonce = 0

    def to_dict(self):
        return {
            "address": self.address,
            "energy_wh": self.energy_wh,
            "micro_coins": self.micro_coins,
            "nonce": self.nonce
        }