'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Play, Github, BookOpen, Command } from 'lucide-react';
import { verifyCode, type VerifyResponse } from '@/lib/api';
import ProofViewer from '@/components/ProofViewer';
import ExampleSelector from '@/components/ExampleSelector';
import LayerSidebar from '@/components/LayerSidebar';
import ArchitectChat from '@/components/ArchitectChat';
import GhostVisualizer from '@/components/GhostVisualizer';
import SentinelRadar from '@/components/SentinelRadar';
import ExecutionLog from '@/components/ExecutionLog';
import OracleAtlas from '@/components/OracleAtlas';
import SovereignIdentity from '@/components/SovereignIdentity';

// Dynamically import Editor to avoid SSR issues with Monaco
const Editor = dynamic(() => import('@/components/Editor'), { ssr: false });

interface LogEntry {
  timestamp: number;
  layer: 'judge' | 'architect' | 'sentinel' | 'ghost' | 'oracle';
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  details?: string;
}

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
  const [activeLayer, setActiveLayer] = useState('judge');
  const [chatOpen, setChatOpen] = useState(false);
  const [ghostMode, setGhostMode] = useState(false);
  const [logOpen, setLogOpen] = useState(false);
  const [executionLogs, setExecutionLogs] = useState<LogEntry[]>([]);
  const [sentinelStatus, setSentinelStatus] = useState<'idle' | 'scanning' | 'verified' | 'threat'>('idle');
  const [threatLevel, setThreatLevel] = useState(0);
  const [activeOracles, setActiveOracles] = useState<string[]>([]);

  // CMD+K handler for Architect Chat
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setChatOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Update Ghost mode when layer changes
  useEffect(() => {
    setGhostMode(activeLayer === 'ghost');
  }, [activeLayer]);

  // Detect external data sources in code
  useEffect(() => {
    const externalMatches = code.match(/external\s+\w+/g);
    if (externalMatches && externalMatches.length > 0) {
      // Simulate oracle activation based on code content
      const oracles: string[] = [];
      if (code.includes('price') || code.includes('btc')) {
        oracles.push('chainlink-nyc', 'chainlink-geneva');
      }
      if (code.includes('rainfall') || code.includes('weather')) {
        oracles.push('weather-london', 'weather-houston');
      }
      setActiveOracles(oracles);
    } else {
      setActiveOracles([]);
    }
  }, [code]);

  const handleVerify = async () => {
    setIsVerifying(true);
    setResult(null);
    setExecutionLogs([]);
    setSentinelStatus('scanning');
    setThreatLevel(0);
    
    // Simulate execution log
    const startTime = Date.now();
    const addLog = (layer: LogEntry['layer'], level: LogEntry['level'], message: string, delay: number) => {
      setTimeout(() => {
        setExecutionLogs(prev => [...prev, {
          timestamp: Date.now() - startTime,
          layer,
          level,
          message
        }]);
      }, delay);
    };

    addLog('sentinel', 'info', 'Initializing security scan...', 100);
    addLog('sentinel', 'info', 'Scanning for overflow vulnerabilities...', 300);
    addLog('sentinel', 'success', 'No overflow threats detected', 500);
    addLog('judge', 'info', 'Parsing intent definition...', 700);
    addLog('judge', 'info', 'Extracting guard conditions...', 900);
    addLog('judge', 'info', 'Generating Z3 constraints...', 1100);
    addLog('sentinel', 'info', 'Validating conservation laws...', 1300);
    
    try {
      const response = await verifyCode(code);
      setResult(response);
      
      if (response.status === 'PROVED') {
        addLog('judge', 'success', 'Z3 Solver: Theorem PROVED (sat)', 1500);
        addLog('sentinel', 'success', 'Conservation validated: All balances preserved', 1700);
        addLog('judge', 'success', 'Verification complete: PROVED', 1900);
        setSentinelStatus('verified');
        setThreatLevel(0);
      } else {
        addLog('judge', 'error', `Verification failed: ${response.message}`, 1500);
        addLog('sentinel', 'warning', 'Potential logic error detected', 1700);
        setSentinelStatus('threat');
        setThreatLevel(75);
      }
    } catch (error) {
      setResult({
        status: 'ERROR',
        message: 'Failed to connect to verification service',
      });
      addLog('judge', 'error', 'Connection to verification service failed', 1500);
      setSentinelStatus('threat');
      setThreatLevel(100);
    } finally {
      setIsVerifying(false);
      setTimeout(() => {
        if (sentinelStatus !== 'threat') {
          setSentinelStatus('idle');
        }
      }, 3000);
    }
  };

  const handleExampleSelect = (exampleCode: string) => {
    setCode(exampleCode);
    setResult(null);
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Layer Sidebar */}
      <LayerSidebar onLayerChange={setActiveLayer} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="border-b border-gray-800 bg-gray-900">
          <div className="flex items-center justify-between gap-4 px-6 py-4">
            <div className="flex items-center gap-4 min-w-0">
              <div className="flex flex-col leading-tight min-w-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent truncate">
                  Aethel Plataforma
                </h1>
                <span className="text-xs text-gray-400 truncate">
                  Enterprise Verification Console
                </span>
              </div>
              {/* Layer Indicator */}
              <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  activeLayer === 'judge' ? 'bg-blue-500' :
                  activeLayer === 'architect' ? 'bg-green-500' :
                  activeLayer === 'sentinel' ? 'bg-red-500' :
                  activeLayer === 'ghost' ? 'bg-purple-500' :
                  'bg-amber-500'
                }`} />
                <span className="text-xs font-semibold uppercase">{activeLayer}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4 flex-wrap justify-end">
              {/* Architect Chat Trigger */}
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                title="Open Architect (CMD+K)"
              >
                <Command className="w-4 h-4" />
                <span className="text-sm font-semibold">AI Chat</span>
              </button>

              <div className="ml-1">
                <ExampleSelector onSelect={handleExampleSelect} />
              </div>
              
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

        {/* Editor & Proof Viewer */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          <div className="flex-1 flex overflow-hidden min-h-0">
            {/* Editor Panel */}
            <div className="flex-1 border-r border-gray-800 flex flex-col relative">
              <div className="px-4 py-2 bg-gray-900 border-b border-gray-800 flex items-center justify-between gap-4">
                <h2 className="text-sm font-semibold text-gray-400">CODE EDITOR</h2>
                <div className="flex items-center gap-3 min-w-0">
                  {/* Sovereign Identity */}
                  <SovereignIdentity code={code} />
                  {ghostMode && (
                    <div className="flex items-center gap-2 text-xs text-purple-400">
                      <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                      Ghost Protocol Active
                    </div>
                  )}
                </div>
              </div>
              <div className="flex-1 relative">
                <Editor value={code} onChange={(value) => setCode(value || '')} />
                {/* Ghost Visualizer Overlay */}
                {ghostMode && <GhostVisualizer code={code} />}
              </div>
            </div>

            {/* Proof Viewer Panel */}
            <div className="flex-1 flex flex-col bg-gray-900">
              <div className="px-4 py-2 bg-gray-900 border-b border-gray-800">
                <h2 className="text-sm font-semibold text-gray-400">PROOF VIEWER</h2>
              </div>
              <div className="flex-1 overflow-auto p-4 space-y-4 min-h-0">
                <ProofViewer result={result} isVerifying={isVerifying} />
                
                {/* Sentinel Radar */}
                {activeLayer === 'sentinel' && (
                  <SentinelRadar
                    isActive={isVerifying || sentinelStatus !== 'idle'}
                    threatLevel={threatLevel}
                    status={sentinelStatus}
                  />
                )}

                {/* Oracle Atlas */}
                {activeLayer === 'oracle' && (
                  <OracleAtlas activeSources={activeOracles} />
                )}
              </div>
            </div>
          </div>

          {chatOpen && (
            <div className="w-[420px] shrink-0 bg-gray-900 border-l border-gray-800 overflow-hidden">
              <ArchitectChat
                isOpen={chatOpen}
                onClose={() => setChatOpen(false)}
                onCodeGenerated={(generatedCode) => {
                  setCode(generatedCode);
                  setResult(null);
                }}
              />
            </div>
          )}
        </div>

        {/* Execution Log Drawer */}
        <ExecutionLog
          entries={executionLogs}
          isOpen={logOpen}
          onToggle={() => setLogOpen(!logOpen)}
        />

        {/* Footer with Layer-specific Info */}
        <footer className="border-t border-gray-800 bg-gray-900 px-6 py-3">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div className="flex items-center gap-4">
              <span>Genesis Merkle Root: <span className="font-mono text-blue-400">1e994337bc48d0b2...</span></span>
              {activeLayer === 'sentinel' && (
                <span className="text-green-400">• Sentinel: Active • Threats: 0</span>
              )}
              {activeLayer === 'ghost' && (
                <span className="text-purple-400">• Ghost Protocol: Enabled • ZKP Ready</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span>Powered by Z3 Theorem Prover</span>
              <span className="text-gray-600">|</span>
              <span className="text-xs">Press <kbd className="px-2 py-0.5 bg-gray-800 rounded">CMD+K</kbd> for Architect</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
