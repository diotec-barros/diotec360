'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Play, Github, BookOpen } from 'lucide-react';
import { verifyCode, type VerifyResponse } from '@/lib/api';
import ProofViewer from '@/components/ProofViewer';
import ExampleSelector from '@/components/ExampleSelector';

// Dynamically import Editor to avoid SSR issues with Monaco
const Editor = dynamic(() => import('@/components/Editor'), { ssr: false });

const DEFAULT_CODE = `intent transfer(sender: Account, receiver: Account, amount: Balance) {
  guard {
    sender_balance >= amount;
    amount > 0;
  }
  
  verify {
    sender_balance == old_sender_balance - amount;
    receiver_balance == old_receiver_balance + amount;
    total_supply == old_total_supply;
  }
}`;

export default function Home() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerify = async () => {
    setIsVerifying(true);
    setResult(null);
    
    try {
      const response = await verifyCode(code);
      setResult(response);
    } catch (error) {
      setResult({
        status: 'ERROR',
        message: 'Failed to connect to verification service',
      });
    } finally {
      setIsVerifying(false);
    }
  };

  const handleExampleSelect = (exampleCode: string) => {
    setCode(exampleCode);
    setResult(null);
  };

  return (
    <div className="flex flex-col h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#1a1a1a]">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Aethel Studio
            </h1>
            <span className="text-sm text-gray-400">
              Correct-by-Construction Software
            </span>
          </div>
          
          <div className="flex items-center gap-3">
            <ExampleSelector onSelect={handleExampleSelect} />
            
            <button
              onClick={handleVerify}
              disabled={isVerifying}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-semibold"
            >
              <Play className="w-4 h-4" />
              {isVerifying ? 'Verifying...' : 'Verify'}
            </button>

            <a
              href="https://github.com/diotec-barros/aethel-lang"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="View on GitHub"
            >
              <Github className="w-5 h-5" />
            </a>

            <a
              href="https://github.com/diotec-barros/aethel-lang#readme"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Documentation"
            >
              <BookOpen className="w-5 h-5" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor Panel */}
        <div className="flex-1 border-r border-gray-800 flex flex-col">
          <div className="px-4 py-2 bg-[#1a1a1a] border-b border-gray-800">
            <h2 className="text-sm font-semibold text-gray-400">CODE EDITOR</h2>
          </div>
          <div className="flex-1">
            <Editor value={code} onChange={(value) => setCode(value || '')} />
          </div>
        </div>

        {/* Proof Viewer Panel */}
        <div className="flex-1 flex flex-col bg-[#0f0f0f]">
          <div className="px-4 py-2 bg-[#1a1a1a] border-b border-gray-800">
            <h2 className="text-sm font-semibold text-gray-400">PROOF VIEWER</h2>
          </div>
          <div className="flex-1 overflow-auto">
            <ProofViewer result={result} isVerifying={isVerifying} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-[#1a1a1a] px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            Genesis Merkle Root: <span className="font-mono text-blue-400">1e994337bc48d0b2...</span>
          </div>
          <div>
            Powered by Z3 Theorem Prover
          </div>
        </div>
      </footer>
    </div>
  );
}
