class IRGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, ast):
        self.visit(ast)
        return self.code

    def visit(self, node):
        method = f"visit_{node.__class__.__name__}"
        if hasattr(self, method):
            return getattr(self, method)(node)
        else:
            raise Exception(f"IR: No visitor defined for {node.__class__.__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Declaration(self, node):
        if node.init_value:
            expr_temp = self.visit(node.init_value)
            self.emit(f"{node.name} = {expr_temp}")
        else:
            self.emit(f"# declare {node.datatype} {node.name}")

    def visit_Assignment(self, node):
        expr_temp = self.visit(node.expr)
        self.emit(f"{node.name} = {expr_temp}")

    def visit_PrintStatement(self, node):
        expr_temp = self.visit(node.expr)
        self.emit(f"print {expr_temp}")

    def visit_PrintfStatement(self, node):
        if node.format_str:
            args_temps = [self.visit(arg) for arg in node.args]
            self.emit(f"printf {node.format_str}, {args_temps}")

    def visit_ReturnStatement(self, node):
        if node.return_val:
            ret_temp = self.visit(node.return_val)
            self.emit(f"return {ret_temp}")
        else:
            self.emit("return")

    def visit_IfStatement(self, node):
        cond_temp = self.visit(node.condition)
        label_else = self.new_label()
        label_end = self.new_label()
        
        self.emit(f"if_false {cond_temp} goto {label_else}")
        self.visit(node.then_block)
        self.emit(f"goto {label_end}")
        
        self.emit(f"{label_else}:")
        if node.else_block:
            self.visit(node.else_block)
        
        self.emit(f"{label_end}:")

    def visit_WhileStatement(self, node):
        label_start = self.new_label()
        label_end = self.new_label()
        
        self.emit(f"{label_start}:")
        cond_temp = self.visit(node.condition)
        self.emit(f"if_false {cond_temp} goto {label_end}")
        
        self.visit(node.body)
        self.emit(f"goto {label_start}")
        self.emit(f"{label_end}:")

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.new_temp()

        self.emit(f"{result} = {left} {node.op} {right}")
        return result

    def visit_Number(self, node):
        return str(node.value)

    def visit_Identifier(self, node):
        return node.name
