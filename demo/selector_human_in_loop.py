"""
Selector group chat for the procurement workflow with human-in-the-loop.

Uses agents and tools from demo/prompts.py and demo/tools.py.
Run from repo root: python demo/selector_human_in_loop.py
"""

import asyncio
import os
import sys

# Ensure demo and project root are on path for prompts, tools, and constants
_demo_dir = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_demo_dir)
if _root not in sys.path:
    sys.path.insert(0, _root)
if _demo_dir not in sys.path:
    sys.path.insert(0, _demo_dir)

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from constants import openai_api_key
from prompts import AGENT_CONFIG

# -----------------------------------------------------------------------------
# Model client
# -----------------------------------------------------------------------------
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=openai_api_key,
)

# -----------------------------------------------------------------------------
# Build agents from AGENT_CONFIG (intake, policy, finance, vendor_risk, reviewer)
# -----------------------------------------------------------------------------
AGENT_DESCRIPTIONS = {
    "intake_agent": "Extracts and structures procurement request from user input. Use first for new requests.",
    "policy_agent": "Checks policy compliance and approval rules. Use after intake when request is structured.",
    "finance_agent": "Validates budget and spend. Use after intake for financial checks.",
    "vendor_risk_agent": "Assesses vendor eligibility and risk. Use when vendor is known.",
    "reviewer_agent": "Synthesizes all findings and decides next action (approve/escalate/reject). Use after other agents.",
}

assistant_agents = []
for key, config in AGENT_CONFIG.items():
    if key == "human_proxy_agent":
        continue
    name = key.replace("_agent", " ").replace("_", " ").title()
    assistant_agents.append(
        AssistantAgent(
            name=key,
            description=AGENT_DESCRIPTIONS.get(key, config["prompt"][:200]),
            model_client=model_client,
            system_message=config["prompt"],
            tools=config.get("tools") or [],
        )
    )

# Human-in-the-loop: when selector chooses this agent, user is prompted for input
human_agent = UserProxyAgent(
    "human_proxy_agent",
    description="Human approver. Select when the reviewer escalates or when final approval/rejection is needed.",
)

participants = assistant_agents + [human_agent]

# -----------------------------------------------------------------------------
# Termination: stop on explicit end or after max messages
# -----------------------------------------------------------------------------
termination = (
    TextMentionTermination("TERMINATE")
    | TextMentionTermination("FINAL_DECISION")
    | TextMentionTermination("APPROVED")
    | TextMentionTermination("REJECTED")
    | MaxMessageTermination(max_messages=30)
)

# -----------------------------------------------------------------------------
# Selector prompt for procurement workflow
# -----------------------------------------------------------------------------
selector_prompt = """You are selecting the next agent in a procurement workflow.

Agents and when to use them:
{roles}

Current conversation:
{history}

Select exactly one agent from {participants} to perform the next step.
Prefer order: intake (structure request) -> policy/finance/vendor_risk (checks) -> reviewer (synthesize).
Choose human_proxy_agent when the reviewer has escalated or when a final human decision is needed.
Reply with only the agent name.
"""

# -----------------------------------------------------------------------------
# Team
# -----------------------------------------------------------------------------
team = SelectorGroupChat(
    participants,
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,
)


async def main() -> None:
    task = (
        "We need to procure 50 MacBooks for Engineering, budget around 75L INR, "
        "next quarter, prefer Apple Authorized Vendor. Process this request."
    )
    while True:
        print("\n--- Running procurement workflow ---\n")
        stream = team.run_stream(task=task)
        await Console(stream)
        task = input("\nEnter next instruction or feedback (or 'exit' to quit): ").strip()
        if not task or task.lower() == "exit":
            break


if __name__ == "__main__":
    asyncio.run(main())
