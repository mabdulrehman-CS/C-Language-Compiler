from ast_nodes import *

class Optimizer:
    def __init__(self):
        self.optimized_code = []
    
    def optimize_ir(self, ir_code):
        self.optimized_code = []
        
        ir_code = self._constant_folding(ir_code)
        ir_code = self._constant_propagation(ir_code)
        ir_code = self._dead_code_elimination(ir_code)
        
        return ir_code
    
    def _constant_propagation(self, ir_code):
        # Build a map of variable -> constant value
        const_map = {}
        for instruction in ir_code:
            if '=' in instruction and not instruction.startswith('if') and not instruction.startswith('goto'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value = parts[1].strip()
                    try:
                        const_map[var_name] = int(value)
                    except:
                        try:
                            const_map[var_name] = float(value)
                        except:
                            pass
        
        # Replace variable references in printf with constant values
        optimized = []
        for instruction in ir_code:
            if 'printf' in instruction:
                # Replace variables in printf arguments with their constant values
                new_instruction = instruction
                for var, val in const_map.items():
                    # Replace ['var'] with [val]
                    new_instruction = new_instruction.replace(f"['{var}']", f"[{val}]")
                    new_instruction = new_instruction.replace(f"'{var}'", f"{val}")
                optimized.append(new_instruction)
            else:
                optimized.append(instruction)
        
        return optimized
    
    def _constant_folding(self, ir_code):
        optimized = []
        temp_values = {}
        
        for instruction in ir_code:
            if '=' in instruction and not instruction.startswith('if') and not instruction.startswith('goto'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expr = parts[1].strip()
                    
                    try:
                        result = self._evaluate_constant_expr(expr, temp_values)
                        if result is not None:
                            optimized.append(f"{var_name} = {result}")
                            temp_values[var_name] = result
                        else:
                            optimized.append(instruction)
                    except:
                        optimized.append(instruction)
                else:
                    optimized.append(instruction)
            else:
                optimized.append(instruction)
        
        return optimized
    
    def _evaluate_constant_expr(self, expr, temp_values):
        expr = expr.strip()
        
        try:
            return int(expr)
        except:
            pass
        
        for op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']:
            if f' {op} ' in expr:
                parts = expr.split(f' {op} ')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    try:
                        left_val = int(left) if left.isdigit() else temp_values.get(left, None)
                        right_val = int(right) if right.isdigit() else temp_values.get(right, None)
                        
                        if left_val is not None and right_val is not None:
                            if op == '+':
                                return left_val + right_val
                            elif op == '-':
                                return left_val - right_val
                            elif op == '*':
                                return left_val * right_val
                            elif op == '/' and right_val != 0:
                                return left_val // right_val
                            elif op == '%' and right_val != 0:
                                return left_val % right_val
                            elif op == '==':
                                return int(left_val == right_val)
                            elif op == '!=':
                                return int(left_val != right_val)
                            elif op == '<':
                                return int(left_val < right_val)
                            elif op == '>':
                                return int(left_val > right_val)
                            elif op == '<=':
                                return int(left_val <= right_val)
                            elif op == '>=':
                                return int(left_val >= right_val)
                    except:
                        pass
        
        return None
    
    def _dead_code_elimination(self, ir_code):
        used_vars = set()
        labels = set()
        
        for instruction in ir_code:
            instruction = instruction.strip()
            
            if instruction.endswith(':'):
                labels.add(instruction[:-1])
            
            if '=' in instruction and not instruction.startswith('if') and not instruction.startswith('goto'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    expr = parts[1].strip()
                    for word in expr.split():
                        if word.isidentifier() and not word in {'if', 'false', 'goto', 'printf', 'print', 'return'}:
                            used_vars.add(word)
            
            if instruction.startswith('if_false'):
                parts = instruction.split()
                if len(parts) >= 2:
                    used_vars.add(parts[1])
            
            if 'printf' in instruction or 'print ' in instruction:
                for word in instruction.split():
                    if word.isidentifier() and word not in {'printf', 'print'}:
                        used_vars.add(word)
        
        optimized = []
        assigned_vars = {}
        
        for instruction in ir_code:
            instruction = instruction.strip()
            
            if instruction.endswith(':') or instruction.startswith('if') or instruction.startswith('goto'):
                optimized.append(instruction)
            elif instruction.startswith('printf') or instruction.startswith('print') or instruction.startswith('return'):
                optimized.append(instruction)
            elif '=' in instruction:
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    if var_name in used_vars or not var_name.startswith('t'):
                        optimized.append(instruction)
                        assigned_vars[var_name] = True
            else:
                optimized.append(instruction)
        
        return optimized
    
    def optimize_ast(self, node):
        if isinstance(node, Program):
            node.statements = [self.optimize_ast(stmt) for stmt in node.statements]
            return node
        elif isinstance(node, Block):
            node.statements = [self.optimize_ast(stmt) for stmt in node.statements]
            return node
        elif isinstance(node, Declaration):
            if node.init_value:
                node.init_value = self.optimize_ast(node.init_value)
            return node
        elif isinstance(node, Assignment):
            node.expr = self.optimize_ast(node.expr)
            return node
        elif isinstance(node, BinaryOp):
            node.left = self.optimize_ast(node.left)
            node.right = self.optimize_ast(node.right)
            if isinstance(node.left, Number) and isinstance(node.right, Number):
                result = self._evaluate_binary_op(node.left.value, node.op, node.right.value)
                if result is not None:
                    return Number(result)
            return node
        elif isinstance(node, IfStatement):
            node.condition = self.optimize_ast(node.condition)
            node.then_block = self.optimize_ast(node.then_block)
            if node.else_block:
                node.else_block = self.optimize_ast(node.else_block)
            return node
        elif isinstance(node, WhileStatement):
            node.condition = self.optimize_ast(node.condition)
            node.body = self.optimize_ast(node.body)
            return node
        elif isinstance(node, PrintfStatement):
            node.args = [self.optimize_ast(arg) for arg in node.args]
            return node
        elif isinstance(node, ReturnStatement):
            if node.return_val:
                node.return_val = self.optimize_ast(node.return_val)
            return node
        else:
            return node
    
    def _evaluate_binary_op(self, left, op, right):
        try:
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/' and right != 0:
                return left // right
            elif op == '%' and right != 0:
                return left % right
            elif op == '==':
                return int(left == right)
            elif op == '!=':
                return int(left != right)
            elif op == '<':
                return int(left < right)
            elif op == '>':
                return int(left > right)
            elif op == '<=':
                return int(left <= right)
            elif op == '>=':
                return int(left >= right)
        except:
            pass
        return None