"""
Test suite for Mini Compiler features:
1. Lexer & Roman Urdu keywords
2. While loop & TAC backward jump
3. Modulo & Logical operators
4. Semantic type checking
5. Optimization (Constant folding & dead branch pruning)
6. Factorial calculation end-to-end
"""

from lexer import tokenize
from parser import Parser
from semantic import SemanticAnalyzer
from optimizer import Optimizer
from tac import TACGenerator
from vm import execute_tac

def test_compiler():
    print("=== TEST 1: Factorial in Roman Urdu with While loop & Comments ===")
    source = """
    // Factorial calculation in Roman Urdu
    rakho n = 5;
    rakho fact = 1;
    /* loop starts here */
    jabtak (n > 1) {
        fact = fact * n;
        n = n - 1;
    }
    dikhao "Factorial result:";
    dikhao fact;
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    sym_table, sem_errors = analyzer.analyze(ast)
    assert not sem_errors, f"Semantic errors: {sem_errors}"

    optimizer = Optimizer()
    opt_ast, opt_stats = optimizer.optimize(ast)
    gen = TACGenerator()
    tac = gen.generate(opt_ast)
    tac_dicts = [t.to_dict() for t in tac]
    output = execute_tac(tac_dicts)
    print("Output:", output)
    assert any(o.get("value") == "120" for o in output), "Factorial 5! should be 120"
    print("PASS: Factorial Roman Urdu passed!\n")

    print("=== TEST 2: Optimization (Constant Folding) ===")
    opt_source = """
    let x = 10 + 20 * 2;
    let y = 100 / 2 - 10;
    if (1) {
        let active = 1;
    } else {
        let dead = 999;
    }
    print x + y;
    """
    toks = tokenize(opt_source)
    ast2 = Parser(toks).parse()
    _, stats = Optimizer().optimize(ast2)
    print("Optimization stats:", stats)
    assert stats["constants_folded"] >= 2, "Should fold constants"
    assert stats["dead_branches_pruned"] >= 1, "Should prune dead else branch"
    print("PASS: Optimization passed!\n")

    print("=== TEST 3: Modulo & Logic Operators (Even / Odd) ===")
    logic_source = """
    let num = 7;
    if (num % 2 == 1 && num > 0) {
        print "Odd and positive";
    }
    """
    toks = tokenize(logic_source)
    ast3 = Parser(toks).parse()
    tac3 = [t.to_dict() for t in TACGenerator().generate(ast3)]
    out3 = execute_tac(tac3)
    print("Output:", out3)
    assert any("Odd and positive" in o.get("value", "") for o in out3)
    print("PASS: Modulo & Logic passed!\n")

    print("=== TEST 4: Semantic Type Error Detection ===")
    bad_source = """
    let text = "hello";
    let bad = text - 5;
    """
    toks = tokenize(bad_source)
    ast4 = Parser(toks).parse()
    _, errors = SemanticAnalyzer().analyze(ast4)
    print("Detected semantic errors:", errors)
    assert len(errors) > 0, "Should catch string subtraction at semantic phase"
    print("PASS: Semantic error checking passed!\n")

    print("ALL TESTS PASSED SUCCESSFULLY! 🚀")

if __name__ == "__main__":
    test_compiler()
