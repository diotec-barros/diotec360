'use client';

import { useState, useEffect } from 'react';
import { getExamples, type Example } from '@/lib/api';
import { ChevronDown } from 'lucide-react';

interface ExampleSelectorProps {
  onSelect: (code: string) => void;
}

export default function ExampleSelector({ onSelect }: ExampleSelectorProps) {
  const [examples, setExamples] = useState<Example[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExamples();
  }, []);

  const loadExamples = async () => {
    setLoading(true);
    const data = await getExamples();
    setExamples(data);
    setLoading(false);
  };

  const handleSelect = (example: Example) => {
    onSelect(example.code);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
      >
        <span>Examples</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20 overflow-hidden">
            {loading ? (
              <div className="p-4 text-center text-gray-400">Loading examples...</div>
            ) : examples.length === 0 ? (
              <div className="p-4 text-center text-gray-400">No examples available</div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {examples.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleSelect(example)}
                    className="w-full text-left p-4 hover:bg-gray-700 transition-colors border-b border-gray-700 last:border-b-0"
                  >
                    <div className="font-semibold text-white mb-1">{example.name}</div>
                    <div className="text-sm text-gray-400">{example.description}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
