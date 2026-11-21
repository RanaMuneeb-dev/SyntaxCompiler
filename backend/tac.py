"""
Three Address Code (TAC) Generator
Supports:
  - Variable assignments & expressions
  - Print instructions
  - Arithmetic (+, -, *, /, %)
  - Logical operations (&&, ||, !)
  - Conditionals (if / else with labels and conditional jumps)
  - Loops (while with backward jumps)
"""

from ast_nodes import (
    ProgramNode, DeclNode, AssignNode, PrintNode, IfNode, WhileNode,
    CompareNode, LogicalOpNode, UnaryOpNode, BinOpNode,
    NumberNode, StringNode, IdentNode, ASTNode,
)


class TACInstruction:
    def __init__(self, result: str, op: str = None, arg1: str = None, arg2: str = None):
        self.result = result
        self.op     = op
        self.arg1   = arg1
        self.arg2   = arg2

    def __str__(self):
        if self.op == "label":
            return f"{self.result}:"
        if self.op == "goto":
            return f"goto {self.result}"
        if self.op == "if_false":
            return f"if_false {self.arg1} goto {self.result}"
        if self.op == "print":
            return f"print {self.arg1}"
        if self.op == "!":
            return f"{self.result} = !{self.arg1}"
        if self.op == "compare":
            if self.arg2 and ":" in str(self.arg2):
                cmp_op, right_name = self.arg2.split(":", 1)
                return f"{self.result} = {self.arg1} {cmp_op} {right_name}"
            return f"{self.result} = {self.arg1} == {self.arg2}"
        if self.op is None:
            return f"{self.result} = {self.arg1}"
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"

    def to_dict(self):
        return {
            "result": self.result,
            "op":     self.op,
            "arg1":   self.arg1,
            "arg2":   self.arg2,
            "text":   str(self),
        }


class TACGenerator:
    def __init__(self):
        self.instructions: list[TACInstruction] = []
        self._temp_count  = 0
        self._label_count = 0

    def _new_temp(self) -> str:
        self._temp_count += 1
        return f"t{self._temp_count}"

    def _new_label(self, hint: str = "L") -> str:
        self._label_count += 1
        return f"{hint}{self._label_count}"

    def generate(self, program: ProgramNode) -> list[TACInstruction]:
        for stmt in program.statements:
            self._visit(stmt)
        return self.instructions

    def _visit(self, node: ASTNode) -> str:
        method = f"_visit_{type(node).__name__}"
        return getattr(self, method)(node)

    def _visit_DeclNode(self, node: DeclNode):
        result = self._visit(node.expr)
        self.instructions.append(TACInstruction(result=node.name, arg1=result))

    def _visit_AssignNode(self, node: AssignNode):
        result = self._visit(node.expr)
        self.instructions.append(TACInstruction(result=node.name, arg1=result))

    def _visit_PrintNode(self, node: PrintNode):
        for arg in node.args:
            result = self._visit(arg)
            self.instructions.append(TACInstruction(result="_", op="print", arg1=result))

    def _visit_IfNode(self, node: IfNode):
        cond_temp = self._visit(node.condition)
        has_else  = bool(node.else_body)
        l_else    = self._new_label("L_else")
        l_end     = self._new_label("L_end")

        jump_target = l_else if has_else else l_end
        self.instructions.append(
            TACInstruction(result=jump_target, op="if_false", arg1=cond_temp)
        )

        for stmt in node.then_body:
            self._visit(stmt)

        if has_else:
            self.instructions.append(TACInstruction(result=l_end, op="goto"))
            self.instructions.append(TACInstruction(result=l_else, op="label"))
            for stmt in node.else_body:
                self._visit(stmt)

        self.instructions.append(TACInstruction(result=l_end, op="label"))

    def _visit_WhileNode(self, node: WhileNode):
        l_start = self._new_label("L_while_start")
        l_end   = self._new_label("L_while_end")

        # Loop start label
        self.instructions.append(TACInstruction(result=l_start, op="label"))

        # Evaluate condition
        cond_temp = self._visit(node.condition)

        # Check condition -> break to end if false
        self.instructions.append(
            TACInstruction(result=l_end, op="if_false", arg1=cond_temp)
        )

        # Loop body
        for stmt in node.body:
            self._visit(stmt)

        # Loop backward jump
        self.instructions.append(TACInstruction(result=l_start, op="goto"))

        # Loop end label
        self.instructions.append(TACInstruction(result=l_end, op="label"))

    def _visit_CompareNode(self, node: CompareNode) -> str:
        left  = self._visit(node.left)
        right = self._visit(node.right)
        temp  = self._new_temp()
        self.instructions.append(
            TACInstruction(result=temp, op="compare", arg1=left, arg2=f"{node.op}:{right}")
        )
        return temp

    def _visit_LogicalOpNode(self, node: LogicalOpNode) -> str:
        left  = self._visit(node.left)
        right = self._visit(node.right)
        temp  = self._new_temp()
        self.instructions.append(
            TACInstruction(result=temp, op=node.op, arg1=left, arg2=right)
        )
        return temp

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand = self._visit(node.expr)
        temp    = self._new_temp()
        if node.op == "-":
            self.instructions.append(
                TACInstruction(result=temp, op="-", arg1="0", arg2=operand)
            )
        elif node.op == "!":
            self.instructions.append(
                TACInstruction(result=temp, op="!", arg1=operand)
            )
        else:
            return operand
        return temp

    def _visit_BinOpNode(self, node: BinOpNode) -> str:
        left  = self._visit(node.left)
        right = self._visit(node.right)
        temp  = self._new_temp()
        self.instructions.append(
            TACInstruction(result=temp, op=node.op, arg1=left, arg2=right)
        )
        return temp

    def _visit_NumberNode(self, node: NumberNode) -> str:
        temp = self._new_temp()
        self.instructions.append(TACInstruction(result=temp, arg1=str(node.value)))
        return temp

    def _visit_StringNode(self, node: StringNode) -> str:
        temp = self._new_temp()
        self.instructions.append(TACInstruction(result=temp, arg1=f"__str__{node.value}"))
        return temp

    def _visit_IdentNode(self, node: IdentNode) -> str:
        return node.name
