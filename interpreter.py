from ast_nodes import *
from errors import RuntimeError

class Interpreter:
    def __init__(self):
        self.env = {}
        self.output = []

    def run(self, node):
        self.visit(node)
        return self.output

    def visit(self, node):
        method = f"visit_{node.__class__.__name__}"
        if hasattr(self, method):
            return getattr(self, method)(node)
        raise RuntimeError(f"No runtime rule for {node.__class__.__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Declaration(self, node):
        if node.init_value:
            self.env[node.name] = self.visit(node.init_value)
        else:
            self.env[node.name] = 0

    def visit_Assignment(self, node):
        value = self.visit(node.expr)
        self.env[node.name] = value

    def visit_PrintStatement(self, node):
        value = self.visit(node.expr)
        self.output.append(value)

    def visit_PrintfStatement(self, node):
        if node.format_str:
            format_str = node.format_str.strip('"')
            # Handle escape sequences
            format_str = format_str.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
            args = [self.visit(arg) for arg in node.args]
            try:
                output = format_str
                for arg in args:
                    output = output.replace('%d', str(arg), 1)
                    output = output.replace('%s', str(arg), 1)
                    output = output.replace('%f', str(float(arg)), 1)
                self.output.append(output)
            except:
                self.output.append(format_str)
        else:
            args = [self.visit(arg) for arg in node.args]
            for arg in args:
                self.output.append(arg)

    def visit_ReturnStatement(self, node):
        pass
    def visit_IfStatement(self, node):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.then_block)
        elif node.else_block:
            self.visit(node.else_block)

    def visit_WhileStatement(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left // right  # integer division
        elif node.op == '%':
            return left % right
        elif node.op == '==':
            return int(left == right)
        elif node.op == '!=':
            return int(left != right)
        elif node.op == '<':
            return int(left < right)
        elif node.op == '<=':
            return int(left <= right)
        elif node.op == '>':
            return int(left > right)
        elif node.op == '>=':
            return int(left >= right)
        else:
            raise RuntimeError(f"Unknown operator {node.op}")

    def visit_Number(self, node):
        return node.value

    def visit_Identifier(self, node):
        if node.name not in self.env:
            raise RuntimeError(f"Variable '{node.name}' not defined")
        return self.env[node.name]
