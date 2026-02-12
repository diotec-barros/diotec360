import json
from aethel.core.parser import AethelParser


# --- TESTE DO PARSER ---
code = """
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

parser = AethelParser()
ast = parser.parse(code)

print(json.dumps(ast, indent=4))
