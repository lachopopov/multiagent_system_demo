import ast
import operator
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from contants import openai_api_key


# Calculation tools — each takes two numbers and returns a result
async def add(a: float, b: float) -> float:
    """Add two numbers. Args: a (first number), b (second number)."""
    return a + b


async def subtract(a: float, b: float) -> float:
    """Subtract b from a. Args: a (first number), b (number to subtract)."""
    return a - b


async def multiply(a: float, b: float) -> float:
    """Multiply two numbers. Args: a (first number), b (second number)."""
    return a * b


async def divide(a: float, b: float) -> float:
    """Divide a by b. Args: a (numerator), b (denominator). Returns error if b is zero."""
    if b == 0:
        return float("nan")  # or raise; agent will see nan
    return a / b


async def power(a: float, b: float) -> float:
    """Raise a to the power of b. Args: a (base), b (exponent)."""
    return a**b


def _eval_node(node):
    """Safely evaluate an AST node (numbers and +, -, *, /, **)."""
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return ops[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return ops[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


async def evaluate(expression: str) -> float:
    """Evaluate a full mathematical expression (e.g. '2+3*4', '(1+2)*3'). Use this for expressions with multiple operators; it respects BODMAS/order of operations."""
    expr = expression.strip().replace(" ", "")
    tree = ast.parse(expr, mode="eval")
    return float(_eval_node(tree.body))


# Create the agent with all calculation tools
model_client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano",
    api_key=openai_api_key,
)
agent = AssistantAgent(
    name="calculator",
    model_client=model_client,
    tools=[evaluate, add, subtract, multiply, divide, power],
    system_message="You are a calculator assistant. For expressions with multiple operators (e.g. 2+3*4, 10/2+1), always use the 'evaluate' tool with the full expression—it handles BODMAS correctly. Use add/subtract/multiply/divide only for simple two-number operations.",
)

async def main():
    task = input("Enter your calculation or question: ").strip()
    if not task:
        print("No task entered. Exiting.")
        return
    await Console(
        agent.run_stream(task=task),
        output_stats=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
