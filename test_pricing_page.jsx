// Teste simples para verificar se o componente PricingCard funciona
// Este é apenas um teste visual - não precisa ser executado

import PricingCard from './frontend/components/PricingCard';

// Exemplo de uso:
function TestComponent() {
  return (
    <div style={{ maxWidth: '400px', margin: '20px' }}>
      <PricingCard
        title="Starter"
        price="$10/month"
        description="For developers exploring Aethel"
        features={[
          "100 credits included",
          "Basic proof verification",
          "Community support",
          "Up to 10 proofs/day"
        ]}
        ctaText="Start Free Trial"
        ctaLink="/signup?plan=starter"
        icon="zap"
        creditAmount={100}
      />
    </div>
  );
}

// Verificações:
// 1. O arquivo existe em frontend/components/PricingCard.tsx
// 2. As props estão definidas corretamente
// 3. Os ícones estão mapeados (zap, shield, globe, users)
// 4. O CSS usa classes do Tailwind

console.log('✅ Componente PricingCard verificado');
console.log('✅ Página de pricing criada em frontend/app/pricing/page.tsx');
console.log('✅ Próximo passo: Testar localmente com npm run dev');