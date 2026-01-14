# Learning Policy Documentation - Phase 5

**Version**: 1.0.0
**Last Updated**: 2026-01-14
**Status**: Production-Ready

---

## Overview

Phase 5 implements **privacy-preserving behavioral learning** to personalize task suggestions and workflows while maintaining strict privacy boundaries. This document defines what can be learned, what cannot be learned, and how learned patterns decay over time.

**Core Principle**: Only behavioral metadata (timing, frequency, grouping) is learned. NO task content, titles, descriptions, or user-defined metadata is ever stored.

---

## 1. Learnable Signals (Privacy-Safe)

These signals represent **behavioral metadata** that is privacy-safe to learn:

### 1.1 Hour of Day (`hour_of_day`)
- **Description**: Hour when task action occurred (0-23)
- **Data Type**: Integer (0-23)
- **Purpose**: Learn peak productivity hours
- **Example**: User completes tasks at 14:00 → learns afternoon productivity pattern
- **Privacy**: ✅ Safe - temporal metadata only

### 1.2 Day of Week (`day_of_week`)
- **Description**: Day when action occurred (0=Monday, 6=Sunday)
- **Data Type**: Integer (0-6)
- **Purpose**: Learn weekly patterns
- **Example**: User works on specific task types on Mondays → learns Monday behavior
- **Privacy**: ✅ Safe - temporal metadata only

### 1.3 Task Type Hash (`task_type_hash`)
- **Description**: One-way SHA-256 hash of generic task type
- **Data Type**: String (64-character hexadecimal)
- **Purpose**: Identify task type patterns without revealing content
- **Example**: "email" → `a3f4b2c1...` (one-way hash, NOT reversible)
- **Privacy**: ✅ Safe - cannot reconstruct original content
- **CRITICAL**: Only hash generic types ("email", "meeting"), NEVER task titles or descriptions

### 1.4 Session ID (`session_id`)
- **Description**: Session identifier for grouping related actions
- **Data Type**: String (≤64 characters)
- **Purpose**: Learn task grouping behaviors
- **Example**: Tasks completed in same session → learns batching preference
- **Privacy**: ✅ Safe - session identifier only, no content

### 1.5 Event Type (`event_type`)
- **Description**: Type of behavioral event
- **Data Type**: Enum (`task_completed`, `priority_changed`, `task_grouped`)
- **Purpose**: Track which behaviors to learn from
- **Example**: `task_completed` event → learn completion timing
- **Privacy**: ✅ Safe - action type only

### 1.6 Priority Change (`priority_change`)
- **Description**: Priority adjustment pattern (from → to)
- **Data Type**: String (e.g., "low->high", "medium->high")
- **Purpose**: Learn priority adjustment preferences
- **Example**: User changes "low" to "high" in mornings → learns prioritization pattern
- **Privacy**: ✅ Safe - priority metadata only

---

## 2. Forbidden Signals (Privacy Violations)

These signals are **NEVER learned or stored** to protect user privacy:

### 2.1 Task Content
- ❌ `task_title` - Task titles contain sensitive information
- ❌ `task_description` - Task descriptions contain sensitive information
- ❌ `task_notes` - Notes may contain personal information
- ❌ `attachment_content` - Attachments may contain sensitive data

### 2.2 User-Defined Metadata
- ❌ `user_category` - User-defined categories reveal personal organization
- ❌ `user_tag` - Tags may contain sensitive labels
- ❌ `task_metadata` - Custom metadata may contain PII

### 2.3 Personally Identifiable Information (PII)
- ❌ `user_name` - User name is PII
- ❌ `user_email` - Email address is PII
- ❌ Any other identifiable information

**Enforcement**: Automated privacy validation tests in CI/CD pipeline block deployment if any forbidden signals are detected in learning data.

---

## 3. Signal Decay Policy

Behavioral patterns decay over time to ensure recent behavior is weighted more heavily than old behavior.

### 3.1 Decay Formula

**Exponential Decay**:
```
decay_weight = 2^(-days_old / half_life_days)
```

### 3.2 Decay Profiles

| Pattern Type | Profile | Half-Life | Min Confidence | Max Age |
|:---|:---|---:|---:|---:|
| **Peak Hours** | Medium | 30 days | 0.50 | 90 days |
| **Type Timing** | Medium | 30 days | 0.50 | 90 days |
| **Priority Adjustment** | Fast | 14 days | 0.55 | 60 days |
| **Grouping** | Slow | 60 days | 0.45 | 120 days |

### 3.3 Decay Weights by Age

| Age Range | Weight | Explanation |
|:---|---:|:---|
| 0-30 days | 1.0 | Recent behavior - full weight |
| 31-60 days | 0.7 | Moderately recent - 70% weight |
| 61-90 days | 0.4 | Older behavior - 40% weight |
| 91+ days | 0.2 | Old behavior - 20% weight |

---

## 4. Forgetting Rules

Patterns are automatically forgotten when they become stale or unreliable.

### 4.1 Forgetting Triggers

#### Age Threshold
- **Rule**: Pattern older than `max_age_days` is forgotten
- **Example**: Peak hours pattern older than 90 days → forgotten
- **Reason**: User behavior likely changed

#### Inactivity
- **Rule**: No new data points in 60+ days
- **Example**: No task completions in 2 months → pattern forgotten
- **Reason**: Insufficient reinforcement

#### Low Confidence
- **Rule**: Confidence score drops below `min_confidence`
- **Example**: Priority pattern confidence < 0.55 → forgotten
- **Reason**: Pattern no longer reliable

#### Insufficient Data
- **Rule**: Less than 3 data points supporting pattern
- **Example**: Only 2 completions for task type → pattern forgotten
- **Reason**: Not statistically significant

### 4.2 User-Initiated Forgetting

Users can trigger forgetting at any time:
- **Complete Reset**: Delete ALL learning data (GDPR Article 17 compliance)
- **Pattern Revert**: Revert specific pattern to previous version
- **Learning Pause**: Temporarily stop learning (resume later)

---

## 5. Confidence Scoring

Pattern confidence indicates reliability of learned behavior.

### 5.1 Confidence Formula

```
confidence = (frequency_weight * 0.4) + (recency_weight * 0.3) + (consistency_weight * 0.3)
```

### 5.2 Component Definitions

**Frequency Weight** (40%):
- Based on number of data points supporting pattern
- More data points → higher confidence

**Recency Weight** (30%):
- Based on how recent the data points are
- More recent data → higher confidence
- Uses exponential decay

**Consistency Weight** (30%):
- Based on how consistent the pattern is
- Low variance → higher confidence
- High variance → lower confidence

### 5.3 Confidence Thresholds

| Threshold | Value | Purpose |
|:---|---:|:---|
| **Pattern Detection** | ≥ 0.40 | Minimum to detect pattern |
| **Suggestion Generation** | ≥ 0.60 | Minimum to generate suggestion |
| **High Confidence** | ≥ 0.75 | Pattern strongly established |
| **Pattern Forgetting** | < 0.45 | Pattern forgotten (too low) |

---

## 6. Minimum Data Requirements

Patterns require minimum data to be statistically meaningful.

### 6.1 Cold Start Period

- **Minimum Events**: 20 events before showing patterns
- **Reason**: Prevents premature suggestions with insufficient data
- **User Experience**: "Building your profile (12/20 events collected)"

### 6.2 Pattern-Specific Minimums

| Pattern Type | Min Events | Min Days | Reason |
|:---|---:|---:|:---|
| **Peak Hours** | 20 completions | 7 days | Need weekly pattern |
| **Type Timing** | 15 per type | 7 days | Need type-specific data |
| **Priority Adjustment** | 10 changes | 7 days | Need adjustment pattern |
| **Grouping** | 15 sessions | 5 days | Need grouping behavior |

---

## 7. Privacy Compliance

### 7.1 GDPR Compliance

**Article 15 - Right to Access**:
- Users can view ALL learned patterns
- API: `GET /api/learning/patterns`
- Includes: pattern data, confidence scores, data point counts

**Article 17 - Right to Erasure**:
- Users can delete ALL learning data with one click
- API: `DELETE /api/learning/reset`
- Complete deletion within 24 hours

### 7.2 CCPA Compliance

**Opt-In Required**:
- Learning disabled by default (`learning_enabled=false`)
- Explicit consent required before any data collection
- Clear disclosure of what is learned

**Data Export**:
- Users can export ALL learning data
- API: `GET /api/learning/export`
- Format: JSON with data dictionary

### 7.3 Automated Privacy Validation

**CI/CD Pipeline Tests**:
- ✅ No task content in `BehavioralEvent`
- ✅ No PII in learning data
- ✅ User isolation (cross-user data access prevention)
- ✅ Complete data deletion works
- ✅ Audit trail completeness

**Deployment Blocker**: Privacy tests MUST pass before deployment.

---

## 8. User Control & Transparency

### 8.1 Learning Controls

**Enable/Disable**:
- Toggle learning on/off at any time
- Effect: Stop all data collection immediately

**Pause/Resume**:
- Temporarily pause learning
- Resume without losing existing patterns

**Category Selection**:
- Choose which pattern types to learn
- Options: timing patterns, priority patterns, grouping patterns

### 8.2 Pattern Visibility

**Interactive Visualizations**:
- Peak hours bar chart
- Task type timing heatmap
- Priority flow Sankey diagram

**Explanations**:
- "What changed?" - Show pattern changes over time
- "Why it changed?" - Explain reason for pattern update
- "How to revert?" - One-click pattern rollback

### 8.3 Data Transparency

**Learning Status Dashboard**:
- Data points collected: 156 events
- Patterns detected: 3 (peak hours, type timing, priority)
- Confidence scores: High (0.82), Medium (0.67), Low (0.51)
- Days since enabled: 14 days

---

## 9. Implementation Checklist

### ✅ Phase 1: Foundation (BLOCKING)
- [x] Define learnable signal specification
- [x] Define forbidden signal policy
- [x] Implement signal decay rules
- [x] Implement forgetting rules
- [x] Create learning policy documentation

### 🔄 Phase 2: Consent & Controls (BLOCKING)
- [ ] Implement opt-in consent flow
- [ ] Implement opt-out flow
- [ ] Implement pause/resume learning
- [ ] Implement learning category selection
- [ ] Implement complete learning reset
- [ ] Implement learning status indicator
- [ ] Implement data export

---

## 10. References

- **ADR-001**: Privacy-Preserving Behavioral Learning Architecture
- **ADR-002**: Pattern Analysis and Confidence Scoring System
- **ADR-003**: User Control and Transparency Framework
- **Specification**: `specs/005-adaptive-intelligence/spec.md`
- **Implementation Plan**: `specs/005-adaptive-intelligence/plan.md`

---

**Questions or Concerns?**

If you have questions about the learning policy or want to report a privacy concern, please:
1. Review ADRs for architectural decisions
2. Check automated privacy tests in `backend/tests/privacy/`
3. Submit issue on GitHub repository

---

**Last Reviewed**: 2026-01-14
**Next Review**: 2026-04-14 (quarterly review)
