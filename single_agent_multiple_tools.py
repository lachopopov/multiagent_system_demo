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


# Create the agent with all calculation tools
model_client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano",
    api_key=openai_api_key,
)
agent = AssistantAgent(
    name="calculator",
    model_client=model_client,
    tools=[add, subtract, multiply, divide, power],
    system_message="You are a calculator assistant. Use the provided tools to perform calculations. Always use tools for math; do not compute in your head.",
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
