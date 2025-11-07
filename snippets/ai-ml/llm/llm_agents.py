"""
LLM Agents
Autonomous agents that can use tools and make decisions.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Tool:
    """Agent tool definition."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


@dataclass
class AgentStep:
    """Single step in agent execution."""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict] = None
    observation: Optional[str] = None
    status: AgentStatus = AgentStatus.THINKING


@dataclass
class AgentResult:
    """Agent execution result."""
    final_answer: str
    steps: List[AgentStep] = field(default_factory=list)
    total_steps: int = 0
    success: bool = True
    error: Optional[str] = None


class BaseAgent:
    """Base class for LLM agents."""

    def __init__(
        self,
        llm_client,
        tools: List[Tool],
        max_iterations: int = 10,
        verbose: bool = True
    ):
        """
        Initialize agent.

        Args:
            llm_client: LLM client for reasoning
            tools: Available tools
            max_iterations: Maximum execution steps
            verbose: Print execution details
        """
        self.llm_client = llm_client
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.verbose = verbose

    def run(self, task: str) -> AgentResult:
        """
        Run agent on task.

        Args:
            task: Task description

        Returns:
            AgentResult
        """
        raise NotImplementedError


class ReActAgent(BaseAgent):
    """ReAct (Reasoning + Acting) agent."""

    def run(self, task: str) -> AgentResult:
        """
        Execute task using ReAct pattern.

        Args:
            task: Task to complete

        Returns:
            AgentResult
        """
        steps = []

        for i in range(self.max_iterations):
            if self.verbose:
                print(f"\n=== Step {i + 1} ===")

            # Generate thought and action
            thought, action, action_input = self._generate_step(task, steps)

            step = AgentStep(
                step_number=i + 1,
                thought=thought,
                action=action,
                action_input=action_input
            )

            if self.verbose:
                print(f"Thought: {thought}")
                print(f"Action: {action}")

            # Check if final answer
            if action == "Final Answer":
                return AgentResult(
                    final_answer=action_input.get("answer", ""),
                    steps=steps,
                    total_steps=i + 1,
                    success=True
                )

            # Execute action
            try:
                observation = self._execute_action(action, action_input)
                step.observation = observation
                step.status = AgentStatus.COMPLETED

                if self.verbose:
                    print(f"Observation: {observation}")

            except Exception as e:
                step.status = AgentStatus.ERROR
                step.observation = f"Error: {str(e)}"

                if self.verbose:
                    print(f"Error: {e}")

            steps.append(step)

        # Max iterations reached
        return AgentResult(
            final_answer="Max iterations reached",
            steps=steps,
            total_steps=self.max_iterations,
            success=False,
            error="Maximum iterations exceeded"
        )

    def _generate_step(
        self,
        task: str,
        previous_steps: List[AgentStep]
    ) -> tuple:
        """Generate next thought and action."""
        # Build prompt with previous steps
        prompt = self._build_react_prompt(task, previous_steps)

        # Get LLM response
        response = self.llm_client.complete(prompt)

        # Parse response
        thought, action, action_input = self._parse_react_response(response.content)

        return thought, action, action_input

    def _build_react_prompt(
        self,
        task: str,
        previous_steps: List[AgentStep]
    ) -> str:
        """Build ReAct prompt."""
        tools_desc = "\n".join(
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        )

        prompt_parts = [
            f"Task: {task}",
            "",
            "Available tools:",
            tools_desc,
            "",
            "Format:",
            "Thought: [your reasoning]",
            "Action: [tool name or 'Final Answer']",
            "Action Input: {{parameters}}",
            ""
        ]

        # Add previous steps
        for step in previous_steps:
            prompt_parts.extend([
                f"Thought: {step.thought}",
                f"Action: {step.action}",
                f"Action Input: {step.action_input}",
                f"Observation: {step.observation}",
                ""
            ])

        prompt_parts.append("Now continue:")

        return "\n".join(prompt_parts)

    def _parse_react_response(self, response: str) -> tuple:
        """Parse ReAct response."""
        import re

        # Extract thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""

        # Extract action
        action_match = re.search(r'Action:\s*(.+?)(?=Action Input:|$)', response, re.DOTALL)
        action = action_match.group(1).strip() if action_match else ""

        # Extract action input
        input_match = re.search(r'Action Input:\s*(\{.+?\}|.+?)(?=Observation:|$)', response, re.DOTALL)
        action_input_str = input_match.group(1).strip() if input_match else "{}"

        # Try to parse as JSON
        import json
        try:
            action_input = json.loads(action_input_str)
        except:
            action_input = {"input": action_input_str}

        return thought, action, action_input

    def _execute_action(
        self,
        action: str,
        action_input: Dict
    ) -> str:
        """Execute tool action."""
        if action not in self.tools:
            return f"Unknown tool: {action}"

        tool = self.tools[action]

        try:
            result = tool.function(**action_input)
            return str(result)
        except Exception as e:
            return f"Error executing {action}: {str(e)}"


class PlanAndExecuteAgent(BaseAgent):
    """Agent that plans all steps upfront then executes."""

    def run(self, task: str) -> AgentResult:
        """
        Execute task using planning approach.

        Args:
            task: Task to complete

        Returns:
            AgentResult
        """
        # Generate plan
        plan = self._generate_plan(task)

        if self.verbose:
            print("=== Plan ===")
            for i, step in enumerate(plan, 1):
                print(f"{i}. {step}")

        # Execute plan
        steps = []

        for i, planned_action in enumerate(plan):
            if self.verbose:
                print(f"\n=== Executing Step {i + 1} ===")

            # Parse planned action
            action, action_input = self._parse_planned_action(planned_action)

            step = AgentStep(
                step_number=i + 1,
                thought=planned_action,
                action=action,
                action_input=action_input
            )

            # Execute
            try:
                observation = self._execute_action(action, action_input)
                step.observation = observation
                step.status = AgentStatus.COMPLETED

                if self.verbose:
                    print(f"Result: {observation}")

            except Exception as e:
                step.status = AgentStatus.ERROR
                step.observation = f"Error: {str(e)}"

                if self.verbose:
                    print(f"Error: {e}")

            steps.append(step)

        # Get final answer
        final_answer = steps[-1].observation if steps else "No steps executed"

        return AgentResult(
            final_answer=final_answer,
            steps=steps,
            total_steps=len(steps),
            success=True
        )

    def _generate_plan(self, task: str) -> List[str]:
        """Generate execution plan."""
        tools_desc = "\n".join(
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        )

        prompt = f"""Task: {task}

Available tools:
{tools_desc}

Create a step-by-step plan to complete this task.
Output each step on a new line in format: <action_name>(<parameters>)

Plan:"""

        response = self.llm_client.complete(prompt)

        # Parse plan
        plan_lines = [
            line.strip()
            for line in response.content.split('\n')
            if line.strip() and not line.strip().startswith('Plan:')
        ]

        return plan_lines

    def _parse_planned_action(self, planned_action: str) -> tuple:
        """Parse planned action string."""
        import re

        # Match pattern: action_name(param1=value1, param2=value2)
        match = re.match(r'(\w+)\((.*)\)', planned_action)

        if not match:
            return planned_action, {}

        action = match.group(1)
        params_str = match.group(2)

        # Parse parameters
        action_input = {}

        if params_str:
            # Simple parsing (doesn't handle nested structures)
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    action_input[key.strip()] = value.strip().strip('"\'')

        return action, action_input


# Usage Examples
if __name__ == "__main__":
    # Mock LLM client for demo
    class MockLLMClient:
        def complete(self, prompt):
            class Response:
                content = """Thought: I need to search for information
Action: search
Action Input: {"query": "Python programming"}"""

            return Response()

    # Define tools
    def search_tool(query: str) -> str:
        """Search for information."""
        return f"Found information about: {query}"

    def calculate_tool(expression: str) -> float:
        """Calculate mathematical expression."""
        return eval(expression)

    tools = [
        Tool(
            name="search",
            description="Search for information on the internet",
            function=search_tool,
            parameters={"query": "string"}
        ),
        Tool(
            name="calculate",
            description="Perform mathematical calculations",
            function=calculate_tool,
            parameters={"expression": "string"}
        )
    ]

    # Example 1: ReAct Agent
    print("=== ReAct Agent ===")

    client = MockLLMClient()
    agent = ReActAgent(
        llm_client=client,
        tools=tools,
        max_iterations=3,
        verbose=True
    )

    # Note: This is a simplified demo
    # In production, connect to real LLM and implement full parsing

    print("\nReAct agent initialized")
    print(f"Available tools: {list(agent.tools.keys())}")
