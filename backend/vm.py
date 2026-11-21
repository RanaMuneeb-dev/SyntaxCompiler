"""
TAC Virtual Machine / Execution Engine (Phase 5)
Executes Three-Address Code with:
  - Dynamic Variable Environment
  - Control Flow (unconditional goto, conditional if_false)
  - Arithmetic (+, -, *, /, %)
  - Logical Operations (&&, ||, !)
  - Comparisons (==, !=, <, <=, >, >=)
  - Infinite Loop Protection (Max instruction counter)
"""

STRING_PREFIX = "__str__"

COMPARE_OPS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<":  lambda a, b: a <  b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a >  b,
    ">=": lambda a, b: a >= b,
}


def execute_tac(instructions: list) -> list:
    label_map: dict[str, int] = {}
    for i, instr in enumerate(instructions):
        if instr["op"] == "label":
            label_map[instr["result"]] = i

    env: dict = {}
    output: list = []
    pc = 0
    step_count = 0
    MAX_STEPS = 50000

    def resolve(name: str):
        if name is None:
            return None
        if isinstance(name, str) and name.startswith(STRING_PREFIX):
            return name[len(STRING_PREFIX):]
        try:
            return int(name)
        except (ValueError, TypeError):
            pass
        try:
            return float(name)
        except (ValueError, TypeError):
            pass
        if name in env:
            return env[name]
        raise RuntimeError(f"Undefined variable '{name}'")

    def fmt(val):
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        return str(val)

    while pc < len(instructions):
        step_count += 1
        if step_count > MAX_STEPS:
            output.append({
                "type": "error",
                "value": "Runtime error: Maximum instruction limit exceeded (infinite loop protection)",
                "line": pc,
            })
            break

        instr  = instructions[pc]
        result = instr["result"]
        op     = instr["op"]
        arg1   = instr["arg1"]
        arg2   = instr["arg2"]
        pc    += 1

        try:
            if op == "label":
                pass  # no-op

            elif op == "goto":
                if result not in label_map:
                    raise RuntimeError(f"Unknown label '{result}'")
                pc = label_map[result] + 1

            elif op == "if_false":
                val = resolve(arg1)
                if not val:
                    if result not in label_map:
                        raise RuntimeError(f"Unknown label '{result}'")
                    pc = label_map[result] + 1

            elif op == "compare":
                if arg2 and ":" in arg2:
                    cmp_op, right_name = arg2.split(":", 1)
                else:
                    cmp_op, right_name = "==", arg2
                left_val  = resolve(arg1)
                right_val = resolve(right_name)
                fn = COMPARE_OPS.get(cmp_op)
                if fn is None:
                    raise RuntimeError(f"Unknown compare op '{cmp_op}'")
                env[result] = 1 if fn(left_val, right_val) else 0

            elif op == "print":
                val = resolve(arg1)
                output.append({
                    "type":  "print",
                    "value": fmt(val),
                    "line":  pc,
                })

            elif op is None:
                env[result] = resolve(arg1)

            elif op == "+":
                left  = resolve(arg1)
                right = resolve(arg2)
                env[result] = (str(left) + str(right)
                               if isinstance(left, str) or isinstance(right, str)
                               else left + right)

            elif op == "-":
                env[result] = resolve(arg1) - resolve(arg2)

            elif op == "*":
                env[result] = resolve(arg1) * resolve(arg2)

            elif op == "/":
                divisor = resolve(arg2)
                if divisor == 0:
                    raise RuntimeError("Division by zero")
                env[result] = resolve(arg1) / divisor

            elif op == "%":
                divisor = resolve(arg2)
                if divisor == 0:
                    raise RuntimeError("Modulo by zero")
                env[result] = resolve(arg1) % divisor

            elif op == "&&":
                left  = resolve(arg1)
                right = resolve(arg2)
                env[result] = 1 if (left and right) else 0

            elif op == "||":
                left  = resolve(arg1)
                right = resolve(arg2)
                env[result] = 1 if (left or right) else 0

            elif op == "!":
                val = resolve(arg1)
                env[result] = 1 if not val else 0

            else:
                raise RuntimeError(f"Unknown TAC op '{op}'")

        except RuntimeError as e:
            output.append({"type": "error", "value": f"Runtime error: {e}", "line": pc})
            break

    return output
