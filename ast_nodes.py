class Program:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Program({self.statements})"

class Block:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class Declaration:
    def __init__(self, datatype, name, init_value=None):
        self.datatype = datatype
        self.name = name
        self.init_value = init_value
    def __repr__(self):
        return f"Declaration({self.datatype}, {self.name}, {self.init_value})"

class Assignment:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def __repr__(self):
        return f"Assignment({self.name}, {self.expr})"

class PrintStatement:
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"Print({self.expr})"

class PrintfStatement:
    def __init__(self, format_str, args):
        self.format_str = format_str
        self.args = args
    def __repr__(self):
        return f"Printf({self.format_str}, {self.args})"

class ReturnStatement:
    def __init__(self, return_val=None):
        self.return_val = return_val
    def __repr__(self):
        return f"Return({self.return_val})"

class IfStatement:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    def __repr__(self):
        return f"If({self.condition}, {self.then_block}, {self.else_block})"

class WhileStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"While({self.condition}, {self.body})"

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class Number:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)

class Identifier:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
