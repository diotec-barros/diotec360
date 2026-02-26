---
title: Aethel Judge
emoji: ⚖️
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Aethel Judge - Formal Verification System

**Prove your code before you run it.**

Aethel Judge is a formal verification system that uses Z3 theorem prover to mathematically prove the correctness of your code before execution. Write intent-based specifications and get instant mathematical proofs.

## 🚀 Features

- **Formal Verification**: Mathematical proofs using Z3 solver
- **Intent-Based Language**: Declare what you want, not how to do it
- **Conservation Laws**: Automatic verification of invariants (balance conservation, supply constraints)
- **Ghost-Runner**: Zero-latency prediction engine
- **Instant Manifestation**: Preview verified code without deployment

## 📖 Quick Start

### API Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `POST /api/verify` - Verify Aethel code with formal proofs
- `POST /api/compile` - Compile verified code
- `POST /api/execute` - Execute verified code
- `GET /api/examples` - Get example Aethel programs
- `POST /api/ghost/predict` - Ghost-Runner prediction
- `POST /api/mirror/manifest` - Create instant manifestation

### Example: Financial Transfer

```aethel
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > 0;
        old_sender_balance == sender_balance;
        old_receiver_balance == receiver_balance;
        old_total_supply == total_supply;
    }
    
    solve {
        priority: security;
        target: secure_ledger;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
        total_supply == old_total_supply;
    }
}
```

### Verify Code

```bash
curl -X POST https://huggingface.co/spaces/diotec/diotec360-judge/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "intent transfer(...) { ... }"
  }'
```

Response:
```json
{
  "success": true,
  "status": "PROVED",
  "message": "Verified 1 intent(s)",
  "intents": [
    {
      "name": "transfer",
      "status": "PROVED",
      "message": "All constraints satisfied"
    }
  ]
}
```

## 🎯 Use Cases

- **DeFi Protocols**: Prove balance conservation in financial transactions
- **Smart Contracts**: Verify security properties before deployment
- **Critical Systems**: Mathematical guarantees for mission-critical code
- **Token Economics**: Verify supply constraints and minting rules

## 🔬 How It Works

1. **Parse**: Aethel code is parsed into intent specifications
2. **Verify**: Z3 theorem prover checks all constraints
3. **Prove**: Mathematical proof generated for correctness
4. **Execute**: Only proved code can be executed

## 📚 Documentation

- [Full Documentation](https://github.com/diotec/aethel)
- [Whitepaper](https://github.com/diotec/diotec360/blob/main/WHITEPAPER.md)
- [Examples](https://github.com/diotec/diotec360/tree/main/diotec360/examples)

## 🛠️ Technology Stack

- **Z3 Solver**: Microsoft Research theorem prover
- **FastAPI**: High-performance Python web framework
- **Lark**: Parser for Aethel language
- **Docker**: Containerized deployment

## 🌟 Advanced Features

### Ghost-Runner (Epoch 3)
Zero-latency prediction engine that manifests truth by eliminating impossible states.

```bash
curl -X POST https://huggingface.co/spaces/diotec/diotec360-judge/api/ghost/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "..."}'
```

### Mirror Frame (Instant Preview)
Create instant manifestations of verified code without build or deploy.

```bash
curl -X POST https://huggingface.co/spaces/diotec/diotec360-judge/api/mirror/manifest \
  -H "Content-Type: application/json" \
  -d '{"code": "..."}'
```

## 📊 Conservation Laws

Aethel automatically verifies conservation laws:

- **Balance Conservation**: Total supply remains constant in transfers
- **Supply Constraints**: Minting increases supply, burning decreases it
- **State Invariants**: Critical properties maintained across operations

## 🔐 Security

All code is formally verified before execution. The Z3 theorem prover provides mathematical guarantees that:

- No funds can be created or destroyed (except mint/burn)
- All preconditions are satisfied
- All postconditions hold
- State transitions are valid

## 📄 License

MIT License - See [LICENSE](https://github.com/diotec/diotec360/blob/main/LICENSE)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/diotec/diotec360/blob/main/CONTRIBUTING.md)

## 🔗 Links

- [GitHub Repository](https://github.com/diotec/aethel)
- [Aethel Studio](https://diotec360-studio.vercel.app)
- [Documentation](https://github.com/diotec/aethel#readme)

---

Built with ⚡ by the Aethel team
