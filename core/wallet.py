# core/wallet.py

import json
from dataclasses import dataclass
from pathlib import Path

from core.cryptography import generate_key


@dataclass
class Wallet:
    private_key_hex: str
    public_key_hex: str

    @classmethod
    def generate(cls):
        private_key_hex, public_key_hex = generate_key()
        return cls(private_key_hex=private_key_hex, public_key_hex=public_key_hex)

    @classmethod
    def load(cls, path: str):
        wallet_path = Path(path)
        with wallet_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            private_key_hex=data["private_key_hex"],
            public_key_hex=data["public_key_hex"],
        )

    def save(self, path: str):
        wallet_path = Path(path)
        if wallet_path.parent and not wallet_path.parent.exists():
            wallet_path.parent.mkdir(parents=True, exist_ok=True)
        with wallet_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "private_key_hex": self.private_key_hex,
                    "public_key_hex": self.public_key_hex,
                },
                f,
                indent=2,
            )
