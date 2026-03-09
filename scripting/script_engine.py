# scripting/script_engine.py


# specifically for handling errors that happen during a script execution
class ScriptError(Exception):
    pass


class ScriptEngine:
    def __init__(self, script: str, context: dict):
        self.script = script
        self.stack = []
        self.context = context

    def execute(self) -> bool:
        # if there isn't a script, just return true
        if not self.script:
            return True

        tokens = self.script.split()
        for token in tokens:
            try:
                # check if it is a number (will error out if it isn't)
                num = int(token)
                self.stack.append(num)
                continue
            except ValueError:
                pass

            # it must be an operation then
            self._handle_operation(token)

        if len(self.stack) == 0:
            return False

        top = self.stack[-1]
        return bool(top)

    def _handle_operation(self, op: str):
        if op == "DUP":
            if not self.stack:
                raise ScriptError("DUP on empty stack.")
            self.stack.append(self.stack[-1])

        elif op == "DROP":
            if not self.stack:
                raise ScriptError("DROP on empty stack.")
            self.stack.pop()

        # syntax is 'a b EQ'
        elif op == "EQ":
            if len(self.stack) < 2:
                raise ScriptError("EQ requires 2 elements.")
            a, b = self.stack.pop(), self.stack.pop()

            if a == b:
                self.stack.append(1)
            else:
                self.stack.append(0)

        # syntax is 'a b LT'
        elif op == "LT":
            if len(self.stack) < 2:
                raise ScriptError("LT requires 2 elements.")
            b, a = self.stack.pop(), self.stack.pop()

            if a < b:
                self.stack.append(1)
            else:
                self.stack.append(0)

        # syntax is 'a b LTE'
        elif op == "LTE":
            if len(self.stack) < 2:
                raise ScriptError("LTE requires 2 elements.")
            b, a = self.stack.pop(), self.stack.pop()

            if a <= b:
                self.stack.append(1)
            else:
                self.stack.append(0)

        # syntax is 'a b GT'
        elif op == "GT":
            if len(self.stack) < 2:
                raise ScriptError("GT requires 2 elements.")
            b, a = self.stack.pop(), self.stack.pop()

            if a > b:
                self.stack.append(1)
            else:
                self.stack.append(0)

        # syntax is 'a b GTE'
        elif op == "GTE":
            if len(self.stack) < 2:
                raise ScriptError("GTE requires 2 elements.")
            b, a = self.stack.pop(), self.stack.pop()

            if a >= b:
                self.stack.append(1)
            else:
                self.stack.append(0)

        elif op == "AND":
            if len(self.stack) < 2:
                raise ScriptError("AND requires 2 elements.")
            a, b = self.stack.pop(), self.stack.pop()

            if bool(a) and bool(b):
                self.stack.append(1)
            else:
                self.stack.append(0)

        elif op == "OR":
            if len(self.stack) < 2:
                raise ScriptError("OR requires 2 elements.")
            a, b = self.stack.pop(), self.stack.pop()

            if bool(a) or bool(b):
                self.stack.append(1)
            else:
                self.stack.append(0)

        elif op == "VERIFY":
            if not self.stack:
                raise ScriptError("VERIFY on empty stack.")
            top = self.stack.pop()
            if not bool(top):
                raise ScriptError("VERIFY failed.")

        elif op == "GETHEIGHT":
            if "height" not in self.context:
                raise ScriptError("height not in execution context.")
            self.stack.append(self.context["height"])

        elif op == "GET_PUSH_RATE":
            if "push_rate" not in self.context:
                raise ScriptError("push_rate not in execution context.")
            self.stack.append(self.context["push_rate"])

        elif op == "GET_PULL_RATE":
            if "pull_rate" not in self.context:
                raise ScriptError("pull_rate not in execution context.")
            self.stack.append(self.context["pull_rate"])

        else:
            raise ScriptError(f"Unknown operation: {op}")
