"""
AI Dialogue Protocol - Core Engine

Orchestrates multi-turn conversations between Claude and Grok
with configurable interaction modes.

Phase 3 Features:
- Parallel turn execution with dependency management
- Exponential backoff retry logic for transient failures
- Per-turn timeout handling
- Token and cost tracking per model
- Streaming output support
"""

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger(__name__)


# ============ MODEL PRICING (per 1M tokens) ============
MODEL_PRICING = {
    "grok-4-fast-reasoning-latest": {"input": 2.0, "output": 10.0},
    "grok-4-fast-reasoning": {"input": 2.0, "output": 10.0},
    "grok-4-fast-non-reasoning-latest": {"input": 1.0, "output": 5.0},
    "grok-4-fast-non-reasoning": {"input": 1.0, "output": 5.0},
    "grok-code-fast-1": {"input": 3.0, "output": 15.0},
    "grok-2-vision-latest": {"input": 2.0, "output": 10.0},
    "grok-2-image-latest": {"input": 5.0, "output": 20.0},
}

# Claude models (from Anthropic)
MODEL_PRICING.update({
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
})


def calculate_cost(model: str, tokens: Dict[str, int]) -> float:
    """
    Calculate cost for a turn based on model and token usage.

    Args:
        model: Model identifier
        tokens: Token usage dict with 'prompt' and 'completion' keys

    Returns:
        Cost in USD (rounded to 4 decimal places)
    """
    if model not in MODEL_PRICING:
        logger.warning(f"Model {model} not in pricing table, using default (grok-4)")
        model = "grok-4-fast-reasoning-latest"

    pricing = MODEL_PRICING[model]
    prompt_tokens = tokens.get("prompt", 0)
    completion_tokens = tokens.get("completion", 0)

    # Cost = (tokens / 1M) * price_per_1M
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]

    total_cost = input_cost + output_cost
    return round(total_cost, 6)


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
    cost: float = 0.0
    model: str = ""
    error: Optional[str] = None
    retry_count: int = 0


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
    total_cost: float = 0.0
    total_tokens: int = 0

    def update_costs(self):
        """Recalculate total cost and tokens from turns"""
        self.total_cost = sum(turn.cost for turn in self.turns)
        self.total_tokens = sum(turn.tokens.get("total", 0) for turn in self.turns)


class ProtocolEngine:
    """
    Core protocol orchestration engine

    Handles:
    - Mode config loading
    - Turn execution (async) with retry logic and timeouts
    - Context management
    - State persistence
    - Cost and token tracking

    Phase 3 Features:
    - Exponential backoff retry (default: 3 max attempts)
    - Per-turn timeout (default: 30s)
    - Automatic cost calculation
    - Token usage tracking
    """

    def __init__(
        self,
        claude_client,
        grok_client,
        state_manager,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        retry_backoff_base: float = 2.0
    ):
        self.claude = claude_client
        self.grok = grok_client
        self.state = state_manager
        self.modes_dir = Path(__file__).parent / "modes"

        # Phase 3 configuration
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.retry_backoff_base = retry_backoff_base

        logger.info(
            f"ProtocolEngine initialized: "
            f"max_retries={max_retries}, "
            f"timeout={timeout_seconds}s, "
            f"backoff_base={retry_backoff_base}"
        )

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
        conversation.update_costs()

        logger.info(f"Conversation completed: {len(conversation.turns)} turns")
        logger.info(f"Total tokens: {conversation.total_tokens:,}")
        logger.info(f"Total cost: ${conversation.total_cost:.6f}")

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
        """
        Execute a single turn with retry logic and timeout handling.

        Phase 3 Features:
        - Exponential backoff retry for transient failures
        - Per-turn timeout handling
        - Automatic cost calculation
        - Error tracking
        """
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

        # Get timeout and retries from config or use defaults
        timeout = turn_config.get("timeout_seconds", self.timeout_seconds)
        max_retries = turn_config.get("max_retries", self.max_retries)

        response = None
        tokens = {"prompt": 0, "completion": 0, "total": 0}
        error_msg = None
        retry_count = 0
        model_used = ""

        # Execute with retry logic
        for attempt in range(max_retries):
            try:
                # Select appropriate client
                if participant == "claude":
                    model_used = turn_config.get("claude_model", "claude-3-sonnet-20240229")
                elif participant == "grok":
                    model_used = turn_config.get("grok_model", "grok-4")
                else:
                    raise ValueError(f"Unknown participant: {participant}")

                # Execute with timeout
                if participant == "claude":
                    response, tokens = await asyncio.wait_for(
                        self.claude.chat(prompt),
                        timeout=timeout
                    )
                else:  # grok
                    response, tokens = await asyncio.wait_for(
                        self.grok.chat(prompt, model=model_used),
                        timeout=timeout
                    )

                logger.info(
                    f"Turn {turn_num} ({participant}) succeeded on attempt {attempt + 1}"
                )
                error_msg = None
                break

            except asyncio.TimeoutError:
                error_msg = f"Timeout after {timeout}s"
                retry_count = attempt + 1

                if attempt < max_retries - 1:
                    # Calculate backoff with jitter
                    wait_time = self.retry_backoff_base ** attempt
                    jitter = random.uniform(0, wait_time * 0.1)
                    wait_time += jitter

                    logger.warning(
                        f"Turn {turn_num} timed out. "
                        f"Retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Turn {turn_num} failed after {max_retries} attempts: {error_msg}")

            except Exception as e:
                error_msg = str(e)
                retry_count = attempt + 1

                # Check if error is retryable (transient)
                is_retryable = any([
                    "ConnectionError" in str(type(e)),
                    "TimeoutError" in str(type(e)),
                    "429" in error_msg,  # Rate limit
                ])

                if is_retryable and attempt < max_retries - 1:
                    # Calculate backoff with jitter
                    wait_time = self.retry_backoff_base ** attempt
                    jitter = random.uniform(0, wait_time * 0.1)
                    wait_time += jitter

                    logger.warning(
                        f"Turn {turn_num} transient error. "
                        f"Retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries}): {error_msg}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Turn {turn_num} failed: {error_msg}")
                    if not is_retryable:
                        logger.debug(f"Error is not retryable, giving up")
                    break

        end_time = asyncio.get_event_loop().time()
        latency = end_time - start_time

        # Calculate cost if we got tokens
        cost = 0.0
        if tokens.get("total", 0) > 0:
            cost = calculate_cost(model_used, tokens)

        return Turn(
            number=turn_num,
            role=turn_config.get("role", ""),
            participant=participant,
            prompt=prompt,
            response=response or f"[Error: {error_msg}]",
            tokens=tokens,
            latency=latency,
            timestamp=datetime.now().isoformat(),
            context_from=turn_config.get("context_from", []),
            cost=cost,
            model=model_used,
            error=error_msg,
            retry_count=retry_count
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
        """
        Export conversation to markdown format.

        Includes Phase 3 enhancements:
        - Per-turn cost tracking
        - Token usage breakdown
        - Error tracking with retry counts
        - Session cost summary
        """
        # Recalculate costs before export
        conversation.update_costs()

        md = f"# AI Dialogue: {conversation.topic} ({conversation.mode.title()} Mode)\n\n"
        md += f"**Session**: {conversation.session_id}\n"
        md += f"**Mode**: {conversation.mode}\n"
        md += f"**Turns**: {len(conversation.turns)}\n"
        md += f"**Started**: {conversation.started_at}\n"
        md += f"**Completed**: {conversation.completed_at}\n"
        md += f"**Total Tokens**: {conversation.total_tokens:,}\n"
        md += f"**Total Cost**: ${conversation.total_cost:.6f}\n"
        md += f"**Avg Cost per Turn**: ${conversation.total_cost / len(conversation.turns):.6f}\n\n"
        md += "---\n\n"

        for turn in conversation.turns:
            md += f"## Turn {turn.number}: {turn.role.title()} ({turn.participant.title()})\n\n"
            md += f"**Timestamp**: {turn.timestamp}\n"
            md += f"**Model**: {turn.model}\n"
            md += f"**Tokens**: {turn.tokens.get('prompt', 0)} prompt + "
            md += f"{turn.tokens.get('completion', 0)} completion = {turn.tokens.get('total', 0)} total\n"
            md += f"**Cost**: ${turn.cost:.6f}\n"
            md += f"**Latency**: {turn.latency:.2f}s\n"

            if turn.retry_count > 0:
                md += f"**Retries**: {turn.retry_count}\n"

            if turn.error:
                md += f"**Error**: {turn.error}\n"

            if turn.context_from:
                md += f"**Context From**: Turns {', '.join(map(str, turn.context_from))}\n"

            md += f"\n{turn.response}\n\n"
            md += "---\n\n"

        return md
