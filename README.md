# C Compiler

A complete compiler for a C language with GUI, built in Python.

## Features

- **8 Output Modes**: RUN, TOKENS, AST, SYMBOL TABLE, IR, IR (OPTIMIZED), PSEUDOCODE, ASSEMBLY
- **Syntax Highlighting**: Real-time code coloring in editor
- **Code Optimization**: Constant folding & dead code elimination
- **Error Handling**: Clear error messages with line numbers
- **Modern GUI**: Dark theme interface

```
┌─────────────────────────────────────────────────────┐
│  Mini C Compiler                                    │
├────────────────────┬────────────────────────────────┤
│   INPUT CODE       │        OUTPUT                  │
│   (C code here)    │        (Results here)          │
├────────────────────┴────────────────────────────────┤
│  [Output Mode ▼]              [▶ Compile]           │
└─────────────────────────────────────────────────────┘
```

**Requirements**: Python 3.7+ (uses only standard library - no external dependencies)

## Usage

1. Run `python main.py`
2. Enter C code in the left panel
3. Select output mode from dropdown
4. Click **Compile**

## Supported Syntax

**Keywords**: `int`, `float`, `if-else`, `while`, `printf`, 'include', 'studio' 
arithmetic (`+`,`-`,`*`,`/`,`%`), 
comparisons (`==`,`!=`,`<`,`>`,`<=`,`>=`)

## Project Structure

```
├── main.py              # Entry point
├── gui.py               # GUI interface
├── lexer.py             # Tokenizer
├── parser.py            # Syntax analyzer (builds AST)
├── ast_nodes.py         # AST node definitions
├── semantic_analyzer.py # Type & scope checking
├── ir_generator.py      # Three-Address Code generator
├── optimizer.py         # Code optimization
├── code_generator.py    # Pseudocode & Assembly generator
├── interpreter.py       # Program executor
└── errors.py            # Error classes
```

## Compilation Stages

### Stage 1: Lexical Analysis
**Input:** Source code string
**Output:** List of tokens with types and positions

### Stage 2: Syntax Analysis
**Input:** Token stream
**Output:** Abstract Syntax Tree (AST)

### Stage 3: Semantic Analysis
**Input:** AST
**Output:** Validated AST with symbol table

### Stage 4: AST Optimization
**Input:** AST
**Output:** Optimized AST

### Stage 5: IR Generation
**Input:** AST
**Output:** Three-Address Code (TAC)

### Stage 6: IR Optimization
**Input:** IR Code
**Output:** Optimized IR

### Stage 7: Code Generation
**Input:** IR Code
**Output:** Pseudocode or Assembly

### Stage 8: Execution (Run Mode)
**Input:** AST
**Output:** Program output

## Compiler Pipeline

```
Source Code → Lexer → Parser → Semantic Analyzer → IR Generator → Optimizer → Code Generator (Pseudocode / Assembly / Execution)
```

### 8 Output Modes

1. **RUN** - Execute program and display output
2. **TOKENS** - Lexical analysis with table format (No | Type | Value)
3. **AST** - Abstract syntax tree with hierarchical indentation
4. **SYMBOL TABLE** - Variable definitions in column format (Variable | Type)
5. **IR** - Intermediate representation before optimization
6. **IR (OPTIMIZED)** - Intermediate representation after optimization
7. **PSEUDOCODE** - Human-readable intermediate code
8. **ASSEMBLY** - x86-like assembly code

## Installation

```bash
git clone https://github.com/yourusername/mini-c-compiler.git
cd mini-c-compiler
python main.py
```
