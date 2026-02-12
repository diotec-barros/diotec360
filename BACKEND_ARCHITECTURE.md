# 🏗️ Arquitetura Backend - Aethel v3.0.3

## 📋 Visão Geral

O Aethel possui **2 backends complementares** com funções distintas:

---

## 1️⃣ API Backend (api/main.py) - SERVIDOR PRINCIPAL

### Função
Servidor FastAPI que expõe todos os serviços do Aethel via REST API.

### Responsabilidades
- ✅ Verificação formal (Z3 Solver)
- ✅ Compilação de código Aethel
- ✅ Execução em WASM Runtime
- ✅ Lattice Sync (P2P + HTTP Fallback)
- ✅ Oracle Integration
- ✅ Ghost-Runner (previsão de estados)
- ✅ Mirror Frame (preview instantâneo)
- ✅ Vault Management
- ✅ Examples API

### Endpoints Principais
```
GET  /                          # Info da API
GET  /health                    # Health check
POST /api/verify                # Verificação formal
POST /api/compile               # Compilação
POST /api/execute               # Execução
GET  /api/vault/list            # Listar funções no vault
GET  /api/examples              # Exemplos de código
POST /api/ghost/predict         # Ghost-Runner prediction
POST /api/mirror/manifest       # Criar manifestação instantânea
GET  /api/lattice/state         # Estado do Lattice
GET  /api/oracle/list           # Listar oracles
```

### Configuração
```bash
# Porta padrão
PORT=8000

# Variáveis de ambiente necessárias
AETHEL_LATTICE_NODES=http://node1:8000,http://node2:8000
AETHEL_P2P_ENABLED=true
AETHEL_P2P_BOOTSTRAP_PEERS=/ip4/...
```

### Como Executar
```bash
# Desenvolvimento
uvicorn api.main:app --reload --port 8000

# Produção
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## 2️⃣ Generator Backend (aethel_generator.py) - FERRAMENTA CLI

### Função
Compilador standalone que transforma código Aethel em Rust verificado.

### Responsabilidades
- ✅ Parse de código Aethel
- ✅ Verificação formal (Judge)
- ✅ Geração de prompts para IA
- ✅ Integração com LLMs (Claude/GPT/Ollama)
- ✅ Criação de artefatos Rust
- ✅ Relatórios de verificação

### Uso
```python
from aethel_generator import AethelGenerator

# Criar gerador
gen = AethelGenerator(
    ai_provider="anthropic",  # ou "openai", "ollama"
    enable_verification=True
)

# Compilar código
result = gen.compile(
    aethel_code=code,
    intent_name="transfer",
    output_file="output.rs"
)

# Resultado
print(result["status"])        # SUCCESS ou FAILED
print(result["artifact"])       # Código Rust gerado
print(result["report"])         # Relatório de verificação
```

### Configuração
```bash
# Chaves de API (escolha uma)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
# Ollama não precisa de chave (local)
```

### Quando Usar
- 🔧 Desenvolvimento de contratos
- 🧪 Testes de compilação
- 📦 Build de artefatos Rust
- 🤖 Experimentação com diferentes LLMs

---

## 🎯 DECISÃO DE ARQUITETURA

### Cenário 1: Produção Web (Aethel Studio)
```
Frontend (Next.js) → API Backend (api/main.py)
                     ↓
                     Lattice Network
```
**Usar**: `api/main.py` como servidor principal

### Cenário 2: Desenvolvimento Local
```
Developer → Generator (aethel_generator.py) → Rust Artifacts
```
**Usar**: `aethel_generator.py` como ferramenta CLI

### Cenário 3: Lattice Triangle (3 Nós)
```
Node 1 (HuggingFace) → api/main.py:8000
Node 2 (Diotec360)   → api/main.py:8001
Node 3 (Backup)      → api/main.py:8002
```
**Usar**: `api/main.py` em cada nó

---

## 📊 Comparação Rápida

| Característica | api/main.py | aethel_generator.py |
|----------------|-------------|---------------------|
| Tipo | Servidor Web | CLI Tool |
| Protocolo | HTTP/REST | Python API |
| Lattice | ✅ Sim | ❌ Não |
| Oracle | ✅ Sim | ❌ Não |
| Ghost-Runner | ✅ Sim | ❌ Não |
| Verificação | ✅ Sim | ✅ Sim |
| Geração IA | ⚠️ Simplificada | ✅ Completa |
| Deploy | Docker/Cloud | Local |

---

## 🚀 Recomendação Final

### Para o Triangle of Truth (Produção)
**USE**: `api/main.py` em todos os 3 nós

### Para Desenvolvimento
**USE**: `aethel_generator.py` para compilar contratos localmente

### Integração
O `api/main.py` pode chamar `aethel_generator.py` internamente quando precisar de geração de código completa com IA.

---

## 📝 Próximos Passos

1. ✅ Definir portas para cada nó do Triangle
2. ✅ Configurar variáveis de ambiente
3. ✅ Testar conectividade Lattice
4. ✅ Deploy dos 3 nós
5. ✅ Ativar sincronização P2P

---

**Versão**: v3.0.3 Hybrid Sync  
**Data**: 2026-02-12  
**Status**: 🟢 Arquitetura Definida
