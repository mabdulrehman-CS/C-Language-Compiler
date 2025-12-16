from ast_nodes import *
from errors import SyntaxError

class Parser:
    def __init__(self, tokens, line_map=None):
        self.tokens = tokens
        self.pos = 0
        self.includes = set()
        self.line_map = line_map or {}

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)

    def get_line(self):
        return self.line_map.get(self.pos, 0)

    def match(self, t):
        tok = self.peek()
        if tok[0] == t or (t == "KEYWORD" and tok[0] == "KEYWORD"):
            self.pos += 1
            return tok
        
        if self.pos > 0:
            line = self.line_map.get(self.pos - 1, self.line_map.get(self.pos, 0))
        else:
            line = self.get_line()
        
        if t == 'END':
            msg = f"Line {line}: Missing semicolon (;) at end of statement"
        elif t == 'LPAREN':
            msg = f"Line {line}: Missing opening parenthesis '('"
        elif t == 'RPAREN':
            msg = f"Line {line}: Missing closing parenthesis ')'"
        elif t == 'LBRACE':
            msg = f"Line {line}: Missing opening brace '{{'"
        elif t == 'RBRACE':
            msg = f"Line {line}: Missing closing brace '}}'"
        elif t == 'IDENTIFIER':
            msg = f"Line {line}: Expected identifier but found {tok[0]}"
        else:
            msg = f"Line {line}: Expected {t} but found {tok[0]}"
        
        raise SyntaxError(msg)

    def accept(self, t, value=None):
        tok = self.peek()
        if tok[0] == t and (value is None or tok[1] == value):
            self.pos += 1
            return tok
        return None
    def parse(self):
        stmts = []
        while self.peek()[0] == 'INCLUDE':
            self.skip_include()
        if self.peek()[0] == 'KEYWORD' and self.peek()[1] == 'int':
            self.pos_save = self.pos
            self.match('KEYWORD')
            if self.peek()[0] == 'IDENTIFIER' and self.peek()[1] == 'main':
                stmts = self.parse_main_function()
            else:
                self.pos = self.pos_save
                while self.peek()[0] != 'EOF':
                    stmts.append(self.statement())
        else:
            while self.peek()[0] != 'EOF':
                stmts.append(self.statement())
        return Program(stmts)

    def skip_include(self):
        self.match('INCLUDE')
        if self.peek()[0] == 'LT':
            self.match('LT')
            include_name = ""
            while self.peek()[0] not in ('GT', 'EOF'):
                include_name += self.peek()[1]
                self.pos += 1
            self.match('GT')
            self.includes.add(include_name.strip())
        elif self.peek()[0] == 'STRING':
            include_name = self.match('STRING')[1].strip('"')
            self.includes.add(include_name)

    def parse_main_function(self):
        self.match('IDENTIFIER')
        self.match('LPAREN')
        self.match('RPAREN')
        self.match('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.statement())
        self.match('RBRACE')
        return stmts

    def statement(self):
        tok_type, tok_val = self.peek()
        if tok_type == 'KEYWORD':
            if tok_val == 'print':
                return self.print_statement()
            elif tok_val == 'printf':
                return self.printf_statement()
            elif tok_val == 'if':
                return self.if_statement()
            elif tok_val == 'while':
                return self.while_statement()
            elif tok_val == 'return':
                return self.return_statement()
            elif tok_val in {'int', 'float'}:
                return self.declaration()
        elif tok_type == 'IDENTIFIER':
            return self.assignment()
        elif tok_type == 'LBRACE':
            return self.block()
        line = self.get_line()
        raise SyntaxError(f"Line {line}: Unexpected token {tok_type} ({tok_val})")

    def declaration(self):
        dtype = self.match('KEYWORD')[1]
        name = self.match('IDENTIFIER')[1]
        init_value = None
        if self.accept('ASSIGN'):
            init_value = self.expr()
        self.match('END')
        return Declaration(dtype, name, init_value)

    def assignment(self):
        name = self.match('IDENTIFIER')[1]
        self.match('ASSIGN')
        expr = self.expr()
        self.match('END')
        return Assignment(name, expr)

    def print_statement(self):
        self.match('KEYWORD')
        self.match('LPAREN')
        expr = self.expr()
        self.match('RPAREN')
        self.match('END')
        return PrintStatement(expr)

    def printf_statement(self):
        self.match('KEYWORD')
        self.match('LPAREN')
        format_str = None
        args = []
        if self.peek()[0] == 'STRING':
            format_str = self.match('STRING')[1]
            if self.peek()[0] == 'COMMA':
                self.match('COMMA')
                args.append(self.expr())
                while self.peek()[0] == 'COMMA':
                    self.match('COMMA')
                    args.append(self.expr())
        else:
            if self.peek()[0] != 'RPAREN':
                args.append(self.expr())
                while self.peek()[0] == 'COMMA':
                    self.match('COMMA')
                    args.append(self.expr())
        self.match('RPAREN')
        self.match('END')
        return PrintfStatement(format_str, args)

    def return_statement(self):
        self.match('KEYWORD')
        return_val = None
        if self.peek()[0] != 'END':
            return_val = self.expr()
        self.match('END')
        return ReturnStatement(return_val)

    def if_statement(self):
        self.match('KEYWORD')
        self.match('LPAREN')
        cond = self.expr()
        self.match('RPAREN')
        then_block = self.block()
        else_block = None
        if self.accept('KEYWORD', 'else'):
            else_block = self.block()
        return IfStatement(cond, then_block, else_block)

    def while_statement(self):
        self.match('KEYWORD')
        self.match('LPAREN')
        cond = self.expr()
        self.match('RPAREN')
        body = self.block()
        return WhileStatement(cond, body)

    def block(self):
        self.match('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.statement())
        self.match('RBRACE')
        return Block(stmts)

    def expr(self):
        node = self.term()
        while self.peek()[0] in ('OP', 'GT', 'LT', 'EQ', 'NE', 'GE', 'LE'):
            op = self.match(self.peek()[0])[1]
            node = BinaryOp(node, op, self.term())
        return node

    def term(self):
        tok_type, tok_val = self.peek()
        if tok_type == 'NUMBER':
            self.match('NUMBER')
            # Handle both int and float numbers
            if '.' in tok_val:
                return Number(float(tok_val))
            else:
                return Number(int(tok_val))
        elif tok_type == 'IDENTIFIER':
            self.match('IDENTIFIER')
            return Identifier(tok_val)
        elif tok_type == 'LPAREN':
            self.match('LPAREN')
            node = self.expr()
            self.match('RPAREN')
            return node
        line = self.get_line()
        raise SyntaxError(f"Line {line}: Unexpected token {tok_type}")