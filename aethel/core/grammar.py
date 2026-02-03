# Gramática Aethel v1.2 - "The Arithmetic Awakening"
# Suporte a: operadores aritméticos, números literais, comentários
aethel_grammar = """
    start: intent_def+
    
    intent_def: "intent" NAME "(" params ")" "{" guard_block solve_block verify_block "}"
    
    params: (param ("," param)*)?
    param: NAME ":" NAME
    
    guard_block: "guard" "{" (condition ";")+ "}"
    solve_block: "solve" "{" (setting ";")+ "}"
    verify_block: "verify" "{" (condition ";")+ "}"
    
    condition: expr OPERATOR expr
    setting: NAME ":" NAME
    
    ?expr: term
         | expr "+" term    -> add
         | expr "-" term    -> subtract
    
    ?term: factor
         | term "*" factor  -> multiply
         | term "/" factor  -> divide
         | term "%" factor  -> modulo
    
    ?factor: atom
           | "(" expr ")"
    
    ?atom: NAME
         | NUMBER
    
    OPERATOR: ">=" | "<=" | "==" | "!=" | ">" | "<"
    NUMBER: /-?[0-9]+/
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\\n]*/
    
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
