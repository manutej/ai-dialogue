"""
AI Dialogue Protocol - Core Engine

Orchestrates multi-turn conversations between Claude and Grok
with configurable interaction modes.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Turn:
    """Single turn in a conversation"""
    number: int
    role: str
    participant: str
    prompt: str
    response: str
    tokens: Dict[str, int]
    latency: float
    timestamp: str
    context_from: List[int]


@dataclass
class Conversation:
    """Complete conversation session"""
    session_id: str
    mode: str
    topic: str
    turns: List[Turn]
    metadata: Dict
    started_at: str
    completed_at: Optional[str] = None


class ProtocolEngine:
    """
    Core protocol orchestration engine

    Handles:
    - Mode config loading
    - Turn execution (async)
    - Context management
    - State persistence
    """

    def __init__(self, claude_client, grok_client, state_manager):
        self.claude = claude_client
        self.grok = grok_client
        self.state = state_manager
        self.modes_dir = Path(__file__).parent / "modes"

    def load_mode(self, mode_name: str) -> Dict:
        """Load mode configuration from JSON"""
        mode_path = self.modes_dir / f"{mode_name}.json"
        if not mode_path.exists():
            raise ValueError(f"Mode '{mode_name}' not found at {mode_path}")

        with open(mode_path) as f:
            return json.load(f)

    async def run_protocol(
        self,
        mode: str,
        topic: str,
        turns: Optional[int] = None,
        custom_config: Optional[Dict] = None
    ) -> Conversation:
        """
        Execute complete protocol

        Args:
            mode: Mode name (loop, debate, podcast, etc.) or "custom"
            topic: Topic to discuss
            turns: Override number of turns
            custom_config: Custom mode config (for mode="custom")

        Returns:
            Completed conversation with all turns
        """
        # Load config
        if mode == "custom" and custom_config:
            config = custom_config
        else:
            config = self.load_mode(mode)

        # Override turns if specified
        if turns:
            config["turns"] = turns

        # Initialize conversation
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        conversation = Conversation(
            session_id=session_id,
            mode=mode,
            topic=topic,
            turns=[],
            metadata=config.get("metadata", {}),
            started_at=datetime.now().isoformat()
        )

        logger.info(f"Starting {mode} mode conversation: {topic}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Turns: {config['turns']}")

        # Execute turns based on structure
        structure = config.get("structure", "sequential")

        if structure == "sequential":
            await self._execute_sequential(conversation, config, topic)
        elif structure == "parallel":
            await self._execute_parallel(conversation, config, topic)
        elif structure == "mixed":
            await self._execute_mixed(conversation, config, topic)
        else:
            raise ValueError(f"Unknown structure: {structure}")

        conversation.completed_at = datetime.now().isoformat()
        logger.info(f"Conversation completed: {len(conversation.turns)} turns")

        return conversation

    async def _execute_sequential(
        self,
        conversation: Conversation,
        config: Dict,
        topic: str
    ):
        """Execute turns sequentially with context building"""
        context_history = {}

        for turn_num in range(1, config["turns"] + 1):
            turn_key = f"turn_{turn_num}"

            if turn_key not in config["prompts"]:
                logger.warning(f"No config for {turn_key}, using default")
                continue

            turn_config = config["prompts"][turn_key]

            # Build context from previous turns
            context = self._build_context(
                conversation,
                turn_config.get("context_from", [])
            )

            # Execute turn
            turn = await self._execute_turn(
                turn_num,
                turn_config,
                topic,
                context
            )

            conversation.turns.append(turn)
            self.state.save_turn(conversation.session_id, turn)

            logger.info(f"Turn {turn_num} completed: {turn.participant}")

    async def _execute_parallel(
        self,
        conversation: Conversation,
        config: Dict,
        topic: str
    ):
        """Execute independent turns in parallel"""
        tasks = []

        for turn_num in range(1, config["turns"] + 1):
            turn_key = f"turn_{turn_num}"

            if turn_key not in config["prompts"]:
                continue

            turn_config = config["prompts"][turn_key]

            # Create async task for each turn
            task = self._execute_turn(
                turn_num,
                turn_config,
                topic,
                {}  # No context in parallel mode
            )
            tasks.append(task)

        # Execute all turns concurrently
        turns = await asyncio.gather(*tasks)

        # Add to conversation
        for turn in turns:
            conversation.turns.append(turn)
            self.state.save_turn(conversation.session_id, turn)

        logger.info(f"Parallel execution completed: {len(turns)} turns")

    async def _execute_mixed(
        self,
        conversation: Conversation,
        config: Dict,
        topic: str
    ):
        """Execute with mixed parallel/sequential phases"""
        phases = config.get("phases", [])

        for phase in phases:
            phase_type = phase.get("type", "sequential")
            turn_range = phase.get("turns", [])

            if phase_type == "parallel":
                # Execute phase turns in parallel
                tasks = []
                for turn_num in turn_range:
                    turn_key = f"turn_{turn_num}"
                    if turn_key in config["prompts"]:
                        turn_config = config["prompts"][turn_key]
                        task = self._execute_turn(turn_num, turn_config, topic, {})
                        tasks.append(task)

                phase_turns = await asyncio.gather(*tasks)
                for turn in phase_turns:
                    conversation.turns.append(turn)
                    self.state.save_turn(conversation.session_id, turn)

            else:  # sequential
                for turn_num in turn_range:
                    turn_key = f"turn_{turn_num}"
                    if turn_key in config["prompts"]:
                        turn_config = config["prompts"][turn_key]
                        context = self._build_context(
                            conversation,
                            turn_config.get("context_from", [])
                        )
                        turn = await self._execute_turn(turn_num, turn_config, topic, context)
                        conversation.turns.append(turn)
                        self.state.save_turn(conversation.session_id, turn)

    async def _execute_turn(
        self,
        turn_num: int,
        turn_config: Dict,
        topic: str,
        context: Dict
    ) -> Turn:
        """Execute a single turn"""
        start_time = asyncio.get_event_loop().time()

        # Build prompt from template
        template = turn_config.get("template", "")
        prompt = template.format(topic=topic, **context)

        # Add role instruction if specified
        if "role_instruction" in turn_config:
            prompt = f"{turn_config['role_instruction']}\n\n{prompt}"

        participant = turn_config.get("participant", "claude")

        logger.debug(f"Turn {turn_num}: {participant}")
        logger.debug(f"Prompt: {prompt[:100]}...")

        # Call appropriate client
        if participant == "claude":
            response, tokens = await self.claude.chat(prompt)
        elif participant == "grok":
            model = turn_config.get("grok_model", "grok-4-fast")
            response, tokens = await self.grok.chat(prompt, model=model)
        else:
            raise ValueError(f"Unknown participant: {participant}")

        end_time = asyncio.get_event_loop().time()
        latency = end_time - start_time

        return Turn(
            number=turn_num,
            role=turn_config.get("role", ""),
            participant=participant,
            prompt=prompt,
            response=response,
            tokens=tokens,
            latency=latency,
            timestamp=datetime.now().isoformat(),
            context_from=turn_config.get("context_from", [])
        )

    def _build_context(
        self,
        conversation: Conversation,
        context_from: List[int]
    ) -> Dict:
        """Build context dictionary from previous turns"""
        context = {}

        for turn_num in context_from:
            # Find turn by number
            turn = next(
                (t for t in conversation.turns if t.number == turn_num),
                None
            )

            if turn:
                context[f"turn_{turn_num}"] = turn.response
                context[f"turn_{turn_num}_participant"] = turn.participant

        return context

    def export_to_markdown(self, conversation: Conversation) -> str:
        """Export conversation to markdown format"""
        md = f"# AI Dialogue: {conversation.topic} ({conversation.mode.title()} Mode)\n\n"
        md += f"**Session**: {conversation.session_id}\n"
        md += f"**Mode**: {conversation.mode}\n"
        md += f"**Turns**: {len(conversation.turns)}\n"
        md += f"**Started**: {conversation.started_at}\n"
        md += f"**Completed**: {conversation.completed_at}\n\n"
        md += "---\n\n"

        for turn in conversation.turns:
            md += f"## Turn {turn.number}: {turn.role.title()} ({turn.participant.title()})\n\n"
            md += f"**Timestamp**: {turn.timestamp}\n"
            md += f"**Tokens**: {turn.tokens.get('prompt', 0)} prompt, "
            md += f"{turn.tokens.get('completion', 0)} completion\n"
            md += f"**Latency**: {turn.latency:.2f}s\n"

            if turn.context_from:
                md += f"**Context From**: Turns {', '.join(map(str, turn.context_from))}\n"

            md += f"\n{turn.response}\n\n"
            md += "---\n\n"

        return md
