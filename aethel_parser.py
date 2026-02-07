from lark import Lark
from aethel_grammar import aethel_grammar


class AethelParser:
    def __init__(self):
        self.parser = Lark(aethel_grammar, parser='lalr')
    
    def parse(self, code):
        """
        Parse Aethel code and return intents or atomic_batch nodes.
        Returns a dictionary mapping intent names to their structure.
        """
        tree = self.parser.parse(code)
        return self.transform_to_intent_map(tree)
    
    def transform_to_intent_map(self, tree):
        """
        Transform parse tree into intent map.
        Handles both standalone intents and atomic_batch constructs.
        """
        intents = {}
        
        for node in tree.children:
            if node.data == 'intent_def':
                # Regular intent definition
                intent_name = node.children[0].value
                intents[intent_name] = self._extract_intent(node)
            elif node.data == 'atomic_batch':
                # Atomic batch containing multiple intents
                batch_name = node.children[0].value
                # Extract all intents within the batch
                for intent_node in node.children[1:]:
                    if intent_node.data == 'intent_def':
                        intent_name = intent_node.children[0].value
                        intents[intent_name] = self._extract_intent(intent_node)
        
        return intents
    
    def _extract_intent(self, intent_node):
        """Extract intent structure from parse tree node"""
        return {
            "params": self._get_params(intent_node.children[1]),
            "constraints": self._get_conditions(intent_node.children[2]),  # Guard
            "ai_instructions": self._get_settings(intent_node.children[3]),  # Solve
            "post_conditions": self._get_conditions(intent_node.children[4])  # Verify
        }
    
    def _get_params(self, node):
        """Extract parameters from params node"""
        params = []
        for p in node.children:
            # Handle optional 'secret' and 'external' keywords
            param_parts = []
            for child in p.children:
                if hasattr(child, 'value'):
                    param_parts.append(child.value)
            if len(param_parts) >= 2:
                params.append(f"{param_parts[-2]}:{param_parts[-1]}")
        return params
    
    def _get_conditions(self, node):
        """Extract conditions from guard or verify block"""
        conditions = []
        for c in node.children:
            if c.data == 'condition':
                # Build condition string from expression tree
                condition_str = self._expr_to_string(c)
                conditions.append(condition_str)
        return conditions
    
    def _expr_to_string(self, node):
        """Convert expression tree to string"""
        if hasattr(node, 'value'):
            return node.value
        elif node.data == 'condition':
            # condition: expr OPERATOR expr
            left = self._expr_to_string(node.children[0])
            op = node.children[1].value
            right = self._expr_to_string(node.children[2])
            return f"{left} {op} {right}"
        elif node.data in ['add', 'subtract', 'multiply', 'divide', 'modulo']:
            left = self._expr_to_string(node.children[0])
            right = self._expr_to_string(node.children[1])
            ops = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/', 'modulo': '%'}
            return f"{left} {ops[node.data]} {right}"
        elif len(node.children) > 0:
            return self._expr_to_string(node.children[0])
        return str(node)
    
    def _get_settings(self, node):
        """Extract settings from solve block"""
        settings = {}
        for s in node.children:
            if s.data == 'setting':
                key = s.children[0].value
                value = s.children[1].value
                settings[key] = value
        return settings
