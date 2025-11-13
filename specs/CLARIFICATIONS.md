# Clarifications & Open Questions

**Version**: 1.0
**Created**: 2025-01-13
**Purpose**: Document areas requiring decisions before/during implementation
**Status**: Requires stakeholder input

---

## 🎯 Purpose

This document identifies **underspecified areas** in the AI Dialogue system that require clarification, decisions, or further research. Following the spec-kit philosophy, we make ambiguity explicit rather than making assumptions.

---

## 📋 Decision Framework

For each question, we provide:
- **Context**: Why this matters
- **Options**: Possible approaches
- **Tradeoffs**: Pros/cons of each option
- **Recommendation**: Our suggested default (subject to override)
- **Impact**: What changes if we decide differently

---

## 🔧 Category 1: Core Architecture Decisions

### Q1.1: LangChain vs. Direct Integration

**Context**: Core architecture spec recommends LangChain for model abstraction. Is this the right choice?

**Options**:

A) **LangChain (recommended)**
   - ✅ Mature abstraction layer
   - ✅ Active community, many integrations
   - ✅ Handles auth, retries, streaming
   - ❌ Additional dependency
   - ❌ Potential abstraction overhead

B) **Direct API integration**
   - ✅ No extra dependencies
   - ✅ Full control over implementation
   - ❌ Must implement auth, retries, etc.
   - ❌ More code to maintain

C) **Hybrid**: LangChain for major models, direct for custom
   - ✅ Best of both worlds
   - ✅ Flexibility for special cases
   - ❌ Two patterns to maintain

**Tradeoffs**:
- **Development speed**: LangChain wins (weeks saved on boilerplate)
- **Maintenance burden**: LangChain slightly worse (dependency updates)
- **Flexibility**: Hybrid best, direct second, LangChain third
- **Performance**: Direct best (no abstraction overhead), but likely negligible

**Recommendation**: **Option A (LangChain)** for initial implementation

**Rationale**:
- Time to market matters more than perfect control
- LangChain overhead is <50ms per call (acceptable)
- Can always add direct integration later if needed
- Team likely more familiar with LangChain patterns

**Impact if we choose differently**:
- Option B: +2 weeks development time, -1 dependency
- Option C: +1 week development time, more complex codebase

**Decision Needed By**: Before implementation starts (Week 0)
**Decision Owner**: Technical Lead

---

### Q1.2: Async Library Choice

**Context**: Python has multiple async approaches. Which do we use?

**Options**:

A) **asyncio (standard library)**
   - ✅ No dependencies
   - ✅ Everyone knows it
   - ❌ Lower-level API
   - ❌ More boilerplate

B) **Trio**
   - ✅ Better error handling
   - ✅ Cleaner API
   - ❌ Smaller ecosystem
   - ❌ Additional dependency

C) **asyncio + aiohttp helpers**
   - ✅ Best of both (standard + ergonomics)
   - ✅ Widely used pattern
   - ❌ Slight learning curve

**Recommendation**: **Option C (asyncio + aiohttp)**

**Rationale**:
- asyncio is standard, won't disappear
- aiohttp adds minimal dependencies, huge ergonomic win
- LangChain works with asyncio out of box

**Impact if we choose differently**:
- Trio: Entire codebase uses different async style
- Pure asyncio: +20% more boilerplate code

**Decision Needed By**: Week 0
**Decision Owner**: Technical Lead
**Status**: ✅ DECIDED (Option C)

---

### Q1.3: Model Registry Storage

**Context**: Where do we store model capabilities, costs, etc.?

**Options**:

A) **JSON configuration file**
   - ✅ Easy to edit
   - ✅ Version-controlled
   - ❌ No validation until runtime

B) **SQLite database**
   - ✅ Queryable
   - ✅ Can grow to historical performance data
   - ❌ Overkill for initial version

C) **Python dataclasses + JSON**
   - ✅ Type-safe
   - ✅ Edit as JSON, load as Python objects
   - ✅ Validation at load time

**Recommendation**: **Option C (dataclasses + JSON)**

**Example**:
```python
@dataclass
class ModelCapability:
    name: str
    provider: str  # "xai", "anthropic", "openai"
    capabilities: List[str]  # ["reasoning", "vision", "code"]
    cost_per_million: float
    context_window: int
    default_temperature: float = 0.7

# models.json
{
  "grok-4": {
    "provider": "xai",
    "capabilities": ["reasoning", "analysis", "code"],
    "cost_per_million": 5.0,
    "context_window": 131072
  }
}
```

**Decision Needed By**: Week 1
**Decision Owner**: Technical Lead
**Status**: 🟡 PROPOSED (needs review)

---

## 🧠 Category 2: Advanced Capabilities Decisions

### Q2.1: Convergence Detection Thresholds

**Context**: What default thresholds for convergence detection?

**Current Proposals**:
- Semantic similarity: 85%
- Novelty drop: <10%
- Consensus required: 3 of 4 signals

**Questions**:
1. Should thresholds vary by mode?
   - Research mode: Higher threshold (explore more)
   - Podcast mode: Lower threshold (conversational, not exhaustive)

2. Should they adapt based on topic complexity?
   - Simple topics: Lower threshold (converge faster)
   - Complex topics: Higher threshold (need more exploration)

3. Do we need per-user preferences?
   - "I always want max exploration" → high thresholds
   - "I want quick summaries" → low thresholds

**Options**:

A) **Fixed defaults** (simplest)
B) **Mode-specific defaults** (recommended)
C) **Adaptive per topic** (complex but powerful)
D) **User profiles** (most flexible)

**Recommendation**: **Start with B, evolve to C**

**Decision Needed By**: Week 3 (before convergence implementation)
**Decision Owner**: Product + Technical Lead
**Status**: 🟡 NEEDS DISCUSSION

---

### Q2.2: Quality Metrics - What's "Good"?

**Context**: How do we define quality objectively?

**Questions**:
1. **Depth**: Is it topic-dependent?
   - "Explain addition" - shallow but complete
   - "Explain consciousness" - needs depth

2. **Rigor**: What counts as "evidence"?
   - Citations to papers?
   - Logical reasoning?
   - Empirical data?

3. **Novelty**: Novel to whom?
   - An expert?
   - A beginner?
   - The models themselves?

**Proposed Approach**:
```python
quality = QualityMetrics(
    depth={
        "min_turns_on_topic": 3,
        "concept_hierarchy_levels": 4,  # How deep the tree goes
        "abstraction_ladder": 3  # Concrete → Abstract transitions
    },
    rigor={
        "evidence_types": ["citation", "data", "reasoning"],
        "min_evidence_per_claim": 1,
        "hedging_appropriate": True  # Low confidence → hedge
    },
    novelty={
        "baseline": "common_knowledge",  # vs. model training data
        "measure": "new_concepts_per_turn"
    }
)
```

**Questions Remaining**:
- How do we build "common knowledge" baseline?
- Should quality targets vary by use case?
- Can users customize quality definitions?

**Recommendation**: **User-customizable with good defaults**

**Decision Needed By**: Week 4 (before quality metrics implementation)
**Decision Owner**: Product Lead
**Status**: 🟡 NEEDS USER RESEARCH

---

### Q2.3: Meta-Cognition - Who Assesses?

**Context**: Which model should perform meta-cognitive assessment?

**Options**:

A) **Same model assesses itself**
   - ✅ Understands own reasoning
   - ❌ Limited external perspective
   - ❌ May miss own blindspots

B) **Alternate model assesses (Grok ↔ Claude)**
   - ✅ External perspective
   - ✅ Catches different blindspots
   - ❌ May not understand other model's reasoning

C) **Dedicated "assessor" model**
   - ✅ Specialized for evaluation
   - ❌ Extra cost
   - ❌ Needs to understand both models

D) **User provides assessment criteria**
   - ✅ Matches user's actual needs
   - ❌ Requires user to define criteria
   - ❌ Can't run automatically

**Recommendation**: **Option B (alternate) + D (user criteria)**

**Example**:
```python
# Grok generates hypothesis
grok_response = await grok.chat("Generate 3 hypotheses for...")

# Claude assesses quality
assessment = await claude.chat(
    f"Assess these hypotheses for: {user_criteria}\n\n{grok_response}"
)

# Use assessment to guide next turn
next_prompt = build_prompt_with_feedback(grok_response, assessment)
```

**Decision Needed By**: Week 5
**Decision Owner**: Product + Technical Lead
**Status**: 🟡 PROPOSED (needs validation)

---

### Q2.4: Dynamic Depth - How Deep is Too Deep?

**Context**: Sub-dialogues can spawn sub-sub-dialogues. When do we stop?

**Questions**:
1. **Max depth**: How many levels of nesting?
   - 2 levels? (dialogue → sub-dialogue)
   - 3 levels? (dialogue → sub → sub-sub)
   - Unlimited? (with budget constraints)

2. **Spawning criteria**: What importance score triggers spawning?
   - 0.75? (recommended)
   - 0.80? (more selective)
   - Adaptive based on budget?

3. **Parallel vs. serial sub-dialogues**:
   - Spawn all important ones in parallel? (fast, expensive)
   - Spawn highest-importance first, assess, then spawn more? (slower, adaptive)

**Current Proposal**:
```python
depth_config = {
    "max_depth": 2,  # Dialogue → Sub → Stop
    "importance_threshold": 0.75,
    "max_subdialogues_per_level": 3,
    "execution": "parallel",  # Spawn all at once
    "budget": {
        "max_cost_per_depth_level": 1.0,  # $1 per level
        "prioritize": "importance_score"
    }
}
```

**Concerns**:
- Depth 3+ can explode costs (3 → 9 → 27 dialogues)
- How do we visualize deep nesting for users?
- When does depth help vs. just add complexity?

**Recommendation**: **Max depth 2, importance 0.75, parallel execution**

**Decision Needed By**: Week 5
**Decision Owner**: Technical Lead + Product
**Status**: 🟡 NEEDS COST ANALYSIS

---

## 💰 Category 3: Cost & Performance

### Q3.1: Token Budget Strategies

**Context**: How do we prevent cost explosions?

**Questions**:
1. **Hard limits vs. soft warnings**:
   - Hard: Stop at $X (protects user wallet)
   - Soft: Warn at $X, let user decide (more flexible)

2. **Per-dialogue vs. per-session vs. per-user**:
   - Per-dialogue: "$1 max per dialogue"
   - Per-session: "$10 max per session" (multiple dialogues)
   - Per-user: "User has $100 monthly budget"

3. **Budget allocation across features**:
   - Base dialogue: 60% of budget
   - Sub-dialogues: 30% of budget
   - Meta-cognition: 10% of budget
   - Or: Dynamic allocation based on value?

**Options**:

A) **Simple hard limit per dialogue**
   ```python
   dialogue = await orchestrator.run(
       max_cost=1.00  # Stop at $1
   )
   ```

B) **Soft warning + user confirmation**
   ```python
   dialogue = await orchestrator.run(
       budget_warning=1.00,  # Warn at $1
       max_cost=5.00  # Hard stop at $5
   )
   ```

C) **Adaptive allocation**
   ```python
   dialogue = await orchestrator.run(
       total_budget=2.00,
       allocate_by_value=True  # System decides how to spend
   )
   ```

**Recommendation**: **Option B (soft warning + hard limit)**

**Rationale**:
- Protects users from accidents
- Gives flexibility when needed
- Default warning at $1, hard limit at $5

**Decision Needed By**: Week 2
**Decision Owner**: Product Lead
**Status**: 🟡 NEEDS USER TESTING

---

### Q3.2: Caching Strategy

**Context**: Can we cache responses to save costs?

**Considerations**:
1. **Safety**: Same prompt ≠ same context
   - Cache only if context identical?
   - Or cache with context-aware keys?

2. **Staleness**: Models improve over time
   - Cache TTL? (expire after 30 days?)
   - Invalidate on model update?

3. **Privacy**: Can we share caches across users?
   - Public topics: Yes (quantum computing)
   - Private topics: No (medical advice)

**Proposal**:
```python
cache_config = {
    "enabled": True,
    "ttl_days": 30,
    "scope": "user",  # per-user caching only
    "cache_key": "hash(prompt + context + model + temperature)",
    "bypass": ["medical", "legal", "financial"]  # Never cache sensitive
}
```

**Questions**:
- Does LangChain handle caching?
- Should we use Redis or just in-memory?
- How much can we actually save? (needs measurement)

**Recommendation**: **Start without caching, add if cost becomes issue**

**Decision Needed By**: Week 6 (after observing real costs)
**Decision Owner**: Technical Lead
**Status**: 🔵 DEFERRED (revisit after month 1)

---

### Q3.3: Model Selection for Cost Optimization

**Context**: Should we use cheaper models for less important turns?

**Example**:
```python
# Important reasoning → expensive model
turn_1 = {"role": "hypothesis", "model": "grok-4"}  # $5/M tokens

# Simple summarization → cheap model
turn_8 = {"role": "summary", "model": "grok-3"}  # $2/M tokens
```

**Questions**:
1. Can users trust quality with mixed models?
2. How do we determine which turns can use cheaper models?
3. Does model switching hurt coherence?

**Options**:

A) **Always use best model** (simple, expensive)
B) **Task-based model selection** (complex, cheaper)
C) **User chooses quality tier** (flexible)
   - "Economy": Cheaper models
   - "Balanced": Mix of models
   - "Premium": Best models only

**Recommendation**: **Option C (user tiers)**

**Default**: Balanced (use best for reasoning, cheaper for summaries)

**Decision Needed By**: Week 2
**Decision Owner**: Product Lead
**Status**: 🟡 NEEDS PRICING ANALYSIS

---

## 📊 Category 4: User Experience

### Q4.1: Progress Visibility

**Context**: Long dialogues take minutes. How do we show progress?

**Options**:

A) **Silent execution, show results at end**
   - ✅ Simple implementation
   - ❌ Feels unresponsive

B) **Turn-by-turn updates**
   ```
   [Turn 1/8] Grok: Establishing foundation...
   [Turn 2/8] Claude: Analyzing assumptions...
   ```
   - ✅ User knows what's happening
   - ❌ Can be noisy for long dialogues

C) **Phase-based updates**
   ```
   [Phase 1: Foundation] 25% complete...
   [Phase 2: Analysis] 50% complete...
   ```
   - ✅ High-level, not noisy
   - ❌ Less detailed

D) **Streaming responses**
   - ✅ Real-time output
   - ❌ Complex implementation

**Recommendation**: **Start with B, offer C and D as options**

**Decision Needed By**: Week 1 (affects CLI design)
**Decision Owner**: Product Lead
**Status**: 🟡 NEEDS UX REVIEW

---

### Q4.2: Output Format Preferences

**Context**: What output formats matter most?

**Current**: JSON + Markdown export

**User requests**:
- PDF export?
- HTML with interactive navigation?
- Audio (text-to-speech for podcast mode)?
- Jupyter notebook?

**Questions**:
1. Which formats are must-have vs. nice-to-have?
2. Should we integrate with existing tools (Notion, Obsidian)?
3. How much effort per format?

**Recommendation**: **Phase approach**
- Phase 1: JSON + Markdown (have this)
- Phase 2: HTML (if requested)
- Phase 3: Tool integrations (if demand exists)

**Decision Needed By**: Week 2
**Decision Owner**: Product Lead
**Status**: 🟡 NEEDS USER RESEARCH

---

## 🔬 Category 5: Testing & Validation

### Q5.1: How Do We Test Quality Metrics?

**Context**: Quality is subjective. How do we validate our metrics?

**Options**:

A) **Expert human ratings**
   - ✅ Gold standard
   - ❌ Expensive, slow
   - ❌ Can't run in CI

B) **Comparative testing**
   - Compare two dialogues, ask which is better
   - ✅ Easier than absolute ratings
   - ❌ Still requires humans

C) **Proxy metrics**
   - Citation count, concept coverage, logical coherence
   - ✅ Automated
   - ❌ May not capture true quality

D) **User feedback in production**
   - "Was this dialogue helpful? (1-5)"
   - ✅ Real user data
   - ❌ Requires production usage

**Recommendation**: **Use all four**
- A: 10 expert ratings for baseline validation
- B: Comparative tests in CI (choose better of two)
- C: Automated proxy metrics (daily)
- D: Collect feedback from beta users

**Decision Needed By**: Week 4
**Decision Owner**: Technical Lead + QA
**Status**: 🟡 NEEDS BUDGET FOR EXPERT RATINGS

---

### Q5.2: API Cost During Testing

**Context**: Running tests against real APIs costs money. How do we manage this?

**Current situation**:
- Full integration test: ~$0.10
- Full test suite: ~$2.00 per run
- If run 100x/day: $200/day = $6K/month

**Options**:

A) **Mock everything in CI**
   - ✅ Free
   - ❌ Doesn't catch API changes

B) **Real API tests, run nightly only**
   - ✅ Catches issues
   - ❌ Slower feedback

C) **Hybrid**: Mocks in PR checks, real API in nightly
   - ✅ Balance cost and coverage
   - ✅ Fast feedback on most issues

D) **Test credits from providers**
   - Ask Anthropic/XAI for test credits
   - ✅ Real tests for free
   - ❌ May have limits

**Recommendation**: **Option C (hybrid) + pursue D**

**Decision Needed By**: Week 2
**Decision Owner**: Technical Lead
**Status**: 🟡 NEEDS BUDGET APPROVAL

---

## 📋 Decision Tracking

| Question | Status | Owner | Needed By | Blocking? |
|----------|--------|-------|-----------|-----------|
| Q1.1: LangChain vs Direct | 🟡 Proposed | Tech Lead | Week 0 | ✅ Yes |
| Q1.2: Async library | ✅ Decided | Tech Lead | Week 0 | No |
| Q1.3: Model registry | 🟡 Proposed | Tech Lead | Week 1 | ✅ Yes |
| Q2.1: Convergence thresholds | 🟡 Discussion | Product+Tech | Week 3 | No |
| Q2.2: Quality metrics | 🟡 Research | Product | Week 4 | No |
| Q2.3: Meta-cognition assessor | 🟡 Proposed | Product+Tech | Week 5 | No |
| Q2.4: Dynamic depth limits | 🟡 Analysis | Tech+Product | Week 5 | No |
| Q3.1: Token budgets | 🟡 Testing | Product | Week 2 | No |
| Q3.2: Caching | 🔵 Deferred | Tech Lead | Month 2 | No |
| Q3.3: Model cost optimization | 🟡 Analysis | Product | Week 2 | No |
| Q4.1: Progress visibility | 🟡 UX Review | Product | Week 1 | No |
| Q4.2: Output formats | 🟡 Research | Product | Week 2 | No |
| Q5.1: Quality testing | 🟡 Budget | Tech+QA | Week 4 | No |
| Q5.2: API test costs | 🟡 Budget | Tech Lead | Week 2 | No |

### Legend:
- ✅ **Decided**: Decision made, documented
- 🟡 **Needs Decision**: Active discussion, needs resolution
- 🔵 **Deferred**: Will decide later, not blocking
- 🔴 **Blocked**: Can't proceed until resolved

---

## 🎯 Resolution Process

For each open question:

1. **Gather Data**
   - User research (if UX question)
   - Technical spike (if feasibility question)
   - Cost analysis (if budget question)

2. **Propose Options**
   - Document tradeoffs clearly
   - Include recommendation

3. **Get Stakeholder Input**
   - Product lead for UX/features
   - Tech lead for architecture
   - Finance for budget

4. **Decide & Document**
   - Update this document
   - Notify team
   - Update relevant specs

5. **Validate in Implementation**
   - Test assumption
   - Adjust if needed

---

## 📚 References

- **CONSTITUTION.md** - Principles guide decisions
- **CORE-ARCHITECTURE-SPEC.md** - Architectural decisions
- **ADVANCED-CAPABILITIES-SPEC.md** - Feature decisions
- **TECHNICAL-PLAN.md** - Implementation decisions

---

**Next Review**: Weekly standup
**Document Owner**: Product + Technical Leads
**Last Updated**: 2025-01-13

---

*"The only bad decision is no decision. Document options, choose thoughtfully, validate quickly."*
