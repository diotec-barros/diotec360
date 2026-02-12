from aethel.core.parser import AethelParser
from aethel.core.judge import AethelJudge


# Teste 1: Código SEGURO (deve passar)
safe_code = """
intent transfer_funds(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
    }
}
"""

# Teste 2: Código INSEGURO (deve falhar)
unsafe_code = """
intent unsafe_transfer(sender: Account, receiver: Account, amount: Gold) {
    guard {
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance >= 0;
        amount > 1000;
        amount < 0;
    }
}
"""

print("="*70)
print("TESTE 1: Código Seguro (deve passar)")
print("="*70)

parser = AethelParser()
ast = parser.parse(safe_code)
judge = AethelJudge(ast)

result = judge.verify_logic("transfer_funds")
report = judge.generate_proof_report("transfer_funds", result)
print(report)

print("\n" + "="*70)
print("TESTE 2: Código Inseguro (deve falhar)")
print("="*70)

ast2 = parser.parse(unsafe_code)
judge2 = AethelJudge(ast2)

result2 = judge2.verify_logic("unsafe_transfer")
report2 = judge2.generate_proof_report("unsafe_transfer", result2)
print(report2)
