import ast
import operator as op
from crewai_tools import BaseTool
from typing import Dict, Type # Add Type for type hinting in operators dictionary

# Supported operators
# Using Type for ast classes to satisfy linters/type checkers better.
operators: Dict[Type[ast.AST], op.Callable] = {
    ast.Add: op.add, 
    ast.Sub: op.sub, 
    ast.Mult: op.mul, 
    ast.Div: op.truediv
}

def eval_expr(expr: str):
    """
    Safely evaluates a string containing a simple arithmetic expression.
    Example: eval_expr('2 + 2') -> 4
    Example: eval_expr('10 * 5 / 2') -> 25.0
    Handles only basic arithmetic operations: +, -, *, /.
    Does NOT support exponentiation, parentheses for order of operations beyond standard parsing, or functions.
    """
    try:
        # ast.parse can raise SyntaxError for malformed expressions
        node = ast.parse(expr, mode='eval').body 
    except SyntaxError:
        # Catching SyntaxError from ast.parse for fundamentally malformed input
        raise ValueError("Invalid syntax in expression. Ensure it's a simple arithmetic expression like '2 + 2' or '10 * 5'.")

    def _eval(node):
        if isinstance(node, ast.Num): # For Python < 3.8, though ast.Constant is preferred
            return node.n
        if isinstance(node, ast.Constant): # For Python >= 3.8, handles numbers and potentially strings if not careful
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric values are supported in expressions.")
            return node.value
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in operators:
                raise TypeError(f"Unsupported operator: {type(node.op).__name__}. Only +, -, *, / are allowed.")
            left_val = _eval(node.left)
            right_val = _eval(node.right)
            if isinstance(right_val, (int, float)) and isinstance(left_val, (int, float)):
                 if isinstance(node.op, ast.Div) and right_val == 0:
                    raise ZeroDivisionError("Division by zero.")
                 return operators[type(node.op)](left_val, right_val)
            else:
                # This case should ideally be caught by Constant check, but as a safeguard
                raise ValueError("Operands must be numbers.")
        # Removed UnaryOp for simplicity as it wasn't in the primary tool description
        # and can add complexity if not handled carefully (e.g. "--2").
        else:
            # This will catch nodes that are not numbers or binary operations,
            # effectively disallowing more complex structures like function calls, lists, etc.
            raise TypeError(f"Unsupported expression structure: {type(node).__name__}. Only simple arithmetic is allowed (e.g. '5 * 2').")
    
    return _eval(node)

class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "Performs basic arithmetic operations: add (+), subtract (-), multiply (*), divide (/). Input should be a string like '2 + 2' or '10 * 5 / 2'. Does not support parentheses or complex expressions."

    def _run(self, expression: str) -> str:
        """
        Processes a simple arithmetic string expression.
        IMPORTANT: This tool uses a controlled evaluation method (ast.parse) for safety,
        not direct eval(). It only supports basic arithmetic operations (+, -, *, /)
        and does not support parentheses, exponentiation, or complex functions.
        """
        try:
            # Using the safer eval_expr function defined above.
            result = eval_expr(expression)
            return f"The result of '{expression}' is {result}."
        except (TypeError, ValueError, ZeroDivisionError) as e:
            # These are expected errors from eval_expr for invalid/unsupported input
            return f"Error calculating '{expression}': {str(e)}. Please use basic operations (+, -, *, /) and numbers (e.g., '2 + 2', '10 * 5'). Parentheses and other functions are not supported."
        except Exception as e:
            # Catch any other unexpected errors during parsing or evaluation
            return f"An unexpected error occurred while processing the expression '{expression}': {str(e)}"

# --- Seção de Testes Conceituais ---
# Os testes reais devem ser implementados em um framework de testes como pytest ou unittest,
# preferencialmente em arquivos separados dentro de um diretório 'tests/tools/'.

# Testes para eval_expr (`tests/tools/test_calculator_tool.py`):
# 1. Testes de Operações Válidas:
#    - `eval_expr("2 + 2")` deve retornar `4`.
#    - `eval_expr("10 - 3")` deve retornar `7`.
#    - `eval_expr("5 * 4")` deve retornar `20`.
#    - `eval_expr("10 / 2")` deve retornar `5.0`.
#    - `eval_expr("2.5 + 1.5")` deve retornar `4.0`.
#    - `eval_expr("7 * 0.5")` deve retornar `3.5`.
#    - `eval_expr("0 + 0")` deve retornar `0`.
#    - `eval_expr("100 / 4 / 5")` deve retornar `5.0` (testando ordem de avaliação padrão esquerda-direita para operadores de mesma precedência).
#    - `eval_expr("10 - 2 + 3")` deve retornar `11`.

# 2. Testes de Expressões Inválidas/Não Suportadas:
#    - `eval_expr("2 ++ 2")` deve levantar `ValueError` (ou `SyntaxError` pego e convertido para `ValueError`).
#    - `eval_expr("abc / 3")` deve levantar `ValueError` (operando não numérico).
#    - `eval_expr("10 / (2+3)")` deve levantar `TypeError` (parênteses/sub-expressões não suportados pela lógica de `_eval`).
#    - `eval_expr("2 ^ 3")` deve levantar `TypeError` (operador não suportado).
#    - `eval_expr("sqrt(9)")` deve levantar `TypeError` (funções não suportadas).
#    - `eval_expr("")` (string vazia) deve levantar `ValueError` (ou `SyntaxError` pego).
#    - `eval_expr("10 2")` (sem operador) deve levantar `ValueError` (ou `SyntaxError` pego).
#    - `eval_expr("(2+2)")` deve levantar `TypeError` (expressão complexa não suportada).

# 3. Teste de Divisão por Zero:
#    - `eval_expr("5 / 0")` deve levantar `ZeroDivisionError`.
#    - `eval_expr("0 / 0")` deve levantar `ZeroDivisionError`.

# Testes para CalculatorTool._run (`tests/tools/test_calculator_tool.py`):
# 1. Teste de Execução Válida:
#    - `tool = CalculatorTool()`
#    - `tool._run("3 + 4")` deve retornar `"The result of '3 + 4' is 7."`
#    - `tool._run("100 / 10")` deve retornar `"The result of '100 / 10' is 10.0."`

# 2. Teste de Execução com Erro (usando `eval_expr` internamente):
#    - `tool = CalculatorTool()`
#    - `tool._run("5 / 0")` deve retornar uma string de erro como `"Error calculating '5 / 0': Division by zero. Please use basic operations..."`
#    - `tool._run("2 ** 9")` deve retornar uma string de erro como `"Error calculating '2 ** 9': Unsupported operator: Pow. Please use basic operations..."` (ou similar dependendo da implementação exata do erro de `eval_expr`).
#    - `tool._run("invalid input")` deve retornar uma string de erro como `"Error calculating 'invalid input': Invalid syntax in expression..."`
