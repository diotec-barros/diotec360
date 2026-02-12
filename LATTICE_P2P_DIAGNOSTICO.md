# 🔍 DIAGNÓSTICO LATTICE P2P - PROBLEMA IDENTIFICADO

## ❌ PROBLEMA

O `peer_id` retorna `null` porque **o P2P não está sendo inicializado**.

### Evidência nos Logs

```
# logs/nodeA.log - SEM mensagens [LATTICE_P2P]
INFO:     Started server process [12196]
INFO:     Application startup complete.
[MERKLE DB] Initialized at: ...
[VAULT DB] Initialized at: ...
[AUDITOR] Initialized at: ...
# ❌ FALTA: [LATTICE_P2P] started
# ❌ FALTA: [LATTICE_P2P] peer_id=...
```

Se o P2P estivesse funcionando, veríamos:
```
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[LATTICE_P2P] listen=/ip4/127.0.0.1/tcp/9000
```

---

## 🔎 CAUSA RAIZ

O `.bat` define as variáveis de ambiente **ANTES** de iniciar o processo:

```bat
set AETHEL_P2P_ENABLED=true
set AETHEL_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
start "Aethel Node A" cmd /c "python -m uvicorn api.main:app ..."
```

**MAS** o `start` cria um novo processo CMD que **NÃO herda** as variáveis de ambiente do processo pai no Windows.

---

## ✅ SOLUÇÃO

### Opção 1: Usar arquivo `.env` (RECOMENDADO)

O Python pode ler variáveis de um arquivo `.env` usando `python-dotenv`.

**Passo 1:** Criar `.env.nodeA` e `.env.nodeB`

**`.env.nodeA`:**
```env
AETHEL_P2P_ENABLED=true
AETHEL_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
AETHEL_P2P_TOPIC=aethel/lattice/v1
AETHEL_P2P_BOOTSTRAP=
AETHEL_LATTICE_NODES=
AETHEL_STATE_DIR=.aethel_state_nodeA
AETHEL_VAULT_DIR=.aethel_vault_nodeA
AETHEL_SENTINEL_DIR=.aethel_sentinel_nodeA
```

**`.env.nodeB`:**
```env
AETHEL_P2P_ENABLED=true
AETHEL_P2P_LISTEN=/ip4/127.0.0.1/tcp/9001
AETHEL_P2P_TOPIC=aethel/lattice/v1
AETHEL_P2P_BOOTSTRAP=/ip4/127.0.0.1/tcp/9000/p2p/{PEER_ID_DO_NODE_A}
AETHEL_LATTICE_NODES=http://127.0.0.1:8000
AETHEL_STATE_DIR=.aethel_state_nodeB
AETHEL_VAULT_DIR=.aethel_vault_nodeB
AETHEL_SENTINEL_DIR=.aethel_sentinel_nodeB
```

**Passo 2:** Modificar `api/main.py` para carregar `.env`

```python
from dotenv import load_dotenv
import os

# Carregar .env se existir
load_dotenv()
```

**Passo 3:** Modificar `.bat` para usar `--env-file`

```bat
start "Aethel Node A" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --env-file .env.nodeA > logs\nodeA.log 2>&1"
```

---

### Opção 2: Passar variáveis inline (ALTERNATIVA)

Usar `set` dentro do mesmo comando:

```bat
start "Aethel Node A" cmd /c "set AETHEL_P2P_ENABLED=true && set AETHEL_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000 && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 > logs\nodeA.log 2>&1"
```

**Problema:** Linha muito longa e difícil de manter.

---

### Opção 3: Script Python wrapper (MAIS LIMPO)

Criar `start_node.py`:

```python
import os
import sys
import subprocess

def start_node(port, p2p_port, bootstrap=None):
    env = os.environ.copy()
    env['AETHEL_P2P_ENABLED'] = 'true'
    env['AETHEL_P2P_LISTEN'] = f'/ip4/127.0.0.1/tcp/{p2p_port}'
    env['AETHEL_P2P_TOPIC'] = 'aethel/lattice/v1'
    env['AETHEL_P2P_BOOTSTRAP'] = bootstrap or ''
    env['AETHEL_STATE_DIR'] = f'.aethel_state_node{port}'
    env['AETHEL_VAULT_DIR'] = f'.aethel_vault_node{port}'
    env['AETHEL_SENTINEL_DIR'] = f'.aethel_sentinel_node{port}'
    
    subprocess.run([
        'python', '-m', 'uvicorn', 'api.main:app',
        '--host', '127.0.0.1',
        '--port', str(port)
    ], env=env)

if __name__ == '__main__':
    port = int(sys.argv[1])
    p2p_port = int(sys.argv[2])
    bootstrap = sys.argv[3] if len(sys.argv) > 3 else None
    start_node(port, p2p_port, bootstrap)
```

Usar no `.bat`:
```bat
start "Aethel Node A" python start_node.py 8000 9000
```

---

## 🎯 RECOMENDAÇÃO FINAL

**Use a Opção 1 (arquivo `.env`)** porque:
- ✅ Mais limpo e organizado
- ✅ Fácil de editar e versionar
- ✅ Padrão da indústria
- ✅ `python-dotenv` já está instalado

---

## 📝 PRÓXIMOS PASSOS

1. Criar `.env.nodeA` e `.env.nodeB`
2. Modificar `api/main.py` para carregar `.env`
3. Testar com um único nó primeiro
4. Verificar logs para `[LATTICE_P2P] started`
5. Depois iniciar o segundo nó

---

## 🧪 TESTE RÁPIDO

Para testar se o P2P está funcionando:

```cmd
# Terminal 1 - Node A
set AETHEL_P2P_ENABLED=true
set AETHEL_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
set AETHEL_STATE_DIR=.aethel_state_nodeA
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Você deve ver nos logs:
```
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXX...
```

Se não ver, o problema está no código Python, não no `.bat`.
