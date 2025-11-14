# Technical Implementation Plan

**Version**: 1.0
**Created**: 2025-01-13
**Status**: Ready for Execution
**Timeline**: 10 weeks (2 engineers)
**Dependencies**: All specification documents

---

## 🎯 Purpose

Provide a **concrete, actionable implementation plan** following TDD methodology and Pragmatic Programmer principles. This plan honors the Constitution's principles while delivering the core and advanced capabilities.

---

## 📋 Implementation Philosophy

### Test-Driven Development (TDD)

Every feature follows the Red-Green-Refactor cycle:

```
1. RED: Write failing test that captures requirement
2. GREEN: Write minimal code to make test pass
3. REFACTOR: Improve code quality with tests as safety net
4. REPEAT: Next requirement
```

### Parallel Execution

Where possible, use parallel Task agents to:
- Implement independent modules concurrently
- Run test suites in parallel
- Validate multiple approaches simultaneously

### Continuous Integration

- Tests run on every commit
- Quality gates: 80% coverage, 0 lint errors
- API tests run nightly (to manage cost)

---

## 🏗️ Phase 1: Foundation (Weeks 1-2)

### Goal
**LangChain-based model abstraction layer with async orchestration**

### Prerequisites
- [x] All specs reviewed and approved
- [ ] LangChain vs. Direct decision made (Q1.1)
- [ ] Model registry format decided (Q1.3)
- [ ] Development environment set up

### Tasks

#### T1.1: LangChain Integration
**Priority**: CRITICAL
**Effort**: 3 days
**Owner**: Backend Engineer

**Subtasks**:
1. Install LangChain dependencies
   ```bash
   pip install langchain langchain-openai langchain-anthropic langchain-community
   ```

2. Create base model adapter interface
   ```python
   # src/adapters/base.py
   class ModelAdapter(ABC):
       @abstractmethod
       async def chat(self, prompt: str, **kwargs) -> Tuple[str, TokenUsage]:
           pass

       @abstractmethod
       async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
           pass

       @property
       @abstractmethod
       def capabilities(self) -> List[str]:
           pass
   ```

3. Implement Grok adapter (migrate from existing)
   ```python
   # src/adapters/grok_adapter.py
   from langchain_openai import ChatOpenAI

   class GrokAdapter(ModelAdapter):
       def __init__(self, model: str = "grok-4"):
           self.client = ChatOpenAI(
               api_key=os.getenv("XAI_API_KEY"),
               base_url="https://api.x.ai/v1",
               model=MODEL_IDS.get(model, model)
           )
   ```

4. Implement Claude adapter (migrate from existing)
   ```python
   # src/adapters/claude_adapter.py
   from langchain_anthropic import ChatAnthropic

   class ClaudeAdapter(ModelAdapter):
       def __init__(self, model: str = "claude-sonnet-4.5"):
           self.client = ChatAnthropic(
               model=model
           )
   ```

**Tests** (write first!):
```python
# tests/test_adapters.py
async def test_grok_adapter_chat():
    adapter = GrokAdapter(model="grok-4")
    response, tokens = await adapter.chat("Hello")

    assert isinstance(response, str)
    assert len(response) > 0
    assert tokens.total > 0

async def test_claude_adapter_chat():
    adapter = ClaudeAdapter(model="claude-sonnet-4.5")
    response, tokens = await adapter.chat("Hello")

    assert isinstance(response, str)
    assert len(response) > 0
    assert tokens.total > 0

async def test_adapter_streaming():
    adapter = GrokAdapter()
    chunks = []

    async for chunk in adapter.stream("Count to 5"):
        chunks.append(chunk)

    assert len(chunks) > 5  # Should stream multiple chunks
```

**Success Criteria**:
- ✅ Both adapters work with LangChain
- ✅ Tests pass without real API (mocked)
- ✅ Real API tests pass (nightly)

---

#### T1.2: Model Registry
**Priority**: HIGH
**Effort**: 2 days
**Owner**: Backend Engineer

**Implementation**:
```python
# src/registry/models.json
{
  "grok-4": {
    "provider": "xai",
    "capabilities": ["reasoning", "analysis", "code"],
    "cost_per_million_tokens": 5.0,
    "context_window": 131072,
    "default_temperature": 0.7
  },
  "claude-sonnet-4.5": {
    "provider": "anthropic",
    "capabilities": ["analysis", "reasoning", "code", "vision"],
    "cost_per_million_tokens": 3.0,
    "context_window": 200000,
    "default_temperature": 0.7
  }
}

# src/registry/model_registry.py
@dataclass
class ModelInfo:
    name: str
    provider: str
    capabilities: List[str]
    cost_per_million_tokens: float
    context_window: int
    default_temperature: float = 0.7

class ModelRegistry:
    def __init__(self, config_path: Path = None):
        self.models: Dict[str, ModelInfo] = {}
        self._load_config(config_path)

    def get_best_model(self, capability: str, max_cost: float = None) -> ModelInfo:
        """Get best model for capability within cost constraint"""
        candidates = [
            m for m in self.models.values()
            if capability in m.capabilities
        ]

        if max_cost:
            candidates = [c for c in candidates if c.cost_per_million_tokens <= max_cost]

        # Sort by cost (prefer cheaper for same capability)
        return min(candidates, key=lambda m: m.cost_per_million_tokens)
```

**Tests**:
```python
def test_registry_loads_models():
    registry = ModelRegistry()
    assert "grok-4" in registry.models
    assert "claude-sonnet-4.5" in registry.models

def test_get_best_model_for_capability():
    registry = ModelRegistry()
    best = registry.get_best_model("reasoning")
    assert "reasoning" in best.capabilities

def test_get_best_model_within_cost():
    registry = ModelRegistry()
    cheap = registry.get_best_model("analysis", max_cost=4.0)
    assert cheap.cost_per_million_tokens <= 4.0
```

**Success Criteria**:
- ✅ Registry loads from JSON
- ✅ Can query by capability
- ✅ Can filter by cost
- ✅ Validates config on load

---

#### T1.3: Orchestration Engine Refactor
**Priority**: HIGH
**Effort**: 4 days
**Owner**: Backend Engineer

**Migration Plan**:
1. Extract current `ProtocolEngine` to `OrchestrationEngine`
2. Replace direct client calls with adapter pattern
3. Add model registry integration
4. Preserve existing mode configurations

**New Architecture**:
```python
# src/orchestration/engine.py
class OrchestrationEngine:
    def __init__(self, registry: ModelRegistry, state_manager: StateManager):
        self.registry = registry
        self.state = state_manager
        self.adapters: Dict[str, ModelAdapter] = {}

    def register_adapter(self, provider: str, adapter: ModelAdapter):
        """Register model adapter for provider"""
        self.adapters[provider] = adapter

    async def execute_turn(
        self,
        turn_config: TurnConfig,
        context: ConversationContext
    ) -> Turn:
        """Execute single turn with optimal model selection"""

        # Select model based on config + registry
        if "model" in turn_config:
            model_name = turn_config["model"]
        elif "requires" in turn_config:
            # Capability-based selection
            capability = turn_config["requires"][0]
            model_info = self.registry.get_best_model(capability)
            model_name = model_info.name

        # Get adapter for model's provider
        model_info = self.registry.models[model_name]
        adapter = self.adapters[model_info.provider]

        # Execute
        prompt = self._build_prompt(turn_config, context)
        response, tokens = await adapter.chat(prompt, **turn_config.get("params", {}))

        return Turn(...)
```

**Tests**:
```python
async def test_orchestration_uses_registry():
    registry = ModelRegistry()
    engine = OrchestrationEngine(registry, state_manager)

    engine.register_adapter("xai", GrokAdapter())
    engine.register_adapter("anthropic", ClaudeAdapter())

    turn = await engine.execute_turn(
        turn_config={"requires": ["reasoning"]},
        context=ConversationContext()
    )

    # Should have selected Grok (best for reasoning)
    assert turn.model_used in ["grok-4", "grok-3"]

async def test_orchestration_respects_explicit_model():
    engine = OrchestrationEngine(registry, state_manager)

    turn = await engine.execute_turn(
        turn_config={"model": "claude-sonnet-4.5"},
        context=ConversationContext()
    )

    assert turn.model_used == "claude-sonnet-4.5"
```

**Success Criteria**:
- ✅ Migrated from old protocol.py
- ✅ Uses adapters + registry
- ✅ Backward compatible with existing modes
- ✅ All existing tests still pass

---

### Phase 1 Deliverables

**By end of Week 2**:
- ✅ LangChain adapters for Grok + Claude
- ✅ Model registry with capability-based selection
- ✅ Refactored orchestration engine
- ✅ 80%+ test coverage
- ✅ All existing modes still work

**Demo**: Run existing loop mode using new architecture

---

## 🚀 Phase 2: Advanced Capabilities (Weeks 3-6)

### Goal
**Convergence detection, meta-cognition, dynamic depth**

### Week 3: Convergence Detection

#### T2.1: Semantic Similarity Module
**Effort**: 3 days
**Dependencies**: Sentence transformer models

**Implementation**:
```python
# src/analysis/convergence.py
from sentence_transformers import SentenceTransformer

class ConvergenceDetector:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    async def analyze(self, conversation: Conversation) -> ConvergenceResult:
        """Detect convergence across multiple signals"""

        # Semantic similarity
        semantic = self._check_semantic_similarity(conversation)

        # Novelty decay
        novelty = self._check_novelty_decay(conversation)

        # Consensus
        converged = (semantic.converged and novelty.converged)

        return ConvergenceResult(
            detected=converged,
            confidence=min(semantic.confidence, novelty.confidence),
            signals={"semantic": semantic, "novelty": novelty}
        )

    def _check_semantic_similarity(self, conversation) -> Signal:
        """Calculate embedding similarity for recent turns"""
        recent_turns = conversation.turns[-3:]
        embeddings = [self.embedder.encode(t.response) for t in recent_turns]

        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(embeddings[i], embeddings[i+1])
            similarities.append(sim)

        avg_sim = sum(similarities) / len(similarities)
        converged = avg_sim > self.threshold

        return Signal(converged=converged, confidence=avg_sim)
```

**Tests** (write first!):
```python
async def test_convergence_detects_repetition():
    responses = [
        "Quantum computing uses qubits...",
        "Qubits enable superposition...",
        "Superposition allows parallel computation...",
        "Parallel computation is the key advantage...",
        "The key advantage comes from qubits..."  # Loops back
    ]

    conversation = create_mock_conversation(responses)
    detector = ConvergenceDetector(threshold=0.85)

    result = await detector.analyze(conversation)
    assert result.detected == True

async def test_convergence_not_detected_early():
    responses = [
        "Quantum computing uses qubits...",
        "Cryptography has many applications...",
        "Shor's algorithm factors large numbers..."
    ]

    conversation = create_mock_conversation(responses)
    detector = ConvergenceDetector()

    result = await detector.analyze(conversation)
    assert result.detected == False
```

---

#### T2.2: Novelty Scoring
**Effort**: 2 days

**Implementation**:
```python
# src/analysis/novelty.py
import spacy

class NoveltyAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.seen_concepts = set()

    def analyze_turn(self, turn: Turn) -> NoveltyScore:
        """Calculate percentage of novel concepts in turn"""

        # Extract entities and noun chunks
        doc = self.nlp(turn.response)
        current_concepts = set()

        for ent in doc.ents:
            current_concepts.add(ent.text.lower())

        for chunk in doc.noun_chunks:
            current_concepts.add(chunk.text.lower())

        # Calculate novelty
        novel = current_concepts - self.seen_concepts
        novelty_score = len(novel) / len(current_concepts) if current_concepts else 0

        # Update seen concepts
        self.seen_concepts.update(current_concepts)

        return NoveltyScore(
            score=novelty_score,
            novel_concepts=novel,
            total_concepts=current_concepts
        )
```

**Tests**:
```python
def test_novelty_high_for_first_turn():
    analyzer = NoveltyAnalyzer()
    turn = Turn(response="Quantum computing uses qubits and superposition...")

    score = analyzer.analyze_turn(turn)
    assert score.score > 0.90  # >90% novel

def test_novelty_decreases_with_repetition():
    analyzer = NoveltyAnalyzer()

    turn_1 = Turn(response="Quantum computing uses qubits...")
    turn_2 = Turn(response="Qubits enable quantum computing...")

    score_1 = analyzer.analyze_turn(turn_1)
    score_2 = analyzer.analyze_turn(turn_2)

    assert score_2.score < score_1.score  # Decreasing novelty
```

---

### Week 4-5: Meta-Cognition

#### T2.3: Quality Assessment Framework
**Effort**: 4 days

**Implementation**:
```python
# src/analysis/quality.py
@dataclass
class QualityMetrics:
    depth: float  # 0-1
    breadth: float  # 0-1
    rigor: float  # 0-1
    coherence: float  # 0-1
    novelty: float  # 0-1

    @property
    def overall(self) -> float:
        return (self.depth + self.breadth + self.rigor + self.coherence + self.novelty) / 5

class QualityAnalyzer:
    async def analyze_conversation(self, conversation: Conversation) -> QualityMetrics:
        """Analyze multi-dimensional quality"""

        depth = await self._measure_depth(conversation)
        breadth = await self._measure_breadth(conversation)
        rigor = await self._measure_rigor(conversation)
        coherence = await self._measure_coherence(conversation)
        novelty = await self._measure_novelty(conversation)

        return QualityMetrics(depth, breadth, rigor, coherence, novelty)

    async def _measure_depth(self, conversation) -> float:
        """Measure exploration depth"""
        # Count concept hierarchy levels
        # Track abstraction ladder traversals
        # Measure time spent on key subtopics
        ...

    async def _measure_rigor(self, conversation) -> float:
        """Measure epistemic rigor"""
        # Count citations/evidence mentions
        # Detect hedging for uncertain claims
        # Check logical coherence
        ...
```

**Tests**:
```python
async def test_quality_metrics_calculated():
    conversation = await orchestrator.run(mode="loop", topic="AI safety")

    metrics = await QualityAnalyzer().analyze_conversation(conversation)

    assert 0 <= metrics.depth <= 1
    assert 0 <= metrics.breadth <= 1
    assert 0 <= metrics.overall <= 1

async def test_quality_correlates_with_human_rating():
    conversations = load_human_rated_conversations()  # 10 conversations

    correlations = []
    for conv in conversations:
        metrics = await QualityAnalyzer().analyze_conversation(conv)
        human_rating = conv.human_quality_score

        correlation = pearson_correlation(metrics.overall, human_rating)
        correlations.append(correlation)

    avg_correlation = sum(correlations) / len(correlations)
    assert avg_correlation > 0.70  # R² > 0.70
```

---

#### T2.4: Meta-Cognitive Assessment Turns
**Effort**: 3 days

**Implementation**:
```python
# src/orchestration/meta_cognition.py
class MetaCognitiveEngine:
    def __init__(self, orchestrator: OrchestrationEngine):
        self.orchestrator = orchestrator
        self.quality_analyzer = QualityAnalyzer()

    async def insert_assessment_turn(
        self,
        conversation: Conversation,
        interval: int = 5
    ) -> Optional[Turn]:
        """Insert quality assessment at intervals"""

        if len(conversation.turns) % interval != 0:
            return None

        # Generate assessment prompt
        recent_turns = conversation.turns[-interval:]
        prompt = f"""
        Assess the quality of the last {interval} turns of this dialogue:

        {format_turns(recent_turns)}

        Evaluate:
        1. Depth: Are we exploring thoroughly?
        2. Rigor: Are claims supported by evidence?
        3. Gaps: What perspectives are missing?
        4. Improvements: What should we do differently?

        Provide actionable feedback for the next turn.
        """

        # Execute assessment
        turn = await self.orchestrator.execute_turn(
            turn_config={
                "role": "meta_assessment",
                "participant": "claude",  # Claude assesses
                "template": prompt
            },
            context=conversation.context
        )

        # Parse feedback and update context
        feedback = self._parse_assessment(turn.response)
        conversation.context.add_meta_feedback(feedback)

        return turn
```

**Tests**:
```python
async def test_assessment_turns_inserted():
    dialogue = await orchestrator.run(
        mode="loop",
        turns=12,
        meta_cognitive={"interval": 5}
    )

    assessments = [t for t in dialogue.turns if t.role == "meta_assessment"]
    assert len(assessments) >= 2  # At turns 5, 10

async def test_assessment_influences_subsequent_turns():
    dialogue = await orchestrator.run(
        mode="loop",
        turns=8,
        meta_cognitive={"interval": 4}
    )

    assessment = next(t for t in dialogue.turns if t.role == "meta_assessment")
    next_turn_index = dialogue.turns.index(assessment) + 1

    if next_turn_index < len(dialogue.turns):
        next_turn = dialogue.turns[next_turn_index]
        assert "feedback" in next_turn.context
```

---

### Week 6: Dynamic Depth

#### T2.5: Importance Scoring & Sub-Dialogue Spawning
**Effort**: 5 days

**Implementation**:
```python
# src/orchestration/dynamic_depth.py
class DynamicDepthEngine:
    def __init__(self, orchestrator: OrchestrationEngine, max_depth: int = 2):
        self.orchestrator = orchestrator
        self.max_depth = max_depth

    async def analyze_subtopics(self, turn: Turn) -> List[Subtopic]:
        """Extract and score subtopics for importance"""

        # Use model to identify subtopics
        prompt = f"""
        Identify 3-5 key subtopics mentioned in this response that might warrant
        deeper exploration:

        {turn.response}

        For each, rate importance (0-1) based on:
        - Complexity (more complex → higher score)
        - Novelty (less obvious → higher score)
        - User interest (if known)

        Return JSON: {{"subtopics": [{{"name": "...", "importance": 0.85}}]}}
        """

        response = await self.orchestrator.quick_query(prompt)
        subtopics = parse_subtopics_json(response)

        return subtopics

    async def spawn_subdialogues(
        self,
        conversation: Conversation,
        subtopics: List[Subtopic],
        threshold: float = 0.75
    ) -> List[Conversation]:
        """Spawn sub-dialogues for high-importance subtopics"""

        high_importance = [s for s in subtopics if s.importance > threshold]

        # Limit to top 3
        high_importance = sorted(high_importance, key=lambda s: s.importance, reverse=True)[:3]

        # Spawn in parallel
        tasks = [
            self.orchestrator.run(
                mode="focused",
                topic=subtopic.name,
                parent_context=conversation.context,
                depth=conversation.depth + 1
            )
            for subtopic in high_importance
        ]

        subdialogues = await asyncio.gather(*tasks)
        return subdialogues
```

**Tests**:
```python
async def test_subtopic_identification():
    turn = Turn(response="AI safety includes alignment, robustness, and interpretability...")

    engine = DynamicDepthEngine(orchestrator)
    subtopics = await engine.analyze_subtopics(turn)

    assert len(subtopics) >= 3
    assert all(0 <= s.importance <= 1 for s in subtopics)

async def test_subdialogue_spawning():
    conversation = Conversation(...)
    subtopics = [
        Subtopic(name="mesa-optimization", importance=0.90),
        Subtopic(name="reward hacking", importance=0.85),
        Subtopic(name="safe exploration", importance=0.70)
    ]

    engine = DynamicDepthEngine(orchestrator)
    subdialogues = await engine.spawn_subdialogues(conversation, subtopics, threshold=0.75)

    # Should spawn top 2 (above threshold)
    assert len(subdialogues) == 2
    assert any("mesa-optimization" in s.topic for s in subdialogues)
    assert any("reward hacking" in s.topic for s in subdialogues)
```

---

### Phase 2 Deliverables

**By end of Week 6**:
- ✅ Convergence detection (semantic + novelty)
- ✅ Meta-cognitive assessment framework
- ✅ Dynamic depth with sub-dialogues
- ✅ Quality metrics calculation
- ✅ Integration tests for all features

**Demo**: Run loop mode with all advanced features enabled

---

## 🎯 Phase 3: Production Hardening (Weeks 7-8)

### Goal
**Observability, error handling, performance optimization**

### Week 7: Observability

#### T3.1: Structured Logging
- Correlation IDs for request tracing
- JSON-formatted logs
- Log levels: DEBUG, INFO, WARNING, ERROR

#### T3.2: Metrics Collection
- Track: latency, tokens, cost per dialogue
- Export to Prometheus/CloudWatch
- Alerting on anomalies

#### T3.3: Dashboards
- Real-time dialogue monitoring
- Cost tracking
- Quality trends

### Week 8: Reliability

#### T3.4: Graceful Fallbacks
- Model unavailable → try fallback
- API timeout → retry with backoff
- Cost limit reached → graceful stop

#### T3.5: Crash Recovery
- Auto-save after each turn
- Resume from last checkpoint
- Idempotent turn execution

---

## 🧪 Phase 4: Validation & Polish (Weeks 9-10)

### Week 9: Testing

- Load testing (10 concurrent dialogues)
- Chaos engineering (random failures)
- Human quality validation (10 expert ratings)
- Cost analysis (optimize expensive operations)

### Week 10: Documentation & Handoff

- API documentation (auto-generated)
- User guide (how to create custom modes)
- Developer guide (how to add new models)
- Video walkthrough

---

## 📊 Success Metrics

### Technical Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Test Coverage** | 80% | - | 🟡 TBD |
| **Orchestration Overhead** | <500ms | - | 🟡 TBD |
| **Parallel Efficiency** | ≥80% | - | 🟡 TBD |
| **Model Adapter Time** | <1 hour | - | 🟡 TBD |
| **Convergence Accuracy** | >85% | - | 🟡 TBD |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User Satisfaction** | >4.0/5.0 | Beta user surveys |
| **Quality Correlation** | R² >0.75 | vs. expert ratings |
| **Token Efficiency** | +30% | vs. fixed-turn baseline |
| **Cost Optimization** | +40% | Better cost/quality ratio |

---

## 🚧 Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LangChain API changes | Medium | High | Pin versions, monitor changelog |
| Model API rate limits | High | Medium | Implement backoff, queue requests |
| Quality metrics inaccurate | Medium | High | Validate with human ratings |
| Convergence false positives | Medium | Medium | Multi-signal detection, user override |

### Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | High | Stick to spec, defer enhancements |
| API cost overruns | Medium | Medium | Budget alerts, cost tracking |
| Team availability | Low | High | Document decisions, pair programming |

---

## 📚 References

- **CONSTITUTION.md** - Principles guide implementation
- **CORE-ARCHITECTURE-SPEC.md** - What we're building
- **ADVANCED-CAPABILITIES-SPEC.md** - Advanced features
- **CLARIFICATIONS.md** - Open questions and decisions

---

**Status**: Ready for Execution
**Start Date**: TBD
**End Date**: +10 weeks from start
**Team**: 2 engineers (backend focus)

---

*"Plans are useless, but planning is indispensable." - Dwight D. Eisenhower*

*"Simple, clear purpose and principles give rise to complex intelligent behavior." - Dee Hock*
