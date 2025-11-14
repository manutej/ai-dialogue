# AI Dialogue Project - Constitution

**Version**: 1.0
**Created**: 2025-01-13
**Purpose**: Establish governing principles and non-negotiable development standards

---

## 🎯 Project Vision

**Enable sophisticated, nuanced AI-to-AI dialogues through iterative exploration, using a mixture of expert models in a flexible, task-agnostic orchestration framework.**

### Core Philosophy

The AI Dialogue system is not just a chatbot wrapper—it's an **orchestration platform** that enables emergent intelligence through structured multi-agent collaboration. By combining different AI models' strengths through configurable interaction patterns, we create outcomes that exceed what any single model can achieve.

---

## 📜 Governing Principles

### 1. Model Agnostic by Design

**Principle**: The architecture must support any AI model without core changes.

**Rationale**: Models evolve rapidly. Today it's Claude & Grok; tomorrow it might be GPT-5, Gemini Ultra, or domain-specific models. The system must adapt without rewriting core logic.

**Implementation Requirements**:
- ✅ Use abstraction layers (LangChain v1+ or equivalent)
- ✅ Models are configuration, not code
- ✅ Model-specific optimizations are plugins, not core features
- ✅ Success: Adding a new model requires ≤50 lines of adapter code

**Test**: Can we add support for a new model in <1 hour?

---

### 2. Asynchronous by Default

**Principle**: All I/O operations must be non-blocking.

**Rationale**: AI API calls take 2-30 seconds. Blocking execution wastes time and makes parallel orchestration impossible. Async enables mixture-of-experts patterns where multiple models work concurrently.

**Implementation Requirements**:
- ✅ Python asyncio throughout the stack
- ✅ No blocking I/O in critical paths
- ✅ Parallel execution where dependencies allow
- ✅ Success: 3 independent API calls complete in parallel, not series

**Test**: Does a 3-model parallel dialogue complete in ~10s, not ~30s?

---

### 3. Mixture of Experts Architecture

**Principle**: Different models excel at different tasks; orchestrate their strengths.

**Rationale**: Grok excels at reasoning and X-platform knowledge. Claude excels at nuanced analysis and ethical considerations. Use each for what it does best.

**Implementation Requirements**:
- ✅ Mode definitions specify which model plays which role
- ✅ Model selection is declarative (config), not imperative (code)
- ✅ System can route tasks to optimal models dynamically
- ✅ Success: "Reasoning" turns use Grok, "Analysis" turns use Claude automatically

**Test**: Can we configure a mode where Grok handles hypothesis generation and Claude handles validation?

---

### 4. Task-Agnostic Flexibility

**Principle**: Modes are composable patterns, not hardcoded workflows.

**Rationale**: We can't predict every use case. Researchers, developers, and creators need different interaction patterns. Provide primitives, not prescriptions.

**Implementation Requirements**:
- ✅ Modes are JSON configurations, not Python classes
- ✅ Users can create custom modes without code changes
- ✅ Core system provides: turns, context, roles, execution patterns
- ✅ Success: Non-developer can create a new mode by editing JSON

**Test**: Can we create a "Detective Mode" (hypothesis → evidence → contradiction → refinement) in 10 minutes without touching Python?

---

### 5. DRY (Don't Repeat Yourself)

**Principle**: Every piece of knowledge has a single, authoritative representation.

**Rationale**: Duplication creates maintenance burden and inconsistencies. Code, configuration, and documentation should derive from single sources of truth.

**Implementation Requirements**:
- ✅ Mode configurations define structure once, execution engine interprets
- ✅ Model capabilities defined in model registry, not scattered across code
- ✅ Documentation generated from code/config where possible
- ✅ Success: Changing a model's default parameters requires editing 1 file

**Test**: How many files must change to update Grok's default model from grok-4 to grok-5?

---

### 6. Test-Driven Development (TDD)

**Principle**: Write tests first, implement second, refactor third.

**Rationale**: Tests capture requirements better than documentation. They prevent regressions, enable confident refactoring, and serve as executable specifications.

**Implementation Requirements**:
- ✅ Every feature starts with a failing test
- ✅ Tests are hypothesis-driven, not surface-level (see §7)
- ✅ 80%+ code coverage on core modules
- ✅ Success: Tests demonstrate capability, not just code execution

**Test**: Can a new developer understand features by reading tests alone?

---

### 7. Hypothesis-Driven Testing

**Principle**: Tests must validate core behaviors, not just execute code paths.

**Rationale**: Surface-level tests (e.g., "method returns non-null") provide false confidence. Real tests verify the system works as intended under realistic conditions.

**Implementation Requirements**:
- ✅ Each test has a clear hypothesis about system behavior
- ✅ Tests use realistic data, not minimal mocks
- ✅ Tests cover edge cases and failure modes
- ✅ Success: Failed test immediately reveals what's broken and why

**Example**:
- ❌ Bad: `test_convergence_detector_returns_bool()`
- ✅ Good: `test_convergence_detected_when_semantic_similarity_exceeds_85_percent_for_3_turns()`

---

### 8. Domain-Oriented Design

**Principle**: Code speaks the language of dialogue orchestration.

**Rationale**: Abstractions should match mental models. Classes like `Turn`, `Conversation`, `Convergence` are more maintainable than `Node`, `Graph`, `Threshold`.

**Implementation Requirements**:
- ✅ Types/classes named after domain concepts
- ✅ Methods named after domain actions
- ✅ Configuration uses domain terminology
- ✅ Success: Product manager can read code and understand what it does

**Example**:
```python
# ✅ Domain-oriented
conversation = protocol.run_dialogue(mode="loop", topic="AI safety")
if convergence.detected(conversation):
    conversation.export_insights()

# ❌ Generic/technical
graph = executor.run(config="loop", input="AI safety")
if analyzer.check(graph, threshold=0.85):
    exporter.dump(graph)
```

---

### 9. Progressive Complexity

**Principle**: Simple use cases should be simple; complex use cases should be possible.

**Rationale**: Most users need basic functionality (run a dialogue). Advanced users need customization. Don't force everyone to master complexity to do basic tasks.

**Implementation Requirements**:
- ✅ Default configurations work out-of-box
- ✅ Common patterns have presets
- ✅ Advanced customization available but not required
- ✅ Success: "Hello world" dialogue is ≤3 lines of code

**Example**:
```python
# Simple (most users)
dialogue.run(mode="loop", topic="quantum computing")

# Advanced (power users)
dialogue.run(
    mode="custom",
    config=CustomMode(
        convergence_threshold=0.9,
        max_cycles=5,
        quality_metrics=["novelty", "coherence", "depth"]
    )
)
```

---

### 10. Fail Fast, Fail Clearly

**Principle**: Errors should surface immediately with actionable messages.

**Rationale**: Silent failures and cryptic errors waste developer time. If something's wrong, say what and how to fix it.

**Implementation Requirements**:
- ✅ Validate configurations at load time, not runtime
- ✅ Error messages include: what failed, why, how to fix
- ✅ No silent failures or default-to-broken states
- ✅ Success: User can fix error without reading source code

**Example**:
```python
# ❌ Bad error
ValueError: Invalid model

# ✅ Good error
ModelNotFoundError: Model 'grok-5' not recognized.
Available models: ['grok-4', 'grok-3', 'claude-sonnet', 'claude-opus']
To add a new model, see: docs/ADDING-MODELS.md
```

---

## 🚫 Anti-Patterns to Avoid

### 1. Premature Optimization
- Don't optimize for performance before measuring
- Optimize for clarity first, speed second
- **Exception**: Async is always correct (never block)

### 2. Over-Engineering
- Don't build features "we might need someday"
- Don't add abstraction layers until 3rd use case appears
- **Test**: Can you explain why every class exists in <30 seconds?

### 3. Configuration Sprawl
- Don't make everything configurable
- Some decisions should be opinionated (e.g., async-only)
- **Test**: Can default config fit on one screen?

### 4. Test Theater
- Don't write tests just to hit coverage targets
- Don't mock everything (integration tests are valuable)
- **Test**: Do tests catch real bugs or just verify mocks?

### 5. Documentation Drift
- Don't write docs that get out of sync with code
- Don't document what code already explains
- **Test**: Is every code example in docs runnable?

---

## ✅ Quality Standards

### Code Quality
- **Readability**: Code is read 10x more than written
- **Modularity**: Functions do one thing well
- **Testability**: If it's hard to test, it's probably poorly designed
- **Documentation**: Public APIs have docstrings with examples

### Test Quality
- **Coverage**: 80%+ on core modules (protocol, clients, orchestration)
- **Speed**: Unit tests run in <5s, integration tests <30s
- **Clarity**: Test names explain what's being tested
- **Reliability**: No flaky tests (fix or delete)

### Performance Standards
- **Latency**: Dialogue orchestration overhead <500ms
- **Throughput**: Support 10 concurrent dialogues
- **Memory**: <100MB per active conversation
- **Tokens**: Track and report usage per dialogue

---

## 🎓 Learning & Evolution

### Continuous Learning
- Every PR should leave code better than found
- Regular refactoring is healthy, not wasteful
- **Time budget**: 20% of dev time for learning & improvement

### Stakeholder Involvement
- Unclear requirements? Ask the user.
- Tradeoff decisions? Present options.
- **Transparency**: Over-communicate, don't assume

### Technology Evolution
- Stay current on AI/LLM developments
- Reevaluate architecture yearly
- **Principle**: Question assumptions, not randomly

---

## 📋 Checklist for New Features

Before merging any feature, verify:

- [ ] Follows model-agnostic principle (works with any model)
- [ ] Uses async I/O (no blocking calls)
- [ ] Has failing test written first (TDD)
- [ ] Tests are hypothesis-driven (validate behavior, not just code)
- [ ] Code is domain-oriented (speaks dialogue orchestration language)
- [ ] Error messages are actionable (user can self-resolve)
- [ ] Documentation updated (if public API changed)
- [ ] Performance acceptable (measured, not assumed)
- [ ] Reviewed by at least one other developer

---

## 🔬 Success Criteria for This Constitution

This Constitution succeeds if:

1. **Alignment**: Developers reference it when making design decisions
2. **Clarity**: New contributors understand project philosophy from this doc alone
3. **Enforcement**: Code reviews cite principles, not personal preference
4. **Evolution**: Document updates when principles prove wrong

**Test**: Ask a new developer "Why is the system async?" If they answer "because the Constitution says so," we've succeeded.

---

## 📚 Related Documents

- **CORE-ARCHITECTURE-SPEC.md** - How these principles manifest in system design
- **ADVANCED-CAPABILITIES-SPEC.md** - Sophisticated features built on this foundation
- **TECHNICAL-PLAN.md** - Implementation approach honoring these principles
- **VALIDATION-CHECKLIST.md** - Ensuring compliance with Constitution

---

**Approved By**: Project Lead
**Next Review**: 2025-04-13 (quarterly)
**Amendments**: Require team consensus, not individual authority

---

*"Principles are not rules. They're guideposts for thoughtful decision-making."*
