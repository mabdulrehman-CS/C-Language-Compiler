class CodeGenerator:
    def __init__(self):
        self.register_count = 0
        self.assembly_code = []
        self.pseudocode = []
    
    def generate_pseudocode(self, ir_code):
        self.pseudocode = []
        
        for instruction in ir_code:
            instruction = instruction.strip()
            
            if not instruction:
                continue
            
            if instruction.endswith(':'):
                self.pseudocode.append(f"\n{instruction}")
            elif instruction.startswith('if_false'):
                parts = instruction.split()
                var = parts[1]
                label = parts[-1]
                self.pseudocode.append(f"    if NOT {var} goto {label}")
            elif instruction.startswith('goto'):
                label = instruction.split()[-1]
                self.pseudocode.append(f"    goto {label}")
            elif 'printf' in instruction:
                self.pseudocode.append(f"    OUTPUT: {instruction}")
            elif 'print' in instruction:
                var = instruction.split()[-1]
                self.pseudocode.append(f"    PRINT {var}")
            elif instruction.startswith('return'):
                parts = instruction.split()
                if len(parts) > 1:
                    self.pseudocode.append(f"    RETURN {parts[1]}")
                else:
                    self.pseudocode.append(f"    RETURN")
            elif '=' in instruction and not instruction.startswith('#'):
                parts = instruction.split('=', 1)
                var = parts[0].strip()
                expr = parts[1].strip()
                self.pseudocode.append(f"    {var} := {expr}")
            else:
                self.pseudocode.append(f"    {instruction}")
        
        return self.pseudocode
    
    def generate_assembly(self, ir_code):
        self.assembly_code = []
        self.assembly_code.append(".text")
        self.assembly_code.append("main:")
        
        register_map = {}
        current_register = 0
        
        for instruction in ir_code:
            instruction = instruction.strip()
            
            if not instruction:
                continue
            
            if instruction.endswith(':'):
                self.assembly_code.append(f"{instruction}")
            elif instruction.startswith('if_false'):
                parts = instruction.split()
                var = parts[1]
                label = parts[-1]
                reg = self._get_register(var, register_map, current_register)
                self.assembly_code.append(f"    cmp {reg}, 0")
                self.assembly_code.append(f"    je {label}")
            elif instruction.startswith('goto'):
                label = instruction.split()[-1]
                self.assembly_code.append(f"    jmp {label}")
            elif '=' in instruction and not instruction.startswith('#'):
                parts = instruction.split('=', 1)
                var = parts[0].strip()
                expr = parts[1].strip()
                
                if expr.isdigit() or expr.lstrip('-').isdigit():
                    reg = self._allocate_register(var, register_map, current_register)
                    self.assembly_code.append(f"    mov {reg}, {expr}")
                elif '+' in expr:
                    self._generate_binary_op(expr, var, register_map, current_register, '+', 'add')
                elif '-' in expr:
                    self._generate_binary_op(expr, var, register_map, current_register, '-', 'sub')
                elif '*' in expr:
                    self._generate_binary_op(expr, var, register_map, current_register, '*', 'imul')
                elif '/' in expr:
                    self._generate_binary_op(expr, var, register_map, current_register, '/', 'idiv')
                else:
                    reg = self._allocate_register(var, register_map, current_register)
                    self.assembly_code.append(f"    mov {reg}, {expr}")
            elif 'printf' in instruction or 'print' in instruction:
                self.assembly_code.append(f"    call print_function  # {instruction}")
            elif instruction.startswith('return'):
                self.assembly_code.append(f"    mov eax, 0")
                self.assembly_code.append(f"    ret")
            else:
                self.assembly_code.append(f"    # {instruction}")
        
        self.assembly_code.append("")
        self.assembly_code.append(".data")
        
        return self.assembly_code
    
    def _allocate_register(self, var, register_map, current_reg):
        if var not in register_map:
            register_map[var] = f"r{current_reg % 8}"
        return register_map[var]
    
    def _get_register(self, var, register_map, current_reg):
        if var not in register_map:
            register_map[var] = f"r{len(register_map) % 8}"
        return register_map[var]
    
    def _generate_binary_op(self, expr, var, reg_map, current_reg, op, asm_op):
        parts = expr.split(f' {op} ')
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            
            reg = self._allocate_register(var, reg_map, current_reg)
            
            if left.isdigit():
                self.assembly_code.append(f"    mov {reg}, {left}")
            else:
                left_reg = self._get_register(left, reg_map, current_reg)
                self.assembly_code.append(f"    mov {reg}, {left_reg}")
            
            if right.isdigit():
                self.assembly_code.append(f"    {asm_op} {reg}, {right}")
            else:
                right_reg = self._get_register(right, reg_map, current_reg)
                self.assembly_code.append(f"    {asm_op} {reg}, {right_reg}")
