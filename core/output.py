# core/output.py


class Output:
    def __init__(self, value: int, script: str):
        # shard = 1 / 1000 PolyGlass
        self.value = value
        self.script = script
