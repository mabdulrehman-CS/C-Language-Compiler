import re
from errors import LexicalError

KEYWORDS = {'int', 'float', 'if', 'else', 'while', 'printf', 'return', 'include', 'stdio'}

TOKEN_SPECIFICATION = [
    ('INCLUDE',  r'#include'),
    ('STRING',   r'"[^"]*"'),
    ('NUMBER',   r'\d+(\.\d*)?'),
    ('EQ',       r'=='),
    ('NE',       r'!='),
    ('GE',       r'>='),
    ('LE',       r'<='),
    ('ASSIGN',   r'='),
    ('END',      r';'),
    ('COMMA',    r','),
    ('DOT',      r'\.'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('OP',       r'[\+\-\*/%]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

class Lexer:
    def __init__(self, code):
        self.code = code
        self.line_map = {}
        # Pre-calculate line numbers for each character position
        self._build_line_numbers()

    def _build_line_numbers(self):
        self.pos_to_line = {}
        line = 1
        for pos, char in enumerate(self.code):
            self.pos_to_line[pos] = line
            if char == '\n':
                line += 1

    def get_line_at_pos(self, pos):
        if pos < 0:
            return 1
        if pos >= len(self.code):
            return max(self.pos_to_line.values()) if self.pos_to_line else 1
        return self.pos_to_line.get(pos, 1)

    def tokenize(self):
        tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPECIFICATION)
        get_token = re.compile(tok_regex).match
        pos = 0
        tokens = []
        mo = get_token(self.code)
        
        while mo:
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise LexicalError(f"Line {self.get_line_at_pos(pos)}: Unexpected character '{value}'")
            else:
                token_line = self.get_line_at_pos(pos)
                self.line_map[len(tokens)] = token_line
                
                if kind == 'INCLUDE':
                    tokens.append(('INCLUDE', value))
                elif kind == 'STRING':
                    tokens.append(('STRING', value))
                elif kind == 'NUMBER':
                    tokens.append(('NUMBER', value))
                elif kind == 'DOT':
                    tokens.append(('DOT', value))
                elif kind == 'ID':
                    tokens.append(('KEYWORD' if value in KEYWORDS else 'IDENTIFIER', value))
                elif kind in {'ASSIGN','END','COMMA','OP','LPAREN','RPAREN','LBRACE','RBRACE','GT','LT','EQ','NE','GE','LE'}:
                    tokens.append((kind, value))
            
            pos = mo.end()
            mo = get_token(self.code, pos)
        
        self.line_map[len(tokens)] = self.get_line_at_pos(len(self.code) - 1)
        tokens.append(('EOF', None))
        return tokens
