"""
Comprehensive StateManager Tests - Phase 4A

Tests for StateManager persistence, concurrency, recovery, and operations.
Covers JSON serialization, file management, and state lifecycle.
"""

import pytest
import json
import asyncio
from pathlib import Path
from datetime import datetime
from src.state import StateManager
from src.protocol import Conversation, Turn


# ============= FIXTURES =============

@pytest.fixture
def temp_sessions_dir(tmp_path):
    """Create temporary sessions directory for testing"""
    sessions_dir = tmp_path / "test_sessions"
    sessions_dir.mkdir()
    return sessions_dir


@pytest.fixture
def state_manager(temp_sessions_dir):
    """Create StateManager with temporary directory"""
    return StateManager(sessions_dir=str(temp_sessions_dir))


@pytest.fixture
def sample_turn():
    """Create a sample Turn for testing"""
    return Turn(
        number=1,
        role="foundation",
        participant="grok",
        prompt="Test prompt",
        response="Test response",
        tokens={"prompt": 100, "completion": 200, "total": 300},
        latency=1.5,
        timestamp=datetime.now().isoformat(),
        context_from=[],  # First turn, no context
        cost=0.001
    )


@pytest.fixture
def sample_conversation(sample_turn):
    """Create a sample Conversation for testing"""
    return Conversation(
        session_id="test-session-001",
        mode="loop",
        topic="Test Topic",
        turns=[sample_turn],
        metadata={"test": "data"},
        started_at=datetime.now().isoformat(),
        completed_at=None
    )


# ============= PERSISTENCE TESTS =============

class TestStatePersistence:
    """Test save/load operations and file persistence"""

    def test_save_and_load_conversation(self, state_manager, sample_conversation):
        """Test complete save/load cycle"""
        # Save conversation
        saved_path = state_manager.save_conversation(sample_conversation)

        assert saved_path.exists()
        assert saved_path.name == "test-session-001.json"

        # Load conversation back
        loaded_conversation = state_manager.load_conversation("test-session-001")

        # Verify all fields match
        assert loaded_conversation.session_id == sample_conversation.session_id
        assert loaded_conversation.mode == sample_conversation.mode
        assert loaded_conversation.topic == sample_conversation.topic
        assert len(loaded_conversation.turns) == len(sample_conversation.turns)
        assert loaded_conversation.metadata == sample_conversation.metadata
        assert loaded_conversation.started_at == sample_conversation.started_at

        # Verify turn data
        original_turn = sample_conversation.turns[0]
        loaded_turn = loaded_conversation.turns[0]
        assert loaded_turn.number == original_turn.number
        assert loaded_turn.role == original_turn.role
        assert loaded_turn.response == original_turn.response
        assert loaded_turn.tokens == original_turn.tokens

    def test_session_directory_structure(self, state_manager, sample_conversation):
        """Test that sessions are stored in correct directory structure"""
        state_manager.save_conversation(sample_conversation)

        # Verify file location
        expected_path = state_manager.sessions_dir / "test-session-001.json"
        assert expected_path.exists()

        # Verify JSON structure
        with open(expected_path) as f:
            data = json.load(f)

        assert "session_id" in data
        assert "mode" in data
        assert "turns" in data
        assert isinstance(data["turns"], list)

    def test_append_turns_to_existing_session(self, state_manager, sample_turn):
        """Test incrementally adding turns via save_turn"""
        session_id = "incremental-session"

        # Save first turn (creates new session)
        state_manager.save_turn(session_id, sample_turn)

        # Load and verify
        conversation = state_manager.load_conversation(session_id)
        assert len(conversation.turns) == 1
        assert conversation.turns[0].number == 1

        # Add second turn
        turn_2 = Turn(
            number=2,
            role="analysis",
            participant="claude",
            prompt="Second prompt",
            response="Second response",
            tokens={"prompt": 150, "completion": 250, "total": 400},
            latency=2.0,
            timestamp=datetime.now().isoformat(),
            context_from=[1],  # Builds on turn 1
            cost=0.002
        )

        state_manager.save_turn(session_id, turn_2)

        # Load and verify both turns
        conversation = state_manager.load_conversation(session_id)
        assert len(conversation.turns) == 2
        assert conversation.turns[1].number == 2
        assert conversation.turns[1].response == "Second response"

    def test_duplicate_turn_not_added(self, state_manager, sample_turn):
        """Test that duplicate turn numbers are not added"""
        session_id = "duplicate-test"

        # Save turn twice
        state_manager.save_turn(session_id, sample_turn)
        state_manager.save_turn(session_id, sample_turn)  # Duplicate

        # Load and verify only one turn exists
        conversation = state_manager.load_conversation(session_id)
        assert len(conversation.turns) == 1

    def test_list_all_sessions(self, state_manager):
        """Test listing multiple sessions"""
        # Create multiple conversations
        for i in range(5):
            conv = Conversation(
                session_id=f"session-{i:03d}",
                mode="loop",
                topic=f"Topic {i}",
                turns=[],
                metadata={},
                started_at=datetime.now().isoformat()
            )
            state_manager.save_conversation(conv)

        # List sessions
        sessions = state_manager.list_sessions(limit=10)

        assert len(sessions) == 5
        assert all("session_id" in s for s in sessions)
        assert all("mode" in s for s in sessions)
        assert all("status" in s for s in sessions)

    def test_list_sessions_limit(self, state_manager):
        """Test that list_sessions respects limit"""
        # Create 10 sessions
        for i in range(10):
            conv = Conversation(
                session_id=f"session-{i:03d}",
                mode="loop",
                topic=f"Topic {i}",
                turns=[],
                metadata={},
                started_at=datetime.now().isoformat()
            )
            state_manager.save_conversation(conv)

        # Request only 3
        sessions = state_manager.list_sessions(limit=3)

        assert len(sessions) == 3

    def test_delete_session(self, state_manager, sample_conversation):
        """Test session deletion"""
        # Save session
        state_manager.save_conversation(sample_conversation)

        # Verify it exists
        assert state_manager.load_conversation("test-session-001")

        # Delete it
        result = state_manager.delete_session("test-session-001")
        assert result is True

        # Verify it's gone
        with pytest.raises(FileNotFoundError):
            state_manager.load_conversation("test-session-001")

    def test_delete_nonexistent_session(self, state_manager):
        """Test deleting a session that doesn't exist"""
        result = state_manager.delete_session("nonexistent-session")
        assert result is False


# ============= ERROR RECOVERY TESTS =============

class TestStateRecovery:
    """Test handling of corrupted/invalid state files"""

    def test_load_nonexistent_session_raises(self, state_manager):
        """Test that loading nonexistent session raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="Session not found"):
            state_manager.load_conversation("does-not-exist")

    def test_corrupted_json_file_handling(self, state_manager, temp_sessions_dir):
        """Test handling of corrupted JSON files"""
        # Create corrupted JSON file
        corrupted_file = temp_sessions_dir / "corrupted-session.json"
        with open(corrupted_file, "w") as f:
            f.write("{invalid json content")

        # Attempt to load should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            state_manager.load_conversation("corrupted-session")

    def test_list_sessions_skips_corrupted_files(self, state_manager, temp_sessions_dir, sample_conversation):
        """Test that list_sessions gracefully skips corrupted files"""
        # Save one valid session
        state_manager.save_conversation(sample_conversation)

        # Create corrupted session file
        corrupted_file = temp_sessions_dir / "corrupted.json"
        with open(corrupted_file, "w") as f:
            f.write("not valid json")

        # List sessions should return only valid one (and log warning)
        sessions = state_manager.list_sessions()

        # Should have 1 valid session (corrupted one skipped)
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "test-session-001"

    def test_missing_fields_in_loaded_conversation(self, state_manager, temp_sessions_dir):
        """Test handling of JSON with missing required fields"""
        # Create JSON with missing fields
        incomplete_data = {
            "session_id": "incomplete-session",
            "mode": "loop"
            # Missing: topic, turns, metadata, started_at
        }

        incomplete_file = temp_sessions_dir / "incomplete-session.json"
        with open(incomplete_file, "w") as f:
            json.dump(incomplete_data, f)

        # Attempt to load should raise KeyError
        with pytest.raises(KeyError):
            state_manager.load_conversation("incomplete-session")


# ============= MARKDOWN EXPORT TESTS =============

class TestMarkdownExport:
    """Test markdown export functionality"""

    def test_export_markdown_creates_file(self, state_manager, sample_conversation):
        """Test that markdown export creates .md file"""
        # Export to markdown
        md_path = state_manager.export_markdown(sample_conversation)

        assert md_path.exists()
        assert md_path.suffix == ".md"
        assert md_path.name == "test-session-001.md"

    def test_export_markdown_custom_path(self, state_manager, sample_conversation, temp_sessions_dir):
        """Test markdown export with custom output path"""
        custom_path = temp_sessions_dir / "custom_output.md"

        md_path = state_manager.export_markdown(sample_conversation, output_path=custom_path)

        assert md_path == custom_path
        assert custom_path.exists()

    def test_exported_markdown_contains_conversation_data(self, state_manager, sample_conversation):
        """Test that exported markdown contains conversation data"""
        md_path = state_manager.export_markdown(sample_conversation)

        with open(md_path) as f:
            content = f.read()

        # Should contain key conversation data
        assert sample_conversation.topic in content
        assert sample_conversation.mode in content
        assert sample_conversation.turns[0].response in content


# ============= CONCURRENCY TESTS =============

class TestStateConcurrency:
    """Test concurrent access patterns"""

    @pytest.mark.asyncio
    async def test_concurrent_writes_to_different_sessions(self, state_manager):
        """Test writing to different sessions concurrently"""
        async def save_session(session_num):
            conv = Conversation(
                session_id=f"concurrent-{session_num}",
                mode="loop",
                topic=f"Topic {session_num}",
                turns=[],
                metadata={},
                started_at=datetime.now().isoformat()
            )
            # StateManager is sync, but we can still test concurrent execution
            state_manager.save_conversation(conv)

        # Save 5 sessions concurrently
        tasks = [save_session(i) for i in range(5)]
        await asyncio.gather(*tasks)

        # Verify all saved
        sessions = state_manager.list_sessions()
        assert len(sessions) == 5

    def test_overwrite_existing_session(self, state_manager, sample_conversation):
        """Test that saving same session_id overwrites"""
        # Save original
        state_manager.save_conversation(sample_conversation)

        # Modify and save again
        sample_conversation.topic = "Updated Topic"
        state_manager.save_conversation(sample_conversation)

        # Load and verify update
        loaded = state_manager.load_conversation("test-session-001")
        assert loaded.topic == "Updated Topic"


# ============= EDGE CASES =============

class TestStateEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_conversation(self, state_manager):
        """Test saving conversation with no turns"""
        empty_conv = Conversation(
            session_id="empty-session",
            mode="loop",
            topic="Empty",
            turns=[],  # No turns
            metadata={},
            started_at=datetime.now().isoformat()
        )

        state_manager.save_conversation(empty_conv)
        loaded = state_manager.load_conversation("empty-session")

        assert len(loaded.turns) == 0

    def test_session_with_special_characters_in_topic(self, state_manager):
        """Test saving conversation with special characters"""
        special_conv = Conversation(
            session_id="special-chars",
            mode="loop",
            topic="Test: Special chars (quotes, 'apostrophes', and \"escapes\")",
            turns=[],
            metadata={"special": "chars & symbols <> / \\"},
            started_at=datetime.now().isoformat()
        )

        state_manager.save_conversation(special_conv)
        loaded = state_manager.load_conversation("special-chars")

        assert loaded.topic == special_conv.topic
        assert loaded.metadata == special_conv.metadata

    def test_large_conversation_with_many_turns(self, state_manager):
        """Test saving conversation with many turns"""
        # Create conversation with 100 turns
        turns = [
            Turn(
                number=i,
                role=f"role_{i}",
                participant="grok" if i % 2 == 0 else "claude",
                prompt=f"Prompt {i}",
                response=f"Response {i}" * 10,  # Make responses longer
                tokens={"prompt": 100, "completion": 200, "total": 300},
                latency=1.5,
                timestamp=datetime.now().isoformat(),
                context_from=list(range(max(0, i-2), i)),  # Context from previous 2 turns
                cost=0.001
            )
            for i in range(100)
        ]

        large_conv = Conversation(
            session_id="large-session",
            mode="loop",
            topic="Large Test",
            turns=turns,
            metadata={},
            started_at=datetime.now().isoformat()
        )

        state_manager.save_conversation(large_conv)
        loaded = state_manager.load_conversation("large-session")

        assert len(loaded.turns) == 100
        assert loaded.turns[99].number == 99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
