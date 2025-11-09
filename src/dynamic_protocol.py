"""
Dynamic Protocol Engine

Supports adaptive workflows with template chains, cycles, and self-modifying prompts
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .protocol import ProtocolEngine, Conversation, Turn

logger = logging.getLogger(__name__)


@dataclass
class CycleConfig:
    """Configuration for cycle execution"""
    max_cycles: int = 3
    convergence_threshold: Optional[float] = None
    cycle_prompt_template: Optional[str] = None


class DynamicProtocolEngine(ProtocolEngine):
    """
    Enhanced protocol engine with dynamic capabilities

    Features:
    - Template variable substitution (<TASK>, <RESULT>, etc.)
    - Dynamic prompt modification based on results
    - Cycle support (loops of loops)
    - Conditional step execution
    - Adaptive workflows that modify themselves
    """

    def __init__(self, claude_client, grok_client, state_manager):
        super().__init__(claude_client, grok_client, state_manager)
        self.context_store = {}  # Persistent context across turns

    async def run_dynamic_protocol(
        self,
        mode: str,
        task: str,
        variables: Optional[Dict[str, Any]] = None,
        cycle_config: Optional[CycleConfig] = None
    ) -> Conversation:
        """
        Execute dynamic protocol with template substitution

        Args:
            mode: Mode name (pipeline, dynamic, etc.)
            task: Primary task description (fills <TASK>)
            variables: Additional template variables
            cycle_config: Configuration for cycle execution

        Returns:
            Completed conversation
        """
        # Initialize variables
        self.context_store = {
            "TASK": task,
            "CYCLE": 0,
            **(variables or {})
        }

        if cycle_config and cycle_config.max_cycles > 1:
            return await self._execute_cycles(mode, task, cycle_config)
        else:
            return await self._execute_single_run(mode, task)

    async def _execute_cycles(
        self,
        mode: str,
        task: str,
        cycle_config: CycleConfig
    ) -> Conversation:
        """Execute multiple cycles until convergence or max cycles"""
        all_turns = []
        cycle = 1

        while cycle <= cycle_config.max_cycles:
            logger.info(f"Starting cycle {cycle}/{cycle_config.max_cycles}")

            # Update cycle number in context
            self.context_store["CYCLE"] = cycle
            self.context_store["PREVIOUS_CYCLE_SUMMARY"] = self._get_previous_cycle_summary(all_turns)

            # Run single cycle
            conversation = await self._execute_single_run(mode, task)
            all_turns.extend(conversation.turns)

            # Check convergence
            if cycle_config.convergence_threshold:
                if self._check_convergence(all_turns, cycle_config.convergence_threshold):
                    logger.info(f"Convergence reached at cycle {cycle}")
                    break

            cycle += 1

        # Create final conversation with all cycles
        from datetime import datetime
        final_conversation = Conversation(
            session_id=f"{conversation.session_id}-cycles",
            mode=f"{mode}-cyclic",
            topic=task,
            turns=all_turns,
            metadata={"cycles": cycle - 1, "config": cycle_config.__dict__},
            started_at=all_turns[0].timestamp if all_turns else datetime.now().isoformat(),
            completed_at=datetime.now().isoformat()
        )

        return final_conversation

    async def _execute_single_run(
        self,
        mode: str,
        task: str
    ) -> Conversation:
        """Execute single run with dynamic templates"""
        config = self.load_mode(mode)

        # Execute using base protocol but with dynamic template substitution
        conversation = await self.run_protocol(
            mode=mode,
            topic=task,
            turns=config.get("turns"),
            custom_config=None
        )

        return conversation

    async def _execute_turn(
        self,
        turn_num: int,
        turn_config: Dict,
        topic: str,
        context: Dict
    ) -> Turn:
        """
        Execute turn with dynamic template substitution

        Overrides base method to add template variable support
        """
        # Build prompt with template substitution
        template = turn_config.get("template", "")

        # Substitute context variables first
        prompt = template.format(topic=topic, **context)

        # Substitute stored context variables (TASK, RESULT, etc.)
        prompt = self._substitute_variables(prompt, self.context_store)

        # Check for dynamic modification instructions
        if turn_config.get("dynamic", False):
            prompt = await self._apply_dynamic_modifications(prompt, turn_num)

        # Update turn config with modified prompt
        modified_config = turn_config.copy()
        modified_config["template"] = prompt

        # Execute turn using base implementation
        turn = await super()._execute_turn(
            turn_num,
            modified_config,
            topic,
            {}  # Context already substituted
        )

        # Store results for future template substitution
        self._update_context_store(turn)

        return turn

    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute template variables like <TASK>, <RESULT>, etc.

        Example:
            "Analyze <TASK> and synthesize <PREVIOUS_RESULT>"
            -> "Analyze quantum computing and synthesize [previous result]"
        """
        pattern = r'<([A-Z_]+)>'

        def replacer(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(pattern, replacer, template)

    async def _apply_dynamic_modifications(self, prompt: str, turn_num: int) -> str:
        """
        Apply dynamic modifications to prompt based on previous results

        This allows prompts to adapt themselves based on what's been learned
        """
        # Check if we need to modify based on previous turn insights
        if turn_num > 1 and "ADAPTIVE_INSTRUCTION" in self.context_store:
            adaptive_instruction = self.context_store["ADAPTIVE_INSTRUCTION"]
            prompt = f"{adaptive_instruction}\n\n{prompt}"

        return prompt

    def _update_context_store(self, turn: Turn):
        """
        Update context store with turn results

        Extracts key information for future template substitution
        """
        # Store last result
        self.context_store[f"TURN_{turn.number}_RESULT"] = turn.response

        # Store by role if specified
        if turn.role:
            role_key = turn.role.upper().replace(" ", "_")
            self.context_store[f"LAST_{role_key}"] = turn.response

        # Extract any adaptive instructions from response
        # Look for markers like "NEXT_STEP:" or "MODIFY_APPROACH:"
        self._extract_adaptive_instructions(turn.response)

    def _extract_adaptive_instructions(self, response: str):
        """
        Extract adaptive instructions from AI responses

        Looks for special markers that indicate workflow modifications
        """
        markers = {
            "NEXT_STEP:": "ADAPTIVE_INSTRUCTION",
            "MODIFY_APPROACH:": "ADAPTIVE_INSTRUCTION",
            "CHANGE_DIRECTION:": "ADAPTIVE_INSTRUCTION"
        }

        for marker, key in markers.items():
            if marker in response:
                # Extract instruction after marker
                parts = response.split(marker, 1)
                if len(parts) > 1:
                    instruction = parts[1].split("\n")[0].strip()
                    self.context_store[key] = instruction
                    logger.info(f"Extracted adaptive instruction: {instruction}")

    def _get_previous_cycle_summary(self, all_turns: List[Turn]) -> str:
        """Generate summary of previous cycles for context"""
        if not all_turns:
            return "This is the first cycle."

        # Get last few turns
        recent_turns = all_turns[-3:] if len(all_turns) >= 3 else all_turns

        summary = "Previous cycle summary:\n"
        for turn in recent_turns:
            summary += f"- {turn.role}: {turn.response[:200]}...\n"

        return summary

    def _check_convergence(self, all_turns: List[Turn], threshold: float) -> bool:
        """
        Check if cycles have converged

        Simple implementation: compare last two cycles
        """
        if len(all_turns) < 10:  # Need at least 2 cycles of 5+ turns
            return False

        # Compare similarity of last cycle vs previous cycle
        # This is a placeholder - could be enhanced with semantic similarity
        mid_point = len(all_turns) // 2
        prev_cycle_responses = " ".join(t.response for t in all_turns[:mid_point])
        curr_cycle_responses = " ".join(t.response for t in all_turns[mid_point:])

        # Simple word overlap metric
        prev_words = set(prev_cycle_responses.lower().split())
        curr_words = set(curr_cycle_responses.lower().split())

        overlap = len(prev_words & curr_words) / len(prev_words | curr_words)

        logger.debug(f"Convergence check: overlap={overlap:.3f}, threshold={threshold}")

        return overlap >= threshold
