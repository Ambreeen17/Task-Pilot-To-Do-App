# ADR-001: Privacy-Preserving Behavioral Learning Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-14
- **Feature:** 005-adaptive-intelligence
- **Context:** Phase 5 introduces adaptive intelligence through behavioral learning to personalize task suggestions and prioritization. However, learning from user behavior poses significant privacy risks if task content is captured. The system must balance personalization benefits against user privacy concerns while maintaining GDPR/CCPA compliance. This architecture decision addresses the fundamental question: how can we learn from user behavior without compromising privacy?

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes privacy foundation for all learning features
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Content-based learning vs metadata-only vs no learning
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects data models, APIs, frontend, testing, compliance
-->

## Decision

Implement a **privacy-first behavioral learning architecture** using metadata aggregation without storing task content:

**Data Collection Strategy:**
- **Capture:** Only behavioral metadata (timing, frequency, grouping patterns)
- **Exclude:** All task content, titles, descriptions, categories, user-defined metadata
- **Hashing:** One-way hash for task type identification (not reversible to content)
- **Storage:** Client-side event capture → Server-side aggregated pattern storage

**Architecture Components:**
- **BehavioralEvent Model:** Captures hour_of_day, day_of_week, task_type_hash, session_id only
- **UserBehaviorProfile Model:** Stores aggregated statistical patterns (peak_hours, type_timing_patterns, priority_adjustment_patterns, grouping_patterns) as JSON
- **Privacy Validation:** Automated tests verify no content leakage at every API boundary
- **User Control:** Opt-in consent required, full data visibility, one-click data deletion

**Privacy Boundaries:**
```python
# What IS learned (privacy-safe)
✅ Task completion timing (hour of day, day of week)
✅ Priority change frequency and patterns
✅ Task grouping behaviors (session-based)
✅ Aggregated statistical patterns

# What IS NOT learned (privacy-protected)
❌ Task titles, descriptions, or content
❌ User-defined categories or tags
❌ Task metadata (notes, attachments)
❌ Any personally identifiable information
```

**Compliance Measures:**
- GDPR Article 17 (Right to Erasure): DELETE /api/learning/reset
- GDPR Article 15 (Right to Access): GET /api/learning/patterns
- CCPA compliance: Opt-in required, data export available
- Encryption: AES-256 at rest, TLS 1.3 in transit
- Isolation: Per-user data partitioning, no cross-user learning

## Consequences

### Positive

1. **Privacy by Design:** Zero risk of task content exposure - system architecturally incapable of storing sensitive data
2. **User Trust:** Transparent learning boundaries build confidence and adoption
3. **Compliance:** GDPR/CCPA compliant by design, no retrofit needed
4. **Reduced Liability:** Minimal PII storage reduces breach impact and regulatory risk
5. **Scalability:** Aggregated patterns are compact (<10KB per user), enabling efficient storage and query
6. **Reversibility:** Complete data deletion in single operation maintains user control
7. **Auditability:** Automated privacy tests provide continuous validation

### Negative

1. **Learning Limitations:** Cannot learn from semantic task content (e.g., "always prioritize client emails")
2. **Reduced Personalization:** Metadata-only limits suggestion specificity compared to content-based learning
3. **Complexity:** Hash-based type identification requires careful implementation to avoid collisions
4. **Cold Start:** New users need 2+ weeks of behavioral data before patterns emerge
5. **Pattern Drift Detection:** Limited context makes it harder to understand why patterns change
6. **Development Overhead:** Privacy validation tests required for every data-touching feature
7. **Debugging Difficulty:** Cannot inspect actual task content when troubleshooting pattern detection

## Alternatives Considered

### Alternative A: Content-Based Learning with Encryption
**Approach:** Store encrypted task content and use NLP for semantic learning
**Components:**
- Task content encrypted with user-specific keys
- Server-side NLP processing on decrypted content
- Learning from task titles, descriptions, categories

**Why Rejected:**
- ❌ Higher privacy risk: Encryption breach exposes all content
- ❌ Key management complexity: User keys must be stored/managed
- ❌ Compliance uncertainty: Encrypted PII still subject to regulations
- ❌ Cannot guarantee "right to be forgotten" if backups exist
- ❌ User trust: Even encrypted, storing content creates perceived risk

### Alternative B: No Behavioral Learning (Static Rules Only)
**Approach:** Use hand-coded heuristics and rules for suggestions
**Components:**
- Fixed prioritization rules (deadline proximity, manual priority)
- No adaptation to user preferences
- Generic suggestions for all users

**Why Rejected:**
- ❌ Limited value: Cannot personalize to individual work patterns
- ❌ Poor UX: Users must manually configure all preferences
- ❌ Maintenance burden: Rules require constant tuning
- ❌ No improvement: System never gets better with usage
- ❌ Competitive disadvantage: Other tools offer adaptive learning

### Alternative C: Client-Side Only Learning (Local Storage)
**Approach:** All learning happens in browser with localStorage/IndexedDB
**Components:**
- Patterns computed and stored entirely client-side
- No server-side aggregation or persistence
- Each device learns independently

**Why Rejected:**
- ❌ Multi-device inconsistency: Patterns don't sync across devices
- ❌ Data loss risk: Browser storage can be cleared/corrupted
- ❌ Limited compute: Complex pattern analysis constrained by client device
- ❌ No backup: User loses all learning if device is lost
- ❌ Implementation complexity: Duplicate logic across platforms

### Decision Rationale

**Metadata-only learning (chosen approach)** provides the best balance:
- ✅ Strong privacy guarantees build user trust
- ✅ Sufficient signal for useful personalization (timing, frequency, grouping)
- ✅ Compliant by design with minimal legal risk
- ✅ Scalable architecture with low storage overhead
- ✅ Cross-device sync with server-side aggregation
- ⚖️ Trade learning power for privacy - acceptable for Phase 5 MVP

## References

- Feature Spec: `specs/005-adaptive-intelligence/spec.md`
- Implementation Plan: `specs/005-adaptive-intelligence/plan.md` (sections 2, 5)
- Related ADRs: ADR-002 (Pattern Analysis), ADR-003 (User Control)
- Privacy Requirements: Spec FR-003, FR-006, FR-008, FR-010
- Success Criteria: SC-003 (95% privacy compliance)
