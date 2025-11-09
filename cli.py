#!/usr/bin/env python3
"""
AI Dialogue CLI

Command-line interface for async AI orchestration protocol
"""

import asyncio
import logging
import sys
from pathlib import Path

import click

from src.protocol import ProtocolEngine
from src.clients.claude import ClaudeClient
from src.clients.grok import GrokClient
from src.state import StateManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """AI Dialogue - Async AI orchestration protocol"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option('--mode', '-m', required=True,
              type=click.Choice(['loop', 'debate', 'podcast', 'dialogue', 'synthesis', 'custom']),
              help='Interaction mode')
@click.option('--topic', '-t', required=True, help='Topic to discuss')
@click.option('--turns', '-n', type=int, help='Number of turns (overrides mode default)')
@click.option('--config', '-c', type=click.Path(exists=True), help='Custom mode config (JSON)')
@click.option('--output', '-o', type=click.Path(), help='Output markdown file path')
@click.option('--claude-model', default='sonnet', help='Claude model (sonnet, opus, haiku)')
@click.option('--grok-model', default='grok-4-fast', help='Grok model (grok-4, grok-4-fast, grok-3)')
def run(mode, topic, turns, config, output, claude_model, grok_model):
    """
    Run a new AI dialogue protocol

    Examples:
        ai-dialogue run --mode loop --topic "quantum computing" --turns 8
        ai-dialogue run --mode debate --topic "AGI safety vs capability"
        ai-dialogue run --mode podcast --topic "Future of work"
    """
    asyncio.run(_run_protocol(mode, topic, turns, config, output, claude_model, grok_model))


async def _run_protocol(mode, topic, turns, config, output, claude_model, grok_model):
    """Async protocol execution"""
    try:
        # Initialize components
        claude_client = ClaudeClient(model=claude_model)
        grok_client = GrokClient(model=grok_model)
        state_manager = StateManager()
        engine = ProtocolEngine(claude_client, grok_client, state_manager)

        click.echo(f"\n🚀 Starting {mode} mode dialogue")
        click.echo(f"📝 Topic: {topic}")
        click.echo(f"🔄 Turns: {turns or 'default'}")
        click.echo()

        # Load custom config if provided
        custom_config = None
        if config:
            import json
            with open(config) as f:
                custom_config = json.load(f)

        # Run protocol
        conversation = await engine.run_protocol(
            mode=mode,
            topic=topic,
            turns=turns,
            custom_config=custom_config
        )

        # Save conversation
        session_path = state_manager.save_conversation(conversation)
        click.echo(f"\n✅ Conversation completed")
        click.echo(f"📁 Session: {conversation.session_id}")
        click.echo(f"💾 Saved to: {session_path}")

        # Export markdown
        if output:
            md_path = Path(output)
        else:
            md_path = None

        md_file = state_manager.export_markdown(conversation, md_path)
        click.echo(f"📄 Markdown: {md_file}")

        # Summary
        click.echo(f"\n📊 Summary:")
        click.echo(f"   Turns completed: {len(conversation.turns)}")

        total_tokens = sum(
            turn.tokens.get('total', 0)
            for turn in conversation.turns
        )
        click.echo(f"   Total tokens: {total_tokens:,}")

        click.echo(f"\n✨ Done!")

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        logger.exception("Protocol execution failed")
        sys.exit(1)
    finally:
        # Cleanup
        if 'grok_client' in locals():
            await grok_client.close()


@cli.command()
@click.argument('session_id')
def resume(session_id):
    """
    Resume an incomplete session

    Example:
        ai-dialogue resume 20250109-143052
    """
    click.echo(f"Resuming session: {session_id}")
    click.echo("⚠️  Resume functionality coming soon")


@cli.command()
@click.option('--limit', '-n', default=20, help='Number of sessions to show')
def list(limit):
    """
    List recent sessions

    Example:
        ai-dialogue list
        ai-dialogue list --limit 10
    """
    state_manager = StateManager()
    sessions = state_manager.list_sessions(limit=limit)

    if not sessions:
        click.echo("No sessions found")
        return

    click.echo(f"\n📚 Recent sessions ({len(sessions)}):\n")

    for session in sessions:
        status_icon = "✅" if session['status'] == 'completed' else "⏳"
        click.echo(f"{status_icon} {session['session_id']}")
        click.echo(f"   Mode: {session['mode']}")
        click.echo(f"   Topic: {session['topic']}")
        click.echo(f"   Turns: {session['turns']}")
        click.echo(f"   Started: {session['started_at']}")
        if session['completed_at']:
            click.echo(f"   Completed: {session['completed_at']}")
        click.echo()


@cli.command()
@click.argument('session_id')
@click.option('--output', '-o', type=click.Path(), help='Output markdown file path')
def export(session_id, output):
    """
    Export session to markdown

    Example:
        ai-dialogue export 20250109-143052
        ai-dialogue export 20250109-143052 --output report.md
    """
    try:
        state_manager = StateManager()
        conversation = state_manager.load_conversation(session_id)

        output_path = Path(output) if output else None
        md_file = state_manager.export_markdown(conversation, output_path)

        click.echo(f"✅ Exported to: {md_file}")

    except FileNotFoundError:
        click.echo(f"❌ Session not found: {session_id}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('session_id')
@click.confirmation_option(prompt='Are you sure you want to delete this session?')
def delete(session_id):
    """
    Delete a session

    Example:
        ai-dialogue delete 20250109-143052
    """
    state_manager = StateManager()

    if state_manager.delete_session(session_id):
        click.echo(f"✅ Deleted: {session_id}")
    else:
        click.echo(f"❌ Session not found: {session_id}", err=True)
        sys.exit(1)


@cli.command()
def modes():
    """
    List available interaction modes

    Shows all built-in modes and their descriptions
    """
    from pathlib import Path
    import json

    modes_dir = Path(__file__).parent / "src" / "modes"

    click.echo("\n📋 Available Modes:\n")

    for mode_file in sorted(modes_dir.glob("*.json")):
        with open(mode_file) as f:
            config = json.load(f)

        click.echo(f"🎯 {config['name']}")
        click.echo(f"   {config['description']}")
        click.echo(f"   Default turns: {config['turns']}")
        click.echo(f"   Use case: {config['metadata'].get('use_case', 'N/A')}")
        click.echo()


if __name__ == '__main__':
    cli()
