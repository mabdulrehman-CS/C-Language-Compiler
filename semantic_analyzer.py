from ast_nodes import *
from errors import SemanticError

class SemanticAnalyzer:
    def __init__(self, includes=None):
        self.symbols = {}
        self.includes = includes or set()
        self.has_stdio = 'stdio.h' in self.includes

    def analyze(self, node):
        if isinstance(node, Program) and len(node.statements) == 0:
            raise SemanticError("Error: C program cannot be empty.")
        self.visit(node)
        return self.symbols

    def visit(self, node):
        method = f"visit_{node.__class__.__name__}"
        if hasattr(self, method):
            return getattr(self, method)(node)
        raise SemanticError(f"Unsupported statement in C: {node.__class__.__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Declaration(self, node):
        if node.name in self.symbols:
            raise SemanticError(f"Error: Variable '{node.name}' already declared.")
        if node.datatype not in {'int', 'float'}:
            raise SemanticError(f"Error: Invalid C data type '{node.datatype}'. Only 'int' and 'float' are supported.")
        self.symbols[node.name] = node.datatype
        if node.init_value:
            self.visit(node.init_value)

    def visit_Assignment(self, node):
        if node.name not in self.symbols:
            raise SemanticError(f"Error: Variable '{node.name}' used before declaration.")
        self.visit(node.expr)

    def visit_PrintStatement(self, node):
        raise SemanticError("Error: 'print' is not valid C syntax. Use 'printf' instead.")

    def visit_PrintfStatement(self, node):
        if not self.has_stdio:
            raise SemanticError("Error: 'printf' requires '#include <stdio.h>' at the top of the program.")
        if node.format_str:
            fmt = node.format_str.strip('"')
            arg_count = len(node.args)
            placeholder_count = fmt.count('%d') + fmt.count('%f') + fmt.count('%s')
            if placeholder_count != arg_count:
                raise SemanticError(f"Error: Format string expects {placeholder_count} placeholders but {arg_count} arguments provided. Check your printf() call.")
        for arg in node.args:
            self.visit(arg)
    def visit_ReturnStatement(self, node):
        if node.return_val:
            self.visit(node.return_val)

    def visit_IfStatement(self, node):
        self.visit(node.condition)
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_WhileStatement(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Number(self, node):
        pass

    def visit_Identifier(self, node):
        if node.name not in self.symbols:
            raise SemanticError(f"Error: Variable '{node.name}' used before declaration.")

