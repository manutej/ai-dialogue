"""
Intelligent Orchestrator

Claude-side intelligence for dynamic workflow management.
Provides tools for Claude to analyze tasks, generate loops, and orchestrate execution.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Subtask:
    """Represents a decomposed subtask"""
    name: str
    description: str
    complexity: str  # simple, moderate, complex
    dependencies: List[str] = field(default_factory=list)
    estimated_turns: int = 1
    context_needed: List[str] = field(default_factory=list)


@dataclass
class ExecutionStrategy:
    """Strategy for executing subtasks"""
    strategy_type: str  # single_loop, one_loop_per_task, mixed
    total_estimated_turns: int
    parallel_groups: List[List[str]] = field(default_factory=list)
    reasoning: str = ""


class IntelligentOrchestrator:
    """
    Claude-side intelligence for dynamic workflow orchestration

    Provides methods that Claude (via protocol) can use to:
    - Parse decomposition responses
    - Generate dynamic prompts
    - Decide on execution strategies
    - Adapt workflows based on results
    """

    def __init__(self):
        self.subtasks: List[Subtask] = []
        self.execution_strategy: Optional[ExecutionStrategy] = None
        self.execution_results: Dict[str, Any] = {}

    def parse_decomposition(self, decomposition_text: str) -> Tuple[List[Subtask], ExecutionStrategy]:
        """
        Parse Claude's decomposition response into structured data

        Looks for patterns like:
        SUBTASKS:
        1. TaskName - Complexity: simple
           Description: ...
           Dependencies: task1, task2

        LOOP_STRATEGY: single_loop
        """
        subtasks = []
        strategy_type = "single_loop"  # default

        # Extract subtasks section
        subtasks_match = re.search(r'SUBTASKS:(.*?)(?:LOOP_STRATEGY:|$)', decomposition_text, re.DOTALL)
        if subtasks_match:
            subtasks_text = subtasks_match.group(1)

            # Parse each subtask
            subtask_pattern = r'\d+\.\s*(.+?)\s*-\s*Complexity:\s*(\w+)(.*?)(?=\d+\.|$)'
            for match in re.finditer(subtask_pattern, subtasks_text, re.DOTALL):
                name = match.group(1).strip()
                complexity = match.group(2).strip().lower()
                details = match.group(3).strip()

                # Extract description
                desc_match = re.search(r'Description:\s*(.+?)(?:\n|Dependencies:|$)', details, re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else ""

                # Extract dependencies
                deps_match = re.search(r'Dependencies:\s*(.+?)(?:\n|$)', details)
                dependencies = []
                if deps_match:
                    deps_text = deps_match.group(1).strip()
                    dependencies = [d.strip() for d in deps_text.split(',') if d.strip() and d.strip().lower() != 'none']

                subtasks.append(Subtask(
                    name=name,
                    description=description,
                    complexity=complexity,
                    dependencies=dependencies
                ))

        # Extract strategy
        strategy_match = re.search(r'LOOP_STRATEGY:\s*(\w+)', decomposition_text)
        if strategy_match:
            strategy_type = strategy_match.group(1).strip()

        # Calculate estimated turns
        total_turns = self._estimate_total_turns(subtasks, strategy_type)

        # Identify parallel opportunities
        parallel_groups = self._identify_parallel_groups(subtasks)

        strategy = ExecutionStrategy(
            strategy_type=strategy_type,
            total_estimated_turns=total_turns,
            parallel_groups=parallel_groups,
            reasoning=self._extract_reasoning(decomposition_text)
        )

        self.subtasks = subtasks
        self.execution_strategy = strategy

        logger.info(f"Parsed {len(subtasks)} subtasks, strategy: {strategy_type}")
        return subtasks, strategy

    def generate_execution_prompts(self) -> List[Dict[str, Any]]:
        """
        Generate dynamic execution prompts based on strategy and subtasks

        Returns list of turn configurations that can be executed
        """
        if not self.subtasks or not self.execution_strategy:
            raise ValueError("Must parse decomposition first")

        prompts = []

        if self.execution_strategy.strategy_type == "single_loop":
            prompts = self._generate_single_loop_prompts()
        elif self.execution_strategy.strategy_type == "one_loop_per_task":
            prompts = self._generate_per_task_loop_prompts()
        elif self.execution_strategy.strategy_type == "mixed":
            prompts = self._generate_mixed_prompts()
        else:
            logger.warning(f"Unknown strategy: {self.execution_strategy.strategy_type}, falling back to single loop")
            prompts = self._generate_single_loop_prompts()

        logger.info(f"Generated {len(prompts)} execution prompts")
        return prompts

    def _generate_single_loop_prompts(self) -> List[Dict[str, Any]]:
        """Generate prompts for single loop execution"""
        prompts = []

        for i, subtask in enumerate(self.subtasks):
            # Executor prompt
            prompts.append({
                "role": f"execute_{subtask.name}",
                "participant": "grok" if i % 2 == 0 else "claude",
                "template": self._create_executor_prompt(subtask),
                "context_from": self._get_dependency_turn_numbers(subtask, prompts),
                "subtask_name": subtask.name
            })

            # Quick validation for moderate/complex tasks
            if subtask.complexity in ["moderate", "complex"]:
                prompts.append({
                    "role": f"validate_{subtask.name}",
                    "participant": "claude" if i % 2 == 0 else "grok",
                    "template": self._create_validator_prompt(subtask),
                    "context_from": [len(prompts)],  # Previous turn
                    "subtask_name": subtask.name
                })

        # Final synthesis
        prompts.append({
            "role": "final_synthesis",
            "participant": "claude",
            "template": self._create_synthesis_prompt(),
            "context_from": list(range(1, len(prompts) + 1))
        })

        return prompts

    def _generate_per_task_loop_prompts(self) -> List[Dict[str, Any]]:
        """Generate prompts for one loop per complex task"""
        prompts = []

        for subtask in self.subtasks:
            if subtask.complexity == "simple":
                # Simple tasks get single execution
                prompts.append({
                    "role": f"execute_{subtask.name}",
                    "participant": "grok",
                    "template": self._create_executor_prompt(subtask),
                    "context_from": self._get_dependency_turn_numbers(subtask, prompts)
                })
            else:
                # Complex tasks get full loop: Research → Execute → Validate → Refine (if needed)
                loop_prompts = self._create_task_loop(subtask, len(prompts))
                prompts.extend(loop_prompts)

        # Final synthesis
        prompts.append({
            "role": "final_synthesis",
            "participant": "claude",
            "template": self._create_synthesis_prompt(),
            "context_from": list(range(1, len(prompts) + 1))
        })

        return prompts

    def _generate_mixed_prompts(self) -> List[Dict[str, Any]]:
        """Generate prompts for mixed strategy"""
        prompts = []

        # Batch simple tasks
        simple_tasks = [st for st in self.subtasks if st.complexity == "simple"]
        if simple_tasks:
            prompts.append({
                "role": "batch_simple_tasks",
                "participant": "grok",
                "template": self._create_batch_prompt(simple_tasks),
                "context_from": []
            })

        # Individual loops for complex tasks
        complex_tasks = [st for st in self.subtasks if st.complexity in ["moderate", "complex"]]
        for subtask in complex_tasks:
            loop_prompts = self._create_task_loop(subtask, len(prompts))
            prompts.extend(loop_prompts)

        # Final synthesis
        prompts.append({
            "role": "final_synthesis",
            "participant": "claude",
            "template": self._create_synthesis_prompt(),
            "context_from": list(range(1, len(prompts) + 1))
        })

        return prompts

    def _create_task_loop(self, subtask: Subtask, start_index: int) -> List[Dict[str, Any]]:
        """Create a mini-loop for a complex subtask"""
        return [
            {
                "role": f"research_{subtask.name}",
                "participant": "grok",
                "grok_model": "grok-4-fast",
                "template": f"**RESEARCH: {subtask.name}**\n\n{subtask.description}\n\nResearch necessary background and gather information needed to complete this subtask effectively.",
                "context_from": self._get_dependency_turn_numbers(subtask, [])
            },
            {
                "role": f"execute_{subtask.name}",
                "participant": "claude",
                "template": self._create_executor_prompt(subtask, with_research=True),
                "context_from": [start_index + 1]
            },
            {
                "role": f"validate_{subtask.name}",
                "participant": "grok",
                "template": self._create_validator_prompt(subtask),
                "context_from": [start_index + 2]
            }
        ]

    def _create_executor_prompt(self, subtask: Subtask, with_research: bool = False) -> str:
        """Create execution prompt for a subtask"""
        prompt = f"**EXECUTE SUBTASK: {subtask.name}**\n\n"
        prompt += f"Description: {subtask.description}\n"
        prompt += f"Complexity: {subtask.complexity}\n\n"

        if with_research:
            prompt += "Based on the research provided, "

        prompt += "execute this subtask:\n\n"
        prompt += "1. **Understand what's needed**\n"
        prompt += "   - Clarify requirements\n"
        prompt += "   - Identify success criteria\n\n"
        prompt += "2. **Execute the task**\n"
        prompt += "   - Provide concrete outputs\n"
        prompt += "   - Be thorough and accurate\n\n"
        prompt += "3. **Document results**\n"
        prompt += "   - What was accomplished?\n"
        prompt += "   - What outputs/artifacts created?\n"
        prompt += "   - What context needed for next steps?\n\n"
        prompt += "Provide clear, actionable results."

        return prompt

    def _create_validator_prompt(self, subtask: Subtask) -> str:
        """Create validation prompt"""
        return f"""**VALIDATE: {subtask.name}**

Review the execution results and validate:

1. **Completeness**
   - Was the subtask fully completed?
   - What's missing or needs improvement?

2. **Quality Check**
   - Does it meet the requirements?
   - Are there errors or issues?

3. **Decision**
   Provide structured response:
   ```
   STATUS: [complete | needs_refinement | incomplete]
   ISSUES: [list any problems or none]
   RECOMMENDATION: [proceed | refine | redo]
   ```

Be thorough but fair."""

    def _create_synthesis_prompt(self) -> str:
        """Create final synthesis prompt"""
        subtask_list = "\n".join(f"- {st.name}: {st.description}" for st in self.subtasks)

        return f"""**FINAL SYNTHESIS**

All subtasks completed:
{subtask_list}

Synthesize complete solution:

1. **Integration**
   - Combine all subtask results into cohesive solution
   - Resolve any conflicts or gaps
   - Ensure completeness

2. **Quality Assessment**
   - Does this solve the original task?
   - What are the strengths?
   - What are the limitations?

3. **Deliverables**
   - Provide complete, ready-to-use output
   - Include necessary documentation
   - Suggest next steps if applicable

4. **Reflection**
   - Was the approach effective?
   - What worked well?
   - What could be improved?

Provide comprehensive, actionable results."""

    def _create_batch_prompt(self, simple_tasks: List[Subtask]) -> str:
        """Create prompt for batching simple tasks"""
        task_list = "\n".join(f"{i+1}. {st.name}: {st.description}"
                               for i, st in enumerate(simple_tasks))

        return f"""**BATCH EXECUTION: Simple Tasks**

Execute the following straightforward tasks:

{task_list}

For each task:
1. Complete it efficiently
2. Provide clear output
3. Note any issues

Batch results in structured format."""

    def _estimate_total_turns(self, subtasks: List[Subtask], strategy: str) -> int:
        """Estimate total turns needed"""
        if strategy == "single_loop":
            return len(subtasks) + sum(1 for st in subtasks if st.complexity != "simple") + 1  # +1 for synthesis

        elif strategy == "one_loop_per_task":
            simple = len([st for st in subtasks if st.complexity == "simple"])
            complex = len([st for st in subtasks if st.complexity in ["moderate", "complex"]])
            return simple + (complex * 3) + 1  # 3 turns per complex task + synthesis

        elif strategy == "mixed":
            simple = len([st for st in subtasks if st.complexity == "simple"])
            complex = len([st for st in subtasks if st.complexity in ["moderate", "complex"]])
            return 1 + (complex * 3) + 1  # 1 batch turn + complex loops + synthesis

        return len(subtasks) + 1

    def _identify_parallel_groups(self, subtasks: List[Subtask]) -> List[List[str]]:
        """Identify which subtasks can run in parallel"""
        # Simple implementation: tasks with no dependencies can run in parallel
        no_deps = [st.name for st in subtasks if not st.dependencies]

        if len(no_deps) > 1:
            return [no_deps]
        return []

    def _get_dependency_turn_numbers(self, subtask: Subtask, existing_prompts: List[Dict]) -> List[int]:
        """Get turn numbers for subtask dependencies"""
        turn_numbers = []

        for dep_name in subtask.dependencies:
            # Find the turn that executed this dependency
            for i, prompt in enumerate(existing_prompts):
                if prompt.get("subtask_name") == dep_name:
                    turn_numbers.append(i + 1)
                    break

        return turn_numbers

    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning from decomposition"""
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n\n|$)', text, re.DOTALL)
        return reasoning_match.group(1).strip() if reasoning_match else ""

    def adapt_on_failure(self, subtask_name: str, failure_reason: str) -> Dict[str, Any]:
        """
        Generate adaptive response when a subtask fails

        Claude can use this to decide what to do next
        """
        subtask = next((st for st in self.subtasks if st.name == subtask_name), None)
        if not subtask:
            return {"action": "skip", "reason": "Subtask not found"}

        # Generate adaptive prompt
        if "incomplete" in failure_reason.lower():
            return {
                "action": "refine",
                "prompt": self._create_refinement_prompt(subtask, failure_reason)
            }
        elif "error" in failure_reason.lower() or "incorrect" in failure_reason.lower():
            return {
                "action": "redo",
                "prompt": self._create_executor_prompt(subtask)
            }
        else:
            return {
                "action": "continue",
                "note": "Minor issues, proceeding"
            }

    def _create_refinement_prompt(self, subtask: Subtask, issues: str) -> str:
        """Create prompt for refining previous attempt"""
        return f"""**REFINE: {subtask.name}**

Previous attempt had issues:
{issues}

Refine and improve:
1. Address the specific issues raised
2. Enhance quality and completeness
3. Provide improved output

Focus on fixing what was problematic."""
