"""
Recursive Descent Parser for Mini Compiler.
Supports:
  - English & Roman Urdu keywords
  - While loops
  - If / Else branching
  - Logical operators (&&, ||, !)
  - Modulo (%) & Unary operators (-, !)
  - Arithmetic operator precedence
"""

from lexer import (
    Token,
    TT_KEYWORD, TT_IDENT, TT_NUMBER, TT_STRING,
    TT_OP, TT_COMPARE, TT_LOGIC_AND, TT_LOGIC_OR, TT_LOGIC_NOT,
    TT_ASSIGN, TT_SEMI, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE,
    TT_COMMA, TT_EOF,
)
from ast_nodes import (
    ProgramNode, DeclNode, AssignNode, PrintNode, IfNode, WhileNode,
    CompareNode, LogicalOpNode, UnaryOpNode, BinOpNode,
    NumberNode, StringNode, IdentNode,
)


class ParseError(Exception):
    def __init__(self, message, line, col):
        super().__init__(message)
        self.line = line
        self.col = col


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current
        self.pos += 1
        return tok

    def expect(self, ttype: str, canonical_val: str = None) -> Token:
        tok = self.current
        if tok.type != ttype:
            raise ParseError(
                f"Expected {ttype!r} but got {tok.type!r} ({tok.value!r})",
                tok.line, tok.col,
            )
        if canonical_val is not None and getattr(tok, "canonical", tok.value) != canonical_val:
            raise ParseError(
                f"Expected {canonical_val!r} but got {tok.value!r}",
                tok.line, tok.col,
            )
        return self.advance()

    # ── Grammar Rules ────────────────────────────────────────────────────────

    def parse(self) -> ProgramNode:
        program = ProgramNode()
        while self.current.type != TT_EOF:
            program.statements.append(self.statement())
        return program

    def statement(self):
        tok = self.current
        canon = getattr(tok, "canonical", tok.value)

        if tok.type == TT_KEYWORD:
            if canon == "let":
                return self.decl()
            if canon == "print":
                return self.print_stmt()
            if canon == "if":
                return self.if_stmt()
            if canon == "while":
                return self.while_stmt()

        if tok.type == TT_IDENT and self.peek().type == TT_ASSIGN:
            return self.assign()

        raise ParseError(
            f"Unexpected token {tok.value!r} — expected declaration, assignment, 'if', 'while', or 'print'",
            tok.line, tok.col,
        )

    def decl(self) -> DeclNode:
        line = self.current.line
        self.advance()  # 'let' or 'rakho'
        name_tok = self.expect(TT_IDENT)
        self.expect(TT_ASSIGN)
        expr = self.logic_or()
        self.expect(TT_SEMI)
        return DeclNode(name=name_tok.value, expr=expr, line=line)

    def assign(self) -> AssignNode:
        line = self.current.line
        name_tok = self.expect(TT_IDENT)
        self.expect(TT_ASSIGN)
        expr = self.logic_or()
        self.expect(TT_SEMI)
        return AssignNode(name=name_tok.value, expr=expr, line=line)

    def print_stmt(self) -> PrintNode:
        line = self.current.line
        self.advance()  # 'print' or 'dikhao'

        if self.current.type == TT_LPAREN:
            self.advance()
            args = self._arg_list()
            self.expect(TT_RPAREN)
            self.expect(TT_SEMI)
            return PrintNode(args=args, line=line)

        expr = self.logic_or()
        self.expect(TT_SEMI)
        return PrintNode(args=[expr], line=line)

    def if_stmt(self) -> IfNode:
        line = self.current.line
        self.advance()  # 'if' or 'agar'
        self.expect(TT_LPAREN)
        condition = self.logic_or()
        self.expect(TT_RPAREN)

        # then branch
        self.expect(TT_LBRACE)
        then_body = []
        while self.current.type != TT_RBRACE and self.current.type != TT_EOF:
            then_body.append(self.statement())
        self.expect(TT_RBRACE)

        # optional else branch
        else_body = []
        if self.current.type == TT_KEYWORD and getattr(self.current, "canonical", self.current.value) == "else":
            self.advance()  # 'else' or 'warna'
            self.expect(TT_LBRACE)
            while self.current.type != TT_RBRACE and self.current.type != TT_EOF:
                else_body.append(self.statement())
            self.expect(TT_RBRACE)

        return IfNode(condition=condition, then_body=then_body, else_body=else_body, line=line)

    def while_stmt(self) -> WhileNode:
        line = self.current.line
        self.advance()  # 'while' or 'jabtak'
        self.expect(TT_LPAREN)
        condition = self.logic_or()
        self.expect(TT_RPAREN)

        self.expect(TT_LBRACE)
        body = []
        while self.current.type != TT_RBRACE and self.current.type != TT_EOF:
            body.append(self.statement())
        self.expect(TT_RBRACE)

        return WhileNode(condition=condition, body=body, line=line)

    def _arg_list(self) -> list:
        args = [self.logic_or()]
        while self.current.type == TT_COMMA:
            self.advance()
            args.append(self.logic_or())
        return args

    # ── Expressions Precedence ───────────────────────────────────────────────

    def logic_or(self):
        """logic_or → logic_and ( '||' logic_and )*"""
        node = self.logic_and()
        while self.current.type == TT_LOGIC_OR:
            op_tok = self.advance()
            right = self.logic_and()
            node = LogicalOpNode(op="||", left=node, right=right, line=op_tok.line)
        return node

    def logic_and(self):
        """logic_and → logic_not ( '&&' logic_not )*"""
        node = self.logic_not()
        while self.current.type == TT_LOGIC_AND:
            op_tok = self.advance()
            right = self.logic_not()
            node = LogicalOpNode(op="&&", left=node, right=right, line=op_tok.line)
        return node

    def logic_not(self):
        """logic_not → ('!') logic_not | comparison"""
        if self.current.type == TT_LOGIC_NOT:
            op_tok = self.advance()
            operand = self.logic_not()
            return UnaryOpNode(op="!", expr=operand, line=op_tok.line)
        return self.comparison()

    def comparison(self):
        """comparison → expr ( COMPARE expr )?"""
        node = self.expr()
        if self.current.type == TT_COMPARE:
            op_tok = self.advance()
            right = self.expr()
            return CompareNode(op=op_tok.value, left=node, right=right, line=op_tok.line)
        return node

    def expr(self):
        """expr → term (( '+' | '-' ) term)*"""
        node = self.term()
        while self.current.type == TT_OP and self.current.value in ("+", "-"):
            op_tok = self.advance()
            right = self.term()
            node = BinOpNode(op=op_tok.value, left=node, right=right, line=op_tok.line)
        return node

    def term(self):
        """term → factor (( '*' | '/' | '%' ) factor)*"""
        node = self.factor()
        while self.current.type == TT_OP and self.current.value in ("*", "/", "%"):
            op_tok = self.advance()
            right = self.factor()
            node = BinOpNode(op=op_tok.value, left=node, right=right, line=op_tok.line)
        return node

    def factor(self):
        tok = self.current

        # Unary + or -
        if tok.type == TT_OP and tok.value in ("+", "-"):
            op_tok = self.advance()
            operand = self.factor()
            if op_tok.value == "-":
                return UnaryOpNode(op="-", expr=operand, line=op_tok.line)
            return operand

        if tok.type == TT_NUMBER:
            self.advance()
            return NumberNode(value=tok.value, line=tok.line)

        if tok.type == TT_STRING:
            self.advance()
            return StringNode(value=tok.value, line=tok.line)

        if tok.type == TT_IDENT:
            self.advance()
            return IdentNode(name=tok.value, line=tok.line)

        if tok.type == TT_LPAREN:
            self.advance()
            node = self.logic_or()
            self.expect(TT_RPAREN)
            return node

        raise ParseError(
            f"Unexpected token {tok.value!r} in expression",
            tok.line, tok.col,
        )
