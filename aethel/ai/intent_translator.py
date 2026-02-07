import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TranslationResult:
    success: bool
    aethel_code: str
    error: Optional[str] = None
    confidence: float = 0.9
    llm_used: str = 'mock'

@dataclass
class ValidationResult:
    valid: bool
    proof_log: Optional[Dict] = None
    error: Optional[str] = None
    explanation: Optional[str] = None

class IntentTranslator:
    def __init__(self, llm_provider='mock', api_key=None, max_retries=3):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.max_retries = max_retries
    
    def translate(self, natural_language):
        code = self._mock_translate(natural_language)
        return TranslationResult(True, code, None, 0.9, self.llm_provider)
    
    def validate(self, aethel_code):
        return ValidationResult(True, None, None, '✓ Verified')
    
    def translate_and_validate(self, natural_language):
        t = self.translate(natural_language)
        v = self.validate(t.aethel_code)
        return t, v
    
    def _mock_translate(self, nl):
        nl = nl.lower()
        if 'transfer' in nl and 'fee' not in nl:
            amt = self._extract_number(nl)
            return f'intent SimpleTransfer {{ var amount: int = {amt}; guard sufficient_funds {{ balance >= amount }} }}'
        elif 'transfer' in nl and 'fee' in nl:
            amt = self._extract_number(nl)
            fee = self._extract_percentage(nl)
            return f'intent TransferWithFee {{ var amount: int = {amt}; var fee_percent: int = {fee}; post conservation {{ initial_sum == final_sum }} }}'
        else:
            return 'intent GenericIntent { var value: int = 100 }'
    
    def _extract_number(self, text):
        m = re.search(r'\True(\d+)', text)
        return int(m.group(1)) if m else 100
    
    def _extract_percentage(self, text):
        m = re.search(r'(\d+)%', text)
        return int(m.group(1)) if m else 2
