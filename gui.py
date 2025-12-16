import tkinter as tk
from tkinter import ttk
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from code_generator import CodeGenerator
from interpreter import Interpreter
from errors import *
from ast_nodes import (
    Program, Block, Declaration, Assignment, PrintfStatement, PrintStatement,
    ReturnStatement, IfStatement, WhileStatement, BinaryOp, Number, Identifier
)

class CompilerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mini C Compiler")
        self.root.geometry("1400x900")
        self.root.config(bg="#0d1117")
        self.root.resizable(True, True)

        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', 
                       fieldbackground="#161b22",
                       background="#161b22",
                       foreground="#c9d1d9",
                       arrowcolor="#58a6ff")
        style.map('TCombobox', 
                 fieldbackground=[('readonly', '#161b22')],
                 background=[('readonly', '#161b22')])

        # Header label with enhanced styling
        header = tk.Label(self.root, text="🔧 Mini C Compiler", 
                         font=("Segoe UI", 22, "bold"), 
                         bg="#161b22", fg="#58a6ff", pady=15)
        header.pack(fill=tk.X)

        # Main content frame
        main_frame = tk.Frame(self.root, bg="#0d1117")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left panel - Input with border
        left_panel = tk.Frame(main_frame, bg="#0d1117", highlightbackground="#30363d", 
                             highlightthickness=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        input_label = tk.Label(left_panel, text="📝 Input Code", font=("Segoe UI", 12, "bold"),
                              bg="#161b22", fg="#58a6ff", pady=8)
        input_label.pack(anchor="w", fill=tk.X)

        # Input text with scrollbar
        input_frame = tk.Frame(left_panel, bg="#0d1117")
        input_frame.pack(fill=tk.BOTH, expand=True)

        input_scrollbar = tk.Scrollbar(input_frame)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_text = tk.Text(input_frame, height=30, width=60, bg="#0d1117", 
                                  fg="#c9d1d9", font=("Courier New", 10), 
                                  insertbackground="#58a6ff", relief=tk.FLAT, bd=0,
                                  yscrollcommand=input_scrollbar.set)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.config(command=self.input_text.yview)

        # Configure syntax highlighting tags for input
        self.input_text.tag_config("keyword", foreground="#ff7b72")          # Red for keywords
        self.input_text.tag_config("string", foreground="#a5d6ff")           # Blue for strings
        self.input_text.tag_config("number", foreground="#d2a8ff")           # Purple for numbers
        self.input_text.tag_config("comment", foreground="#8b949e")          # Gray for comments
        self.input_text.tag_config("preprocess", foreground="#ffa657")       # Orange for #include

        # Bind syntax highlighting to key release events
        self.input_text.bind("<KeyRelease>", lambda e: self._highlight_input_syntax())        # Right panel - Controls and Output
        right_panel = tk.Frame(main_frame, bg="#0d1117")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # Control panel with gradient-like effect
        control_panel = tk.Frame(right_panel, bg="#161b22", relief=tk.FLAT)
        control_panel.pack(fill=tk.X, pady=(0, 12), padx=0)

        # Mode selection
        mode_frame = tk.Frame(control_panel, bg="#161b22")
        mode_frame.pack(fill=tk.X, padx=12, pady=12)

        mode_label = tk.Label(mode_frame, text="Output Mode:", font=("Segoe UI", 11, "bold"),
                             bg="#161b22", fg="#58a6ff")
        mode_label.pack(anchor="w", pady=(0, 6))

        self.mode_var = tk.StringVar(self.root)
        self.mode_var.set("RUN")
        modes = ["RUN", "TOKENS", "AST", "SYMBOL TABLE", "IR", "IR (OPTIMIZED)", "PSEUDOCODE", "ASSEMBLY"]
        
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                       values=modes, state="readonly", width=35, font=("Segoe UI", 10))
        self.mode_combo.pack(fill=tk.X)

        # Button frame
        button_frame = tk.Frame(control_panel, bg="#161b22")
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.button = tk.Button(button_frame, text="▶ Compile", command=self.compile,
                               bg="#238636", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                               relief=tk.FLAT, padx=25, pady=8, cursor="hand2",
                               activebackground="#2ea043", activeforeground="#ffffff",
                               bd=0)
        self.button.pack(fill=tk.X)

        # Output section with border
        output_label = tk.Label(right_panel, text="📊 Output", font=("Segoe UI", 12, "bold"),
                               bg="#161b22", fg="#58a6ff", pady=8)
        output_label.pack(anchor="w", fill=tk.X)

        # Output text with scrollbar
        output_frame = tk.Frame(right_panel, bg="#0d1117")
        output_frame.pack(fill=tk.BOTH, expand=True)

        output_scrollbar = tk.Scrollbar(output_frame)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(output_frame, height=30, width=60, bg="#0d1117",
                                   fg="#79c0ff", font=("Courier New", 9),
                                   relief=tk.FLAT, bd=0,
                                   yscrollcommand=output_scrollbar.set)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.config(command=self.output_text.yview)

        # Configure color tags for output
        self.output_text.tag_config("header", foreground="#58a6ff", font=("Courier New", 9, "bold"))
        self.output_text.tag_config("keyword", foreground="#ff7b72")
        self.output_text.tag_config("number", foreground="#d2a8ff")
        self.output_text.tag_config("string", foreground="#a5d6ff")
        self.output_text.tag_config("operator", foreground="#ffa657")
        self.output_text.tag_config("identifier", foreground="#79c0ff")
        self.output_text.tag_config("type", foreground="#ff7b72")
        self.output_text.tag_config("success", foreground="#3fb950")

        self.root.mainloop()

    def _format_ast_columns(self, node, indent=0):
        result = ""
        prefix = "  " * indent
        
        if isinstance(node, list):
            for item in node:
                result += self._format_ast_columns(item, indent)
        elif node is None:
            pass
        elif isinstance(node, Program):
            result += f"{prefix}Program:\n"
            for stmt in node.statements:
                result += self._format_ast_columns(stmt, indent + 1)
        elif isinstance(node, Block):
            result += f"{prefix}Block:\n"
            for stmt in node.statements:
                result += self._format_ast_columns(stmt, indent + 1)
        elif isinstance(node, Declaration):
            result += f"{prefix}Declaration: {node.datatype} {node.name}\n"
            if node.init_value:
                result += self._format_ast_columns(node.init_value, indent + 1)
        elif isinstance(node, Assignment):
            result += f"{prefix}Assignment: {node.name} =\n"
            result += self._format_ast_columns(node.expr, indent + 1)
        elif isinstance(node, PrintfStatement):
            result += f"{prefix}Printf: {node.format_str}\n"
            for arg in node.args:
                result += self._format_ast_columns(arg, indent + 1)
        elif isinstance(node, PrintStatement):
            result += f"{prefix}Print:\n"
            result += self._format_ast_columns(node.expr, indent + 1)
        elif isinstance(node, ReturnStatement):
            result += f"{prefix}Return"
            if node.return_val:
                result += ":\n"
                result += self._format_ast_columns(node.return_val, indent + 1)
            else:
                result += "\n"
        elif isinstance(node, IfStatement):
            result += f"{prefix}If:\n"
            result += f"{prefix}  Condition:\n"
            result += self._format_ast_columns(node.condition, indent + 2)
            result += f"{prefix}  Then:\n"
            result += self._format_ast_columns(node.then_block, indent + 2)
            if node.else_block:
                result += f"{prefix}  Else:\n"
                result += self._format_ast_columns(node.else_block, indent + 2)
        elif isinstance(node, WhileStatement):
            result += f"{prefix}While:\n"
            result += f"{prefix}  Condition:\n"
            result += self._format_ast_columns(node.condition, indent + 2)
            result += f"{prefix}  Body:\n"
            result += self._format_ast_columns(node.body, indent + 2)
        elif isinstance(node, BinaryOp):
            result += f"{prefix}BinaryOp: {node.op}\n"
            result += f"{prefix}  Left:\n"
            result += self._format_ast_columns(node.left, indent + 2)
            result += f"{prefix}  Right:\n"
            result += self._format_ast_columns(node.right, indent + 2)
        elif isinstance(node, Number):
            result += f"{prefix}Number: {node.value}\n"
        elif isinstance(node, Identifier):
            result += f"{prefix}Identifier: {node.name}\n"
        else:
            result += f"{prefix}{str(node)}\n"
        
        return result

    def _highlight_input_syntax(self):
        self.input_text.tag_remove("keyword", "1.0", tk.END)
        self.input_text.tag_remove("string", "1.0", tk.END)
        self.input_text.tag_remove("number", "1.0", tk.END)
        self.input_text.tag_remove("comment", "1.0", tk.END)
        self.input_text.tag_remove("preprocess", "1.0", tk.END)

        keywords = ["int", "void", "char", "float", "if", "else", "while", "for", "return", "printf"]
        
        content = self.input_text.get("1.0", tk.END)
        
        # Highlight preprocessor directives
        for match in self._find_pattern(content, r"#include.*"):
            start_idx = self._convert_index(match[0], content)
            end_idx = self._convert_index(match[1], content)
            self.input_text.tag_add("preprocess", start_idx, end_idx)
        
        # Highlight strings
        for match in self._find_pattern(content, r'"[^"]*"'):
            start_idx = self._convert_index(match[0], content)
            end_idx = self._convert_index(match[1], content)
            self.input_text.tag_add("string", start_idx, end_idx)
        
        # Highlight numbers
        for match in self._find_pattern(content, r"\b\d+\b"):
            start_idx = self._convert_index(match[0], content)
            end_idx = self._convert_index(match[1], content)
            self.input_text.tag_add("number", start_idx, end_idx)
        
        # Highlight keywords
        for keyword in keywords:
            for match in self._find_pattern(content, r"\b" + keyword + r"\b"):
                start_idx = self._convert_index(match[0], content)
                end_idx = self._convert_index(match[1], content)
                self.input_text.tag_add("keyword", start_idx, end_idx)

    def _find_pattern(self, text, pattern):
        import re
        matches = []
        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end()))
        return matches

    def _convert_index(self, char_idx, text):
        line = text[:char_idx].count("\n") + 1
        col = char_idx - text[:char_idx].rfind("\n") - 1
        return f"{line}.{col}"

    def compile(self):
        code = self.input_text.get("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        try:
            if not code.strip():
                raise SyntaxError("Error: C program is empty. Please enter valid C code.")
            
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens, lexer.line_map)
            ast = parser.parse()
            sem = SemanticAnalyzer(includes=parser.includes)
            sem.analyze(ast)
            
            # Generate IR from original AST (before optimization) for "IR" mode
            ir_gen_before = IRGenerator()
            ir_before_opt = ir_gen_before.generate(ast)
            
            # Now optimize the AST
            optimizer = Optimizer()
            ast_optimized = optimizer.optimize_ast(ast)
            
            # Generate IR from optimized AST
            ir_gen = IRGenerator()
            ir = ir_gen.generate(ast_optimized)
            
            # Apply IR-level optimization
            ir = optimizer.optimize_ir(ir)
            
            code_gen = CodeGenerator()
            pseudocode = code_gen.generate_pseudocode(ir)
            assembly = code_gen.generate_assembly(ir)
            
            interp = Interpreter()
            output = interp.run(ast_optimized)

            mode = self.mode_var.get()
            if mode == "TOKENS":
                self.output_text.insert(tk.END, "TOKENS:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                self.output_text.insert(tk.END, f"{'No.':<5} {'Type':<15} {'Value':<20}\n")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                for i, (tok_type, tok_val) in enumerate(tokens, 1):
                    line = f"{i:<5} "
                    self.output_text.insert(tk.END, line)
                    self.output_text.insert(tk.END, f"{tok_type:<15} ", "keyword")
                    self.output_text.insert(tk.END, f"{str(tok_val):<20}\n", "string")
            elif mode == "AST":
                self.output_text.insert(tk.END, "ABSTRACT SYNTAX TREE:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                self.output_text.insert(tk.END, self._format_ast_columns(ast))
            elif mode == "SYMBOL TABLE":
                self.output_text.insert(tk.END, "SYMBOL TABLE:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                self.output_text.insert(tk.END, f"{'Variable':<20} {'Type':<15}\n")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                for var, dtype in sem.symbols.items():
                    self.output_text.insert(tk.END, f"{var:<20} ", "identifier")
                    self.output_text.insert(tk.END, f"{dtype:<15}\n", "type")
            elif mode == "IR":
                self.output_text.insert(tk.END, "INTERMEDIATE CODE (TAC):\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                for line in ir_before_opt:
                    self.output_text.insert(tk.END, line + "\n", "operator")
            elif mode == "IR (OPTIMIZED)":
                self.output_text.insert(tk.END, "OPTIMIZED CODE:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                for line in ir:
                    self.output_text.insert(tk.END, line + "\n", "success")
            elif mode == "PSEUDOCODE":
                self.output_text.insert(tk.END, "PSEUDOCODE:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                if isinstance(pseudocode, list):
                    for line in pseudocode:
                        self.output_text.insert(tk.END, line + "\n", "identifier")
                else:
                    self.output_text.insert(tk.END, pseudocode, "identifier")
            elif mode == "ASSEMBLY":
                self.output_text.insert(tk.END, "ASSEMBLY:\n", "header")
                self.output_text.insert(tk.END, "-" * 60 + "\n")
                for line in assembly:
                    self.output_text.insert(tk.END, line + "\n", "operator")
            elif mode == "RUN":
                if output:
                    self.output_text.insert(tk.END, "OUTPUT:\n", "header")
                    self.output_text.insert(tk.END, "-" * 60 + "\n")
                    self.output_text.insert(tk.END, "\n".join(map(str, output)), "success")
                else:
                    self.output_text.insert(tk.END, "[Program executed successfully with no output]")

        except (LexicalError, SyntaxError, SemanticError, RuntimeError) as e:
            self.output_text.insert(tk.END, str(e))
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
