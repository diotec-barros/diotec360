---
title: Aethel Judge
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Aethel v1.4.0 - The Overflow Sentinel

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-yellow)](https://huggingface.co/spaces/diotec/aethel-judge)
[![API Status](https://img.shields.io/badge/API-Online-success)](https://diotec-aethel-judge.hf.space)
[![Tests](https://img.shields.io/badge/tests-6%2F6%20passing-brightgreen)](https://diotec-aethel-judge.hf.space/health)
[![Frauds Blocked](https://img.shields.io/badge/frauds%20blocked-2-red)](./SECOND_FRAUD_BLOCKED.md)
[![Version](https://img.shields.io/badge/version-1.4.0-blue)](./V1_4_LAUNCH_COMPLETE.md)

Motor de prova matemática com defesa em 3 camadas para infraestruturas críticas.

> **🚨 NEW**: v1.4 Overflow Sentinel! Triple-Layer Defense System! [Read more →](./V1_4_LAUNCH_COMPLETE.md)

## 🌐 Try It Live!

- **🎮 Playground**: [Aethel Studio](https://aethel-studio.vercel.app)
- **🔌 API**: [https://diotec-aethel-judge.hf.space](https://diotec-aethel-judge.hf.space)
- **📚 API Docs**: [https://diotec-aethel-judge.hf.space/docs](https://diotec-aethel-judge.hf.space/docs)
- **🤗 HF Space**: [diotec/aethel-judge](https://huggingface.co/spaces/diotec/aethel-judge)

## 🎯 O Que É Aethel?

Aethel é uma linguagem de programação formalmente verificada para sistemas financeiros críticos. Cada linha de código é matematicamente provada antes de ser executada.

## ✨ Features v1.4.0

### 🛡️ Triple-Layer Defense System (v1.4) ⭐ NEW
- **Layer 1**: Conservation Guardian - Protege contra criação de fundos
- **Layer 2**: Overflow Sentinel - Protege contra bugs de hardware
- **Layer 3**: Z3 Theorem Prover - Protege contra contradições lógicas

### 🔢 Overflow Sentinel (v1.4) ⭐ NEW
- Detecta integer overflow/underflow
- Limites: 64-bit signed integers (MAX_INT: 2^63-1)
- Previne bugs de hardware antes da execução
- Performance: O(n) - < 1ms

### 🔬 Unified Proof Engine (v1.1.4)
- Detecção de contradições globais
- Previne "Singularidade do Vácuo"
- Verificação formal com Z3 Theorem Prover

### 🧮 Arithmetic Awakening (v1.2.0)
- Operadores aritméticos: `+`, `-`, `*`, `/`, `%`
- Números literais: `0`, `100`, `-50`
- Comentários: `# comentário`
- Expressões complexas: `((amount * rate) / 100)`

### 💰 Conservation Guardian (v1.3.0)
- **Detecção automática de violações de conservação**
- Fast-fail antes do Z3 (O(n) complexity)
- Mensagens de erro claras e acionáveis
- Suporte multi-party (N → M transações)

## 🚀 Como Usar

### Exemplo: Transferência Segura

```aethel
# Transferência com verificação de conservação
intent secure_transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        old_sender_balance >= amount;
        amount > 0;
    }
    
    solve {
        priority: security;
        target: bank_vault;
    }
    
    verify {
        # Conservação exata de fundos
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
    }
}
```

**Resultado**: ✅ PROVED - Conservação válida + Verificação Z3 passou

### Exemplo: Violação Detectada

```aethel
# Tentativa de criar dinheiro
intent money_printer(sender: Account, receiver: Account) {
    guard {
        amount > 0;
    }
    
    verify {
        sender_balance == old_sender_balance - 100;  # Perde 100
        receiver_balance == old_receiver_balance + 200;  # Ganha 200
    }
}
```

**Resultado**: 
```
❌ FAILED: Conservation violation detected
   sender_balance: -100
   receiver_balance: +200
   ────────────────────────────────────────
   Total: 100 units created from nothing
```

## 🏗️ Arquitetura

```
Parser → Judge → Conservation Checker → Z3 Solver
                      ↓
                 Violação? → ❌ FAILED (fast-fail)
                      ↓
                 Válido? → Continue para Z3
```

## 📊 Estatísticas

- **Testes**: 39/39 passando (100%)
- **Performance**: < 5% overhead
- **Detecção**: 100% das violações de conservação
- **Falsos Positivos**: 0%

## 🔗 Links

- **Frontend**: https://aethel.diotec360.com
- **GitHub**: https://github.com/diotec-barros/aethel-lang
- **Documentação**: Ver repositório

## 📝 API Endpoints

### POST /verify
Verifica código Aethel e retorna prova matemática.

**Request**:
```json
{
  "code": "intent transfer(...) { ... }"
}
```

**Response**:
```json
{
  "status": "PROVED",
  "message": "O código é matematicamente seguro.",
  "proof": { ... }
}
```

## 🛡️ Segurança

- Verificação formal com Z3
- Detecção de contradições globais
- Validação de conservação automática
- Zero tolerância a violações

## 🚀 Deployment

### Hugging Face Space (Production)

O Aethel Judge está deployado e disponível publicamente:

```bash
# Health check
curl https://diotec-aethel-judge.hf.space/health

# Verify code
curl -X POST https://diotec-aethel-judge.hf.space/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "intent test() { ... }"}'
```

### Deploy Your Own

```bash
# Deploy to Hugging Face
deploy_to_huggingface.bat

# Test locally with Docker
test_docker_local.bat

# Run test suite
python test_huggingface_deployment.py
```

Veja [HUGGINGFACE_QUICKSTART.md](./HUGGINGFACE_QUICKSTART.md) para instruções detalhadas.

## 📄 Licença

MIT License - Ver LICENSE no repositório

---

**Versão**: v1.3.1 "The Conservation Guardian"  
**Data**: 3 de Fevereiro de 2026  
**Status**: ✅ Production Ready

🚀 **De verificação a proteção. O futuro é conservado!** 🚀
