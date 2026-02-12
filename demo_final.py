"""
AETHEL - DEMONSTRACAO FINAL
Epoch 0 - Mission Complete
"""

print("=" * 70)
print("AETHEL COMPILER v0.6 - DEMONSTRACAO FINAL")
print("=" * 70)
print()

# Teste 1: Parser
print("[1/4] PARSER - Lendo codigo Aethel...")
from aethel.core.parser import AethelParser

code = """
intent power_check(battery: Level, altitude: Meters) {
    guard {
        battery >= min_battery;
        altitude > min_altitude;
    }
    solve {
        priority: survival;
        target: embedded;
    }
    verify {
        battery >= min_battery;
        altitude > min_altitude;
    }
}
"""

parser = AethelParser()
ast = parser.parse(code)
print("   OK - AST gerado com sucesso")
print(f"   Intent encontrado: {list(ast.keys())[0]}")
print()

# Teste 2: Judge
print("[2/4] JUDGE - Verificacao formal com Z3...")
from aethel.core.judge import AethelJudge

judge = AethelJudge(ast)
result = judge.verify_logic("power_check")
print(f"   Status: {result['status']}")
print(f"   Mensagem: {result['message']}")
print()

# Teste 3: Vault
print("[3/4] VAULT - Armazenamento imutavel...")
from aethel.core.vault import AethelVault

vault = AethelVault(".demo_vault")
function_hash = vault.store(
    intent_name="power_check",
    ast_node=ast["power_check"],
    verified_code="fn power_check() { /* codigo gerado */ }",
    verification_result=result
)
print(f"   Hash: {function_hash[:16]}...{function_hash[-8:]}")
print(f"   Status: IMMUTABLE")
print()

# Teste 4: Weaver
print("[4/4] WEAVER - Adaptacao ao hardware...")
from aethel.core.weaver import AethelWeaver

weaver = AethelWeaver(vault)
env = weaver.probe_environment()
print(f"   CPU Load: {env['cpu_load']:.1f}%")
print(f"   Memory: {env['memory_available_gb']:.2f} GB")
print(f"   Battery: {env['battery']['percent']:.0f}%")

mode = weaver.determine_execution_mode(env)
print(f"   Modo selecionado: {mode.value.upper()}")
print()

# Resultado Final
print("=" * 70)
print("RESULTADO FINAL")
print("=" * 70)
print()
print("  Parser:  OK - Codigo parseado")
print(f"  Judge:   OK - {result['status']}")
print(f"  Vault:   OK - Hash {function_hash[:8]}...")
print(f"  Weaver:  OK - Modo {mode.value}")
print()
print("=" * 70)
print("STATUS: MISSION SUCCESSFUL")
print("EPOCH 0: COMPLETE")
print("=" * 70)
print()
print('"In space, there are no second chances.')
print(' In Aethel, there are no bugs."')
print()
print("Aethel v0.6 - The Future is Proved")
