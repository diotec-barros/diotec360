"""
Teste mínimo do WhatsApp Gate
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Teste básico de importação
print("🧪 Testando importações básicas...")

try:
    # Testa se podemos importar as classes básicas
    from aethel.core.whatsapp_gate import WhatsAppMessage, WhatsAppResponse
    
    print("✅ WhatsAppMessage importada com sucesso")
    print("✅ WhatsAppResponse importada com sucesso")
    
    # Testa criação de mensagem
    message = WhatsAppMessage(
        message_id="test_123",
        sender_id="user_456",
        timestamp=1234567890.0,
        content="Teste de mensagem",
        message_type="text"
    )
    
    print(f"✅ Mensagem criada: {message.message_id}")
    print(f"   Remetente: {message.sender_id}")
    print(f"   Conteúdo: {message.content}")
    
    # Testa criação de resposta
    response = WhatsAppResponse(
        response_id="resp_123",
        original_message_id="test_123",
        timestamp=1234567891.0,
        content="Resposta de teste",
        response_type="text"
    )
    
    print(f"✅ Resposta criada: {response.response_id}")
    print(f"   Tipo: {response.response_type}")
    print(f"   Conteúdo: {response.content}")
    
    print("\n🎯 Testes básicos passaram!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ TESTE MÍNIMO CONCLUÍDO COM SUCESSO")
print("="*60)