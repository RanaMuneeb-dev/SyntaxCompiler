import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

from lexer import tokenize, LexerError
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
from optimizer import Optimizer
from tac import TACGenerator
from vm import execute_tac


def compile_source(source: str) -> dict:
    result = {
        "success": False,
        "tokens": [],
        "ast": None,
        "symbol_table": [],
        "semantic_errors": [],
        "tac": [],
        "optimized_tac": [],
        "optimization_stats": {
            "constants_folded": 0,
            "dead_branches_pruned": 0,
            "total_optimizations": 0,
            "log": [],
        },
        "output": [],
        "error": None,
    }

    # Phase 1: Lexer
    try:
        tokens = tokenize(source)
        result["tokens"] = [
            {"type": t.type, "value": t.value, "line": t.line, "col": t.col}
            for t in tokens if t.type != "EOF"
        ]
    except LexerError as e:
        result["error"] = {"phase": "Lexer", "message": str(e), "line": e.line, "col": e.col}
        return result

    # Phase 2: Parser
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        result["ast"] = ast.to_dict()
    except ParseError as e:
        result["error"] = {"phase": "Parser", "message": str(e), "line": e.line, "col": e.col}
        return result

    # Phase 3: Semantic Analyzer
    analyzer = SemanticAnalyzer()
    symbol_table, semantic_errors = analyzer.analyze(ast)
    result["symbol_table"] = symbol_table.to_list()
    result["semantic_errors"] = semantic_errors

    # Phase 4: TAC Generation (Raw)
    if not semantic_errors:
        gen = TACGenerator()
        raw_instructions = gen.generate(ast)
        result["tac"] = [i.to_dict() for i in raw_instructions]

        # Phase 4.5: Compiler Optimization (Constant Folding & Dead Branch Pruning)
        optimizer = Optimizer()
        opt_ast, opt_stats = optimizer.optimize(ast)
        result["optimization_stats"] = opt_stats

        opt_gen = TACGenerator()
        opt_instructions = opt_gen.generate(opt_ast)
        result["optimized_tac"] = [i.to_dict() for i in opt_instructions]

        result["success"] = True

        # Phase 5: Execute in VM
        result["output"] = execute_tac(result["optimized_tac"])
    else:
        result["success"] = False

    return result


class CompilerHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Mini Compiler API is running"}).encode("utf-8"))

    def do_POST(self):
        if self.path in ("/compile", "/compile/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                source = data.get("source", "")
                res_dict = compile_source(source)
                res_bytes = json.dumps(res_dict).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(res_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()


# Optional FastAPI compatibility if needed
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(title="Mini Compiler API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class CompileRequest(BaseModel):
        source: str

    @app.post("/compile")
    def compile_endpoint(req: CompileRequest):
        return compile_source(req.source)

    @app.get("/")
    def root_endpoint():
        return {"message": "Mini Compiler API is running"}
except Exception:
    app = None


def run_server(port=8000):
    server = HTTPServer(("0.0.0.0", port), CompilerHTTPHandler)
    print(f"Mini Compiler Server running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
