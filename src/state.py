"""
State Management

Simple JSON-based conversation state persistence
"""

import json
import logging
from pathlib import Path
from typing import Optional, List
from dataclasses import asdict

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages conversation state persistence

    Simple file-based approach using JSON. Can be enhanced
    with SQLite later if needed.
    """

    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"State manager initialized: {self.sessions_dir}")

    def save_conversation(self, conversation) -> Path:
        """
        Save complete conversation to JSON

        Args:
            conversation: Conversation object

        Returns:
            Path to saved file
        """
        file_path = self.sessions_dir / f"{conversation.session_id}.json"

        data = {
            "session_id": conversation.session_id,
            "mode": conversation.mode,
            "topic": conversation.topic,
            "started_at": conversation.started_at,
            "completed_at": conversation.completed_at,
            "metadata": conversation.metadata,
            "turns": [asdict(turn) for turn in conversation.turns]
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Conversation saved: {file_path}")
        return file_path

    def load_conversation(self, session_id: str):
        """
        Load conversation from JSON

        Args:
            session_id: Session identifier

        Returns:
            Conversation object
        """
        from .protocol import Conversation, Turn

        file_path = self.sessions_dir / f"{session_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        with open(file_path) as f:
            data = json.load(f)

        # Reconstruct conversation
        turns = [Turn(**turn_data) for turn_data in data["turns"]]

        conversation = Conversation(
            session_id=data["session_id"],
            mode=data["mode"],
            topic=data["topic"],
            turns=turns,
            metadata=data["metadata"],
            started_at=data["started_at"],
            completed_at=data.get("completed_at")
        )

        logger.info(f"Conversation loaded: {session_id}")
        return conversation

    def save_turn(self, session_id: str, turn) -> None:
        """
        Incrementally save a turn (for resumability)

        Args:
            session_id: Session identifier
            turn: Turn object
        """
        # Load existing conversation
        try:
            conversation = self.load_conversation(session_id)
        except FileNotFoundError:
            # First turn - create new conversation
            from .protocol import Conversation
            conversation = Conversation(
                session_id=session_id,
                mode="unknown",
                topic="",
                turns=[],
                metadata={},
                started_at=turn.timestamp
            )

        # Add turn if not already present
        if not any(t.number == turn.number for t in conversation.turns):
            conversation.turns.append(turn)

        # Save
        self.save_conversation(conversation)

    def list_sessions(self, limit: int = 20) -> List[dict]:
        """
        List recent sessions

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session metadata dicts
        """
        sessions = []

        # Get all session files, sorted by modification time
        session_files = sorted(
            self.sessions_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for file_path in session_files[:limit]:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                sessions.append({
                    "session_id": data["session_id"],
                    "mode": data["mode"],
                    "topic": data["topic"],
                    "turns": len(data["turns"]),
                    "started_at": data["started_at"],
                    "completed_at": data.get("completed_at"),
                    "status": "completed" if data.get("completed_at") else "in_progress"
                })

            except Exception as e:
                logger.warning(f"Error loading session {file_path}: {e}")
                continue

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        file_path = self.sessions_dir / f"{session_id}.json"

        if file_path.exists():
            file_path.unlink()
            logger.info(f"Session deleted: {session_id}")
            return True
        else:
            logger.warning(f"Session not found for deletion: {session_id}")
            return False

    def export_markdown(self, conversation, output_path: Optional[Path] = None) -> Path:
        """
        Export conversation to markdown

        Args:
            conversation: Conversation object
            output_path: Optional custom output path

        Returns:
            Path to markdown file
        """
        from .protocol import ProtocolEngine

        if output_path is None:
            output_path = self.sessions_dir / f"{conversation.session_id}.md"

        # Use protocol engine's markdown exporter
        engine = ProtocolEngine(None, None, self)
        markdown = engine.export_to_markdown(conversation)

        with open(output_path, "w") as f:
            f.write(markdown)

        logger.info(f"Markdown exported: {output_path}")
        return output_path
