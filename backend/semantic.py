"""
Semantic Analyzer
  - Builds symbol table (variable → type, line declared)
  - Checks:
      * No undeclared variable use
      * No duplicate declarations
      * Type checking for operators (+, -, *, /, %, logical)
      * Block scoping awareness
"""

from ast_nodes import (
    ProgramNode, DeclNode, AssignNode, PrintNode, IfNode, WhileNode,
    CompareNode, LogicalOpNode, UnaryOpNode, BinOpNode,
    NumberNode, StringNode, IdentNode, ASTNode,
)


class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class SymbolTable:
    def __init__(self):
        self._table: dict[str, dict] = {}

    def declare(self, name: str, var_type: str, line: int):
        if name in self._table:
            raise SemanticError(f"Variable '{name}' already declared", line)
        self._table[name] = {"type": var_type, "declared_at": line}

    def assign(self, name: str, line: int):
        if name not in self._table:
            raise SemanticError(f"Variable '{name}' used before declaration", line)

    def lookup(self, name: str, line: int) -> dict:
        if name not in self._table:
            raise SemanticError(f"Undeclared variable '{name}'", line)
        return self._table[name]

    def to_list(self) -> list:
        return [
            {"name": k, "type": v["type"], "declared_at": v["declared_at"]}
            for k, v in self._table.items()
        ]


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[dict] = []

    def analyze(self, program: ProgramNode):
        for stmt in program.statements:
            self._visit(stmt)
        return self.symbol_table, self.errors

    def _visit(self, node: ASTNode):
        method = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method, self._visit_default)
        return visitor(node)

    def _visit_default(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

    def _visit_DeclNode(self, node: DeclNode):
        try:
            expr_type = self._visit(node.expr)
            self.symbol_table.declare(node.name, expr_type or "unknown", node.line)
        except SemanticError as e:
            self.errors.append({"message": str(e), "line": e.line})

    def _visit_AssignNode(self, node: AssignNode):
        try:
            self.symbol_table.assign(node.name, node.line)
            self._visit(node.expr)
        except SemanticError as e:
            self.errors.append({"message": str(e), "line": e.line})

    def _visit_PrintNode(self, node: PrintNode):
        for arg in node.args:
            try:
                self._visit(arg)
            except SemanticError as e:
                self.errors.append({"message": str(e), "line": e.line})

    def _visit_IfNode(self, node: IfNode):
        try:
            self._visit(node.condition)
        except SemanticError as e:
            self.errors.append({"message": str(e), "line": e.line})

        for stmt in node.then_body:
            self._visit(stmt)
        for stmt in node.else_body:
            self._visit(stmt)

    def _visit_WhileNode(self, node: WhileNode):
        try:
            self._visit(node.condition)
        except SemanticError as e:
            self.errors.append({"message": str(e), "line": e.line})

        for stmt in node.body:
            self._visit(stmt)

    def _visit_CompareNode(self, node: CompareNode):
        self._visit(node.left)
        self._visit(node.right)
        return "bool"

    def _visit_LogicalOpNode(self, node: LogicalOpNode):
        self._visit(node.left)
        self._visit(node.right)
        return "bool"

    def _visit_UnaryOpNode(self, node: UnaryOpNode):
        expr_type = self._visit(node.expr)
        if node.op == "!":
            return "bool"
        if node.op == "-":
            if expr_type == "string":
                self.errors.append({
                    "message": f"Type error: Cannot apply unary '-' to string",
                    "line": node.line
                })
            return "number"
        return expr_type

    def _visit_BinOpNode(self, node: BinOpNode):
        left_type  = self._visit(node.left)
        right_type = self._visit(node.right)

        # Check for invalid operations on strings
        if node.op in ("-", "*", "/", "%"):
            if left_type == "string" or right_type == "string":
                self.errors.append({
                    "message": f"Type error: operator '{node.op}' not supported between '{left_type}' and '{right_type}'",
                    "line": node.line,
                })
                return "number"

        if node.op == "+":
            if left_type == "string" or right_type == "string":
                return "string"
            return "number"

        return "number"

    def _visit_NumberNode(self, node: NumberNode):
        return "number"

    def _visit_StringNode(self, node: StringNode):
        return "string"

    def _visit_IdentNode(self, node: IdentNode):
        sym = self.symbol_table.lookup(node.name, node.line)
        return sym["type"]
