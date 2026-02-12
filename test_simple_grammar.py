#!/usr/bin/env python3
"""
Teste simples da gramática Aethel.
"""

import sys
import os

# Adicionar caminho
sys.path.append('.')

# Testar importação
try:
    from aethel.core.grammar import aethel_grammar
    print("✅ Gramática importada com sucesso")
    print(f"Tamanho da gramática: {len(aethel_grammar)} caracteres")
except ImportError as e:
    print(f"❌ Erro ao importar gramática: {e}")
    sys.exit(1)

# Testar com Lark diretamente
try:
    from lark import Lark
    
    # Criar parser
    parser = Lark(aethel_grammar, parser='lalr')
    print("✅ Parser Lark criado com sucesso")
    
    # Testar código simples com números
    test_code_1 = """
    intent test() {
        guard {
            amount == 100;
        }
        solve {
            priority: security;
        }
        verify {
            total == amount;
        }
    }
    """
    
    print("\nTeste 1 - Número inteiro simples:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_1)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar código com expressão aritmética
    test_code_2 = """
    intent calculate() {
        guard {
            base == 1000;
            percentage == 15;
        }
        solve {
            target: result;
        }
        verify {
            result == base + (base * percentage / 100);
        }
    }
    """
    
    print("\nTeste 2 - Expressão aritmética:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_2)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar código com número negativo
    test_code_3 = """
    intent negative() {
        guard {
            temperature == -10;
        }
        solve {
            priority: accuracy;
        }
        verify {
            adjusted == temperature + 5;
        }
    }
    """
    
    print("\nTeste 3 - Número negativo:")
    print("-" * 40)
    try:
        tree = parser.parse(test_code_3)
        print("✅ Parse bem-sucedido!")
        print(f"   Árvore: {tree.pretty()[:200]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar o parser Aethel completo
    print("\n\nTestando Parser Aethel completo:")
    print("=" * 50)
    
    try:
        from aethel.core.parser import AethelParser
        aethel_parser = AethelParser()
        print("✅ Parser Aethel criado com sucesso")
        
        # Testar com código simples
        result = aethel_parser.parse(test_code_1)
        print(f"✅ Parse Aethel bem-sucedido!")
        print(f"   Resultado tipo: {type(result)}")
        
        if isinstance(result, dict):
            print(f"   Intents encontrados: {list(result.keys())}")
            for intent_name, intent_data in result.items():
                print(f"   - {intent_name}:")
                print(f"     Parâmetros: {intent_data.get('params', [])}")
                print(f"     Constraints: {len(intent_data.get('constraints', []))}")
                print(f"     Post-conditions: {len(intent_data.get('post_conditions', []))}")
        
    except Exception as e:
        print(f"❌ Erro no Parser Aethel: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTE COMPLETO")
print("=" * 70)