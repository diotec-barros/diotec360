#!/usr/bin/env python3
"""
Teste de números decimais na gramática Aethel.
"""

import sys
import os

sys.path.append('.')

try:
    from aethel.core.grammar import aethel_grammar
    from lark import Lark
    from aethel.core.parser import AethelParser
    
    print("✅ Módulos importados com sucesso")
    
    # Testar números decimais
    test_cases = [
        {
            "name": "Número decimal simples",
            "code": """
            intent decimal_test() {
                guard {
                    rate == 0.05;
                }
                solve {
                    priority: accuracy;
                }
                verify {
                    result == 100 * rate;
                }
            }
            """
        },
        {
            "name": "Número decimal negativo",
            "code": """
            intent negative_decimal() {
                guard {
                    temperature == -3.14;
                }
                solve {
                    target: measurement;
                }
                verify {
                    adjusted == temperature + 1.5;
                }
            }
            """
        },
        {
            "name": "Expressão com decimais",
            "code": """
            intent complex_decimal() {
                guard {
                    principal == 1000.50;
                    interest_rate == 0.075;
                }
                solve {
                    priority: financial;
                }
                verify {
                    interest == principal * interest_rate;
                    total == principal + interest;
                }
            }
            """
        }
    ]
    
    print("\nTestando gramática atual (sem suporte a decimais):")
    print("=" * 60)
    
    parser = Lark(aethel_grammar, parser='lalr')
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print("-" * 40)
        
        try:
            tree = parser.parse(test['code'])
            print("✅ Parse bem-sucedido (gramática atual)")
        except Exception as e:
            print(f"❌ Erro: {e}")
            print("   (Esperado - gramática atual não suporta decimais)")
    
    # Verificar a regex atual
    print("\n\nAnalisando regex NUMBER atual:")
    print("=" * 60)
    
    # Extrair regex da gramática
    import re
    
    # Encontrar a linha NUMBER na gramática
    lines = aethel_grammar.split('\n')
    for line in lines:
        if 'NUMBER:' in line:
            print(f"Linha encontrada: {line.strip()}")
            # Extrair regex
            match = re.search(r'NUMBER:\s*(/.+?/)', line)
            if match:
                regex = match.group(1)
                print(f"Regex atual: {regex}")
                
                # Testar a regex
                test_numbers = ["0", "100", "-50", "0.05", "-3.14", "1000.50"]
                print("\nTestando regex com números:")
                for num in test_numbers:
                    if re.match(regex[1:-1], num):  # Remover as barras /
                        print(f"  ✅ '{num}' corresponde")
                    else:
                        print(f"  ❌ '{num}' NÃO corresponde")
    
    # Sugerir atualização
    print("\n\nSugestão de atualização:")
    print("=" * 60)
    print("A regex atual: /-?[0-9]+/")
    print("Sugestão: /-?[0-9]+(\\.[0-9]+)?/")
    print("\nIsso permitiria:")
    print("  - Números inteiros: 0, 100, -50")
    print("  - Números decimais: 0.05, -3.14, 1000.50")
    
    # Testar com regex atualizada
    print("\n\nTestando com regex atualizada (simulação):")
    print("=" * 60)
    
    updated_regex = r"-?[0-9]+(\.[0-9]+)?"
    
    test_numbers = ["0", "100", "-50", "0.05", "-3.14", "1000.50", ".5", "100.", "1.2.3"]
    
    for num in test_numbers:
        if re.match(updated_regex + "$", num):
            print(f"  ✅ '{num}' corresponde à regex atualizada")
        else:
            print(f"  ❌ '{num}' NÃO corresponde à regex atualizada")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ANÁLISE COMPLETA")
print("=" * 70)