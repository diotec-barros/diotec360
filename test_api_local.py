#!/usr/bin/env python3
"""
Script para testar a API localmente antes do deploy
"""

import requests
import json
import sys

# URL da API (mude para a URL do Railway depois do deploy)
API_URL = "http://localhost:8000"

def test_health():
    """Testa endpoint de saúde"""
    print("\n🔍 Testando /health...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passou!")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def test_root():
    """Testa endpoint raiz"""
    print("\n🔍 Testando /...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passou!")
            data = response.json()
            print(f"   Nome: {data.get('name')}")
            print(f"   Versão: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Root endpoint falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def test_examples():
    """Testa endpoint de exemplos"""
    print("\n🔍 Testando /api/examples...")
    try:
        response = requests.get(f"{API_URL}/api/examples")
        if response.status_code == 200:
            data = response.json()
            print("✅ Examples endpoint passou!")
            print(f"   Total de exemplos: {data.get('count')}")
            for example in data.get('examples', []):
                print(f"   - {example.get('name')}")
            return True
        else:
            print(f"❌ Examples endpoint falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def test_verify():
    """Testa endpoint de verificação"""
    print("\n🔍 Testando /api/verify...")
    
    test_code = """intent test() {
    guard {
        true;
    }
    verify {
        true;
    }
}"""
    
    try:
        response = requests.post(
            f"{API_URL}/api/verify",
            json={"code": test_code},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Verify endpoint passou!")
            print(f"   Status: {data.get('status')}")
            print(f"   Sucesso: {data.get('success')}")
            print(f"   Mensagem: {data.get('message')}")
            return True
        else:
            print(f"❌ Verify endpoint falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def test_vault_list():
    """Testa endpoint de listagem do vault"""
    print("\n🔍 Testando /api/vault/list...")
    try:
        response = requests.get(f"{API_URL}/api/vault/list")
        if response.status_code == 200:
            data = response.json()
            print("✅ Vault list endpoint passou!")
            print(f"   Total de funções: {data.get('count')}")
            return True
        else:
            print(f"❌ Vault list endpoint falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTANDO API AETHEL LOCALMENTE")
    print("=" * 60)
    print(f"\n📍 URL: {API_URL}")
    print("\n⚠️  Certifique-se que a API está rodando:")
    print("   cd api && uvicorn main:app --reload")
    print("\n" + "=" * 60)
    
    results = []
    
    # Executar testes
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Examples", test_examples()))
    results.append(("Verify", test_verify()))
    results.append(("Vault List", test_vault_list()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Total: {passed} passaram, {failed} falharam")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ API está pronta para deploy no Railway!")
        return 0
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("❌ Corrija os erros antes de fazer deploy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
