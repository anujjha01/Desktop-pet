"""Evaluate simple spoken arithmetic without evaluating arbitrary code."""

import ast
import operator
import re


_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _value(node):
    if isinstance(node, ast.Expression):
        return _value(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_value(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = _value(node.left), _value(node.right)
        if (
            isinstance(node.op, ast.Mult)
            and (abs(left) > 1e9 or abs(right) > 1e9)
        ):
            raise ValueError("That number is too large for me to calculate.")
        return _BINARY[type(node.op)](left, right)
    raise ValueError("I can calculate simple arithmetic like 12 times 3.")


def calculate(spoken):
    expression = spoken.lower().strip()
    expression = re.sub(r"\bmultiplied by\b|\btimes\b|\bx\b", "*", expression)
    expression = re.sub(r"\bdivided by\b|\bover\b", "/", expression)
    expression = re.sub(r"\bplus\b", "+", expression)
    expression = re.sub(r"\bminus\b", "-", expression)
    expression = re.sub(r"\bmodulo\b|\bmod\b", "%", expression)
    expression = re.sub(r"\s+", "", expression)
    if not expression or len(expression) > 100 or re.search(r"[^0-9.+*/%()\-]", expression):
        raise ValueError("I can calculate simple arithmetic like 12 times 3.")
    try:
        result = _value(ast.parse(expression, mode="eval"))
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("I couldn't calculate that expression.") from exc
    if abs(result) > 1e15:
        raise ValueError("That answer is too large for me to say out loud.")
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    if isinstance(result, float):
        result = round(result, 6)
    return f"The answer is {result}."
