#!/usr/bin/env python3
"""
Enhanced Research Example

Demonstrates new Grok API features:
- Files API for document analysis
- Collections API for knowledge base
- Server-side tools for web research

Usage:
    python examples/enhanced_research.py
"""

import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_files_api():
    """Example: Analyze documents using Files API"""
    from src.clients.grok_enhanced import EnhancedGrokClient

    print("\n" + "="*60)
    print("Example 1: Files API - Document Analysis")
    print("="*60)

    grok = EnhancedGrokClient(model="grok-4")

    try:
        # Analyze a single PDF document
        print("\n1. Analyzing single document...")

        # NOTE: Replace with actual file path
        doc_path = "docs/SPEC.md"  # Using existing file for demo

        if Path(doc_path).exists():
            response, tokens = await grok.analyze_file(
                doc_path,
                """
                Analyze this document and provide:
                1. Summary (3 sentences)
                2. Key topics (5 bullet points)
                3. Main takeaways
                """
            )

            print(f"\n✓ Analysis complete ({tokens['total']} tokens)")
            print(f"\nAnalysis:\n{response[:500]}...")
        else:
            print(f"⚠ File not found: {doc_path}")

    finally:
        await grok.close()


async def example_collections_api():
    """Example: Create knowledge base with Collections API"""
    from src.clients.grok_enhanced import EnhancedGrokClient

    print("\n" + "="*60)
    print("Example 2: Collections API - Knowledge Base")
    print("="*60)

    grok = EnhancedGrokClient()

    try:
        # Create collection
        print("\n1. Creating knowledge base collection...")

        collection = await grok.collections.create_collection(
            name="Project Documentation",
            description="Technical documentation and specs",
            enable_embeddings=True
        )

        print(f"✓ Created collection: {collection['id']}")

        # Upload documents
        print("\n2. Uploading documents...")

        docs = [
            "docs/SPEC.md",
            "README.md",
        ]

        existing_docs = [d for d in docs if Path(d).exists()]

        if existing_docs:
            uploaded = await grok.collections.upload_files_batch(
                collection_id=collection['id'],
                file_paths=existing_docs,
                max_concurrent=2
            )

            print(f"✓ Uploaded {len(uploaded)} documents")

        # Wait for embeddings
        print("\n3. Generating embeddings...")
        await asyncio.sleep(2)
        print("✓ Embeddings ready")

        # Query knowledge base
        print("\n4. Querying knowledge base...")

        answer, sources = await grok.chat_with_collection(
            "What is the architecture of this system?",
            collection_ids=[collection['id']],
            search_top_k=3
        )

        print(f"\n✓ Answer: {answer[:300]}...")
        print(f"✓ Based on {len(sources)} sources")

        # Cleanup
        print("\n5. Cleaning up...")
        await grok.collections.delete_collection(collection['id'])
        print("✓ Collection deleted")

    finally:
        await grok.close()


async def example_server_side_tools():
    """Example: Research using server-side tools"""
    from src.clients.grok_enhanced import EnhancedGrokClient

    print("\n" + "="*60)
    print("Example 3: Server-Side Tools - Web Research")
    print("="*60)

    grok = EnhancedGrokClient(model="grok-4-fast")

    try:
        # Web research
        print("\n1. Performing web research...")

        response, tokens = await grok.research_query(
            "What are the latest developments in async Python programming?",
            use_web=True,
            use_x=False,
            use_code=False
        )

        print(f"\n✓ Research complete ({tokens['total']} tokens)")
        print(f"\nFindings:\n{response[:500]}...")

        # Research with code execution
        print("\n2. Research with quantitative analysis...")

        response, tokens = await grok.research_query(
            """
            Find recent statistics about Python package downloads.
            Then calculate the year-over-year growth rate for the top 5 packages.
            """,
            use_web=True,
            use_code=True  # Will execute Python for calculations
        )

        print(f"\n✓ Analysis complete ({tokens['total']} tokens)")
        print(f"\nResults:\n{response[:500]}...")

    finally:
        await grok.close()


async def example_combined_workflow():
    """Example: Combined workflow using all features"""
    from src.clients.grok_enhanced import EnhancedGrokClient

    print("\n" + "="*60)
    print("Example 4: Combined Workflow - All Features")
    print("="*60)

    grok = EnhancedGrokClient(model="grok-4-fast")

    try:
        topic = "AI agent orchestration patterns"

        # Phase 1: Knowledge base search
        print(f"\n Phase 1: Searching knowledge base for '{topic}'...")

        # Create temp collection for demo
        collection = await grok.collections.create_collection(
            f"Research: {topic}",
            enable_embeddings=True
        )

        # Upload relevant docs
        docs = ["README.md", "docs/SPEC.md"]
        existing = [d for d in docs if Path(d).exists()]

        if existing:
            await grok.collections.upload_files_batch(collection['id'], existing)
            await asyncio.sleep(2)  # Wait for embeddings

            kb_answer, sources = await grok.chat_with_collection(
                f"What information do we have about {topic}?",
                collection_ids=[collection['id']],
                search_top_k=3
            )

            print(f"✓ Found {len(sources)} relevant sources")
        else:
            kb_answer = "No existing documentation found."

        # Phase 2: Web research
        print(f"\n Phase 2: Web research on '{topic}'...")

        web_research, tokens = await grok.research_query(
            f"Latest developments in {topic}",
            use_web=True
        )

        print(f"✓ Web research complete ({tokens['total']} tokens)")

        # Phase 3: Synthesis
        print("\n Phase 3: Synthesizing findings...")

        synthesis, tokens = await grok.chat(
            f"""
            Synthesize research on: {topic}

            Internal Knowledge:
            {kb_answer}

            Web Research:
            {web_research}

            Provide:
            1. Executive summary
            2. Key patterns identified
            3. Emerging trends
            4. Recommendations
            """,
            temperature=0.3,
            max_tokens=3000
        )

        print(f"\n✓ Synthesis complete ({tokens['total']} tokens)")
        print(f"\n{'='*60}")
        print("SYNTHESIS")
        print(f"{'='*60}")
        print(synthesis)

        # Cleanup
        await grok.collections.delete_collection(collection['id'])

    finally:
        await grok.close()


async def main():
    """Run all examples"""
    examples = [
        ("Files API", example_files_api),
        ("Collections API", example_collections_api),
        ("Server-Side Tools", example_server_side_tools),
        ("Combined Workflow", example_combined_workflow),
    ]

    print("\n" + "="*60)
    print("Enhanced Grok API Examples")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Example '{name}' failed: {e}")

    print("\n" + "="*60)
    print("✅ All examples complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
