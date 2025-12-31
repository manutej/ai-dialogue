# Test 9 Specification: Cross-Document Synthesis

**Designed via**: Claude ↔ Grok Dialogue (Cycle 6)
**Date**: 2025-12-13
**Status**: Ready to Implement

---

## Hypothesis

**Claim**: Cross-document extraction should show SIMILAR or GREATER gains than Test 7 (+156%) because:
- **Context Isolation = 1.0** (documents are truly independent)
- **Coherence Gap = 0.95** (no inherent connection between sources)

**Prediction**: Gap=0.95 × Isolation=1.0 → **+150-200% coherence improvement**

---

## Document Selection (Grok's Recommendation)

**Topic**: Distributed Data Processing Frameworks

| # | Document | Source | Pages | Focus |
|---|----------|--------|-------|-------|
| 1 | Apache Spark Intro | spark.apache.org/docs/latest/quick-start | ~6 | RDDs, DataFrames, driver-executor |
| 2 | Apache Flink Basics | flink.apache.org/what-is-flink | ~7 | Stream/batch, stateful computations |
| 3 | Apache Beam Overview | beam.apache.org/get-started | ~5 | Unified model, portability |
| 4 | Dask Distributed Tutorial | docs.dask.org/en/stable | ~8 | Python parallelism, task scheduling |
| 5 | Hadoop MapReduce Guide | docs.cloudera.com | ~9 | MapReduce paradigm, HDFS |

**Rationale**: Related concepts (drivers, fault tolerance, scalability) but independent sources → high cross-referencing potential.

---

## Success Criteria

### Confirm Hypothesis
- **Aggregate ≥0.750** (Δ+150% from ~0.300 baseline)
- **Coherence ≥0.800** (exceeding Test 7's +156%)
- **Cross-referencing ≥0.700** (Δ+250%)
- **Statistical**: p<0.01 for comonadic > baseline

### Falsify Hypothesis
- **Aggregate <0.500** (Δ<+67%, no meaningful gain)
- **Coherence <0.600** (Δ<+100%, below Test 7)
- **Statistical**: p≥0.05 (no significant difference)

### Partial Success
- **Aggregate 0.500-0.749** (Δ+67-150%)
- Suggests gains but sub-optimal for high isolation

---

## Implementation Changes

### Key Modifications from Test 7

1. **Data Structure**: Documents instead of sections
```python
docs = [
    {"name": "Apache Spark", "text": extract_text("spark.pdf")},
    {"name": "Apache Flink", "text": extract_text("flink.pdf")},
    # ... 5 total
]
```

2. **History with Document Identifiers**
```python
history_context = f"""
Previous insights from earlier documents:
{chr(10).join([f'- Doc {j+1} ({docs[j]["name"]}): {h[:150]}...' for j, h in enumerate(history)])}

Synthesize by linking concepts across documents (e.g., compare drivers/schedulers).
"""
```

3. **Synthesis-Focused Prompt**
```python
prompt = f"""Round {round_num} of {total_rounds}. Current document: {doc['name']}

{history_context}

Provide a synthesized extraction: Identify key patterns (e.g., execution models)
and explicitly cross-reference/link to prior documents' insights for a unified
overview of distributed frameworks. Ensure coherence across sources."""
```

4. **Batch Processing** (3 rounds across 5 docs)
```
Round 1: Docs 1-2 (Spark, Flink)
Round 2: Docs 3-4 (Beam, Dask)
Round 3: Doc 5 + synthesis (Hadoop)
```

---

## Metrics (Extended from Test 7)

| Metric | Test 7 Definition | Test 9 Extension |
|--------|-------------------|------------------|
| **Cross-referencing** | Intra-section links | Explicit cross-doc concept links (tagged) |
| **Context building** | Narrative accumulation | Unified knowledge graph formation |
| **Coherence** | Overall flow | Logical synthesis with cross-doc transitions |

### Scoring Rubric
- **1.0**: 80%+ key concepts linked accurately across docs
- **0.5**: 50-79% linked
- **0.0**: <50% linked

---

## Falsification Criteria

### What Would Disprove the Hypothesis

1. **Aggregate <0.600**: Cross-doc isolation creates overload (history too disparate)
2. **Error rate >20%**: LLM confabulates links (invents connections)
3. **Round 3 coherence drops >0.2 from Round 2**: History dilution issue

### Confounding Variables to Control
- Document length: Normalize to ~2,000 words/doc
- Rater bias: Blind scoring + Test 7 calibration
- Budget creep: Cap history at 500 chars/doc
- LLM version: Same model as Test 7

---

## Predicted Output Pattern

**Baseline Round 2** (expected):
```
# Apache Flink Key Patterns
## 1. JobManager Pattern
- Central coordinator...
```
(Starts fresh, no Spark reference)

**Comonadic Round 2** (expected):
```
# Cross-Framework Patterns: Flink Integration

Building on Spark's driver-executor model (Doc 1), Flink's JobManager
serves an analogous coordination role with key differences...

## Pattern 3: Stream-First Execution (extends Spark's batch model)
```
(Explicit cross-referencing)

---

## Implementation Checklist

- [ ] Gather 5 documents (download/extract text)
- [ ] Create `run_test_9_crossdoc.py` based on Test 7
- [ ] Add document identifiers to history
- [ ] Add synthesis-focused prompt pattern
- [ ] Run 5x for statistical power
- [ ] Calculate p-value (t-test, comonadic vs baseline)
- [ ] Compare against success criteria

---

## Expected Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Document gathering | 1 hour | 5 text files |
| Code implementation | 2 hours | `run_test_9_crossdoc.py` |
| Single test run | 30 min | Initial results |
| Full validation (5x) | 2.5 hours | Statistical analysis |
| **Total** | **~6 hours** | Validated results |

---

## Comparison to Test 7

| Aspect | Test 7 | Test 9 |
|--------|--------|--------|
| Source | 1 document (3 sections) | 5 documents |
| Isolation | High (section-only) | Maximum (document-only) |
| Coherence Gap | 0.9 | 0.95 (predicted) |
| Predicted Δ | +156% (actual) | +150-200% |
| Novel Challenge | Intra-doc synthesis | Cross-doc synthesis |

---

**Next Step**: Gather documents and implement `run_test_9_crossdoc.py`
