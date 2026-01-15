# Agent 7: Audit & Reset Agent

**Responsibility**: Learning logs, model snapshots, one-click reset

**Priority**: P1 (Compliance - Required for GDPR/CCPA)

---

## Task 7.1: Implement Learning Activity Audit Log

**Description**: Comprehensive audit trail of all learning operations for transparency and compliance

**Acceptance Criteria**:
- [ ] Extend AIActivityLog model to track:
  - Learning enabled/disabled events
  - Consent timestamps
  - Pattern updates (which patterns changed)
  - Suggestion generations
  - User responses (accept/reject/dismiss)
  - Data exports
  - Data deletions
  - Pattern reverts
- [ ] Include metadata:
  - Timestamp
  - User ID
  - Action type
  - Entity target
  - Reasoning/context
  - Result (success/failure)
- [ ] Log retention: 2 years (compliance requirement)
- [ ] API endpoint: GET /api/learning/audit-log

**Files**:
- `backend/src/models/activity.py` (extend)
- `backend/src/services/audit_logger.py` (new)
- `backend/tests/test_audit_logging.py` (new)

**Dependencies**: None (foundation for compliance)

**Estimated Effort**: 7 hours

---

## Task 7.2: Implement Pattern Version Snapshots

**Description**: Store historical versions of learned patterns for rollback and auditability

**Acceptance Criteria**:
- [ ] Create PatternSnapshot model:
  - snapshot_id (UUID)
  - user_id
  - pattern_type (peak_hours, type_timing, priority, grouping)
  - pattern_data (JSON)
  - confidence_score
  - data_points_count
  - created_at
  - snapshot_reason (daily_update, manual_refresh, revert)
- [ ] Automatically create snapshot before pattern updates
- [ ] Keep last 10 snapshots per user per pattern type
- [ ] Auto-delete snapshots older than 90 days
- [ ] API endpoint: GET /api/learning/patterns/:type/history

**Files**:
- `backend/src/models/pattern_snapshot.py` (new)
- `backend/src/services/snapshot_service.py` (new)
- `backend/migrations/versions/xxx_create_pattern_snapshots.py` (new)
- `backend/tests/test_pattern_snapshots.py` (new)

**Dependencies**: Task 3.7 (Pattern updates)

**Estimated Effort**: 8 hours

---

## Task 7.3: Implement Complete Learning Reset

**Description**: One-click deletion of ALL learning data with full audit trail

**Acceptance Criteria**:
- [ ] Comprehensive reset deletes:
  - ✅ All BehavioralEvent records (user_id match)
  - ✅ UserBehaviorProfile record
  - ✅ All AdaptiveSuggestion records
  - ✅ All PatternSnapshot records
  - ✅ Learning-related audit logs (keep deletion event itself)
- [ ] Reset UserPreferences:
  - learning_enabled = false
  - learning_categories = []
  - pattern_visibility = "high" (default)
- [ ] Confirmation modal with checkboxes:
  - ☐ I understand this cannot be undone
  - ☐ I want to delete all my learning data (X events, Y patterns)
  - [Delete My Data] button (danger styling)
- [ ] Log deletion event with summary:
  - Events deleted: count
  - Patterns deleted: types
  - Snapshots deleted: count
- [ ] Email confirmation: "Your learning data has been deleted"
- [ ] API endpoint: DELETE /api/learning/reset

**Files**:
- `frontend/src/components/ResetLearningModal.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/reset_service.py` (new)
- `backend/tests/test_complete_reset.py` (new)

**Dependencies**: Task 7.1 (Audit logging)

**Estimated Effort**: 9 hours

---

## Task 7.4: Implement Audit Log Viewer UI

**Description**: User-facing interface to view their learning activity history

**Acceptance Criteria**:
- [ ] Create audit log viewer page
- [ ] Display events in reverse chronological order
- [ ] Filter by:
  - Event type (consent, pattern_update, suggestion, response, export, deletion)
  - Date range (last 7/30/90 days, all time)
  - Action result (success, failure)
- [ ] Show event details:
  - Timestamp
  - Action description
  - Result
  - Context (e.g., "Pattern updated: peak_hours")
- [ ] Pagination: 20 events per page
- [ ] Export audit log as JSON or CSV

**Files**:
- `frontend/src/pages/AuditLogPage.tsx` (new)
- `frontend/src/components/AuditLogViewer.tsx` (new)
- `frontend/src/components/AuditEventCard.tsx` (new)
- `backend/src/routers/learning.py` (extend - add filters)

**Dependencies**: Task 7.1

**Estimated Effort**: 8 hours

---

## Task 7.5: Implement Data Export with Full History

**Description**: GDPR Article 15 compliance - export all user learning data in machine-readable format

**Acceptance Criteria**:
- [ ] Generate comprehensive JSON export including:
  - User consent history (timestamps, status changes)
  - All behavioral events (raw data)
  - Current learned patterns (all types)
  - Pattern snapshot history (last 10 per type)
  - Suggestion history (all suggestions + responses)
  - Audit log (all learning events)
  - Metadata (export timestamp, data version)
- [ ] Format as structured JSON with explanatory comments
- [ ] Include data dictionary explaining each field
- [ ] File size estimate before download
- [ ] API endpoint: GET /api/learning/export?format=json
- [ ] Support CSV export as alternative format
- [ ] Log export event to audit trail

**Files**:
- `backend/src/services/data_export.py` (extend from Task 2.7)
- `backend/src/exporters/json_exporter.py` (new)
- `backend/src/exporters/csv_exporter.py` (new)
- `backend/tests/test_data_export.py` (new)

**Dependencies**: Task 7.1, Task 7.2

**Estimated Effort**: 9 hours

---

## Task 7.6: Implement Privacy Validation Test Suite

**Description**: Automated tests ensuring no privacy violations in learning system

**Acceptance Criteria**:
- [ ] Test: No task content in BehavioralEvent
  - Verify title, description, notes NOT stored
  - Verify task_type_hash is one-way (not reversible)
- [ ] Test: No PII in any learning data
  - Verify user name, email NOT stored
  - Verify no identifiable information
- [ ] Test: User isolation
  - Verify user A cannot access user B's patterns
  - Verify cross-user data leakage impossible
- [ ] Test: Complete data deletion
  - Verify reset deletes ALL user learning data
  - Verify no orphaned records remain
- [ ] Test: Audit trail completeness
  - Verify all learning operations are logged
  - Verify audit log includes deletion events
- [ ] Run in CI/CD pipeline on every commit

**Files**:
- `backend/tests/privacy/test_no_content_leakage.py` (new)
- `backend/tests/privacy/test_user_isolation.py` (new)
- `backend/tests/privacy/test_complete_deletion.py` (new)
- `backend/tests/privacy/test_audit_completeness.py` (new)
- `.github/workflows/privacy-validation.yml` (new)

**Dependencies**: All previous tasks

**Estimated Effort**: 10 hours

---

## Task 7.7: Implement Learning Health Dashboard (Admin)

**Description**: Internal monitoring dashboard for learning system health

**Acceptance Criteria**:
- [ ] Admin-only dashboard showing:
  - Total users with learning enabled
  - Average data points per user
  - Pattern detection success rate
  - Suggestion acceptance rate (aggregate)
  - System health metrics (API latency, job status)
  - Privacy compliance score (test pass rate)
  - Error rates by endpoint
- [ ] Alerts for:
  - Privacy test failures
  - Batch learning job failures
  - Suggestion acceptance rate drops below 50%
  - API error rate exceeds 1%
- [ ] Historical trends (last 30 days)
- [ ] Export metrics as CSV

**Files**:
- `backend/src/admin/learning_dashboard.py` (new)
- `backend/src/services/metrics_collector.py` (new)
- `frontend/src/pages/admin/LearningHealthPage.tsx` (new - admin only)

**Dependencies**: Task 7.1, Task 7.6

**Estimated Effort**: 12 hours

---

**Total Agent Effort**: 63 hours
