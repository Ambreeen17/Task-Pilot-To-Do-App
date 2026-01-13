# Phase 4: Autonomous & Proactive Todo System - API Contracts

**Feature Branch**: `004-autonomous-todo`
**Status**: DRAFT → IMPLEMENTATION
**Specification**: `specs/004-autonomous-todo/spec.md`
**Plan**: `specs/004-autonomous-todo/plan.md`
**Last Updated**: 2026-01-14

## Overview

This document defines the API contracts for the autonomous todo agent system. All endpoints follow REST conventions and include comprehensive request/response schemas, error handling, and authentication requirements.

## Base Configuration

### Base URL
```
Backend API: http://localhost:8000/api (development)
Frontend API: http://localhost:3000/api (Next.js proxy)
```

### Authentication
All endpoints (except health checks) require JWT authentication:
```
Authorization: Bearer <JWT_TOKEN>
```

### Content-Type
```
Content-Type: application/json
```

### Rate Limiting
- Standard endpoints: 100 requests/10 minutes per user
- AI analysis endpoints: 50 requests/10 minutes per user
- Autonomous action endpoints: 20 requests/10 minutes per user

## API Endpoints

### 1. Autonomy Settings API

#### GET /ai/autonomy/settings
**Description**: Retrieve current autonomy configuration for the authenticated user.

**Request**:
```http
GET /ai/autonomy/settings
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "autonomy_level": "medium",
  "enabled_categories": ["reminders", "scheduling"],
  "work_hours": {
    "start": 9,
    "end": 17
  },
  "timezone": "America/New_York",
  "created_at": "2026-01-14T10:30:00Z",
  "updated_at": "2026-01-14T14:20:00Z"
}
```

**Response Schema**:
```typescript
interface AutonomySettings {
  autonomy_level: "low" | "medium" | "high";
  enabled_categories: string[];
  work_hours: {
    start: number; // 0-23
    end: number;   // 0-23
  };
  timezone: string; // IANA timezone
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: User preferences not found (create default)

#### PUT /ai/autonomy/settings
**Description**: Update user's autonomy preferences.

**Request**:
```http
PUT /ai/autonomy/settings
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "autonomy_level": "high",
  "enabled_categories": ["reminders", "scheduling", "insights"],
  "work_hours": {
    "start": 8,
    "end": 19
  },
  "timezone": "Europe/London"
}
```

**Request Schema**:
```typescript
interface UpdateAutonomySettings {
  autonomy_level?: "low" | "medium" | "high";
  enabled_categories?: string[];
  work_hours?: {
    start?: number;
    end?: number;
  };
  timezone?: string;
}
```

**Response (200 OK)**:
```json
{
  "message": "Autonomy settings updated successfully",
  "settings": {
    "autonomy_level": "high",
    "enabled_categories": ["reminders", "scheduling", "insights"],
    "work_hours": {
      "start": 8,
      "end": 19
    },
    "timezone": "Europe/London",
    "updated_at": "2026-01-14T15:30:00Z"
  }
}
```

**Validation Rules**:
- `autonomy_level`: Must be valid enum value
- `enabled_categories`: Must contain valid category names
- `work_hours.start`: Must be < `work_hours.end`, both 0-23
- `timezone`: Must be valid IANA timezone
- At least one field must be provided

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing JWT token
- `422 Unprocessable Entity`: Validation errors

### 2. AI Analysis Engine API

#### POST /ai/analyze
**Description**: Trigger AI analysis and generate structured suggestions based on user's task data.

**Request**:
```http
POST /ai/analyze
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "include_categories": ["deadline_risk", "pattern_detection", "workload_optimization"],
  "time_period": {
    "start": "2026-01-14T00:00:00Z",
    "end": "2026-01-21T23:59:59Z"
  }
}
```

**Request Schema**:
```typescript
interface AnalyzeRequest {
  include_categories: Array<
    "deadline_risk" |
    "pattern_detection" |
    "workload_optimization" |
    "recurring_tasks" |
    "time_optimization"
  >;
  time_period?: {
    start: string; // ISO 8601
    end: string;   // ISO 8601
  };
}
```

**Response (200 OK)**:
```json
{
  "analysis_id": "analysis_12345",
  "timestamp": "2026-01-14T15:45:00Z",
  "suggestions": [
    {
      "id": "suggestion_001",
      "type": "deadline_risk",
      "task_id": "task_abc123",
      "message": "Task 'Complete report' is due in 2 hours",
      "confidence": 0.95,
      "actions": ["reminder", "reschedule"],
      "priority": "high",
      "reasoning": "Task has high priority and due date approaching",
      "suggested_changes": {
        "due_date": "2026-01-15T14:00:00Z",
        "priority": "high"
      }
    },
    {
      "id": "suggestion_002",
      "type": "pattern_detection",
      "message": "You create 'Gym' tasks every Monday. Consider making it recurring?",
      "confidence": 0.85,
      "actions": ["create_recurring"],
      "priority": "medium",
      "reasoning": "Detected weekly pattern in task creation",
      "suggested_changes": {
        "recurrence": {
          "type": "weekly",
          "interval": 1,
          "day_of_week": "monday"
        }
      }
    }
  ],
  "metrics": {
    "total_tasks": 15,
    "overdue_tasks": 3,
    "tasks_due_today": 5,
    "workload_score": 0.8,
    "risk_level": "medium"
  },
  "analysis_duration": 2.3
}
```

**Response Schema**:
```typescript
interface AnalyzeResponse {
  analysis_id: string;
  timestamp: string; // ISO 8601
  suggestions: Suggestion[];
  metrics: Metrics;
  analysis_duration: number; // seconds
}

interface Suggestion {
  id: string;
  type: string;
  task_id?: string;
  message: string;
  confidence: number; // 0.0-1.0
  actions: string[];
  priority: "low" | "medium" | "high";
  reasoning: string;
  suggested_changes: Record<string, any>;
}

interface Metrics {
  total_tasks: number;
  overdue_tasks: number;
  tasks_due_today: number;
  workload_score: number; // 0.0-1.0
  risk_level: "low" | "medium" | "high";
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing JWT token
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: AI service temporarily unavailable

#### POST /ai/analyze/quick
**Description**: Quick analysis for immediate suggestions (limited scope).

**Request**:
```http
POST /ai/analyze/quick
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "categories": ["deadline_risk"]
}
```

**Response**: Same as `/ai/analyze` but faster with limited analysis scope.

### 3. Autonomous Action Management API

#### GET /ai/actions
**Description**: List pending and recent autonomous actions for the user.

**Request**:
```http
GET /ai/actions?status=pending&limit=20&offset=0
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters**:
- `status`: Filter by status ("pending", "approved", "rejected", "executed", "all")
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `action_type`: Filter by action type
- `start_date`: Filter actions after this date
- `end_date`: Filter actions before this date

**Response (200 OK)**:
```json
{
  "actions": [
    {
      "id": 123,
      "action_type": "reminder",
      "target_task_id": "task_abc123",
      "message": "Task 'Complete report' due in 2 hours",
      "confidence": 0.95,
      "status": "pending",
      "reason": "Deadline approaching",
      "suggested_changes": {
        "reminder_time": "2026-01-14T16:00:00Z"
      },
      "created_at": "2026-01-14T15:30:00Z",
      "executed_at": null
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

**Response Schema**:
```typescript
interface ActionsResponse {
  actions: AutonomousActionSummary[];
  pagination: PaginationInfo;
}

interface AutonomousActionSummary {
  id: number;
  action_type: string;
  target_task_id?: string;
  message: string;
  confidence: number;
  status: "pending" | "approved" | "rejected" | "executed";
  reason: string;
  suggested_changes: Record<string, any>;
  created_at: string;
  executed_at?: string;
}
```

**Error Responses**:
- `400 Bad Request`: Invalid query parameters
- `401 Unauthorized`: Invalid or missing JWT token

#### POST /ai/actions/{action_id}/approve
**Description**: Approve and execute a pending autonomous action.

**Request**:
```http
POST /ai/actions/123/approve
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "reason": "User manually approved the suggestion"
}
```

**Response (200 OK)**:
```json
{
  "action_id": 123,
  "status": "executed",
  "result": {
    "task_id": "task_abc123",
    "changes": {
      "due_date": "2026-01-15T14:00:00Z"
    }
  },
  "reasoning": "Task rescheduled successfully",
  "execution_time": 0.5
}
```

**Error Responses**:
- `400 Bad Request`: Action not in pending status
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Action not found or not owned by user
- `422 Unprocessable Entity`: Action cannot be executed

#### POST /ai/actions/{action_id}/reject
**Description**: Reject a pending autonomous action.

**Request**:
```http
POST /ai/actions/123/reject
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "reason": "Task is not urgent",
  "feedback": "Please be less aggressive with reminders"
}
```

**Response (200 OK)**:
```json
{
  "action_id": 123,
  "status": "rejected",
  "reason": "Task is not urgent",
  "feedback": "Please be less aggressive with reminders",
  "rejected_at": "2026-01-14T15:45:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Action not in pending status
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Action not found or not owned by user

#### POST /ai/actions/{action_id}/execute
**Description**: Execute an approved autonomous action (manual trigger).

**Request**:
```http
POST /ai/actions/123/execute
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "action_id": 123,
  "status": "executed",
  "result": {
    "task_id": "task_abc123",
    "changes": {
      "due_date": "2026-01-15T14:00:00Z"
    }
  },
  "execution_time": 0.3
}
```

**Error Responses**:
- `400 Bad Request`: Action not in approved status
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Action not found or not owned by user
- `422 Unprocessable Entity`: Action cannot be executed

### 4. Activity Logging API

#### GET /ai/activity
**Description**: Retrieve activity log for autonomous actions.

**Request**:
```http
GET /ai/activity?start_date=2026-01-01&end_date=2026-01-14&limit=50
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters**:
- `start_date`: Filter logs after this date
- `end_date`: Filter logs before this date
- `action_type`: Filter by action type
- `status`: Filter by status
- `limit`: Number of results (default: 50, max: 200)
- `offset`: Pagination offset

**Response (200 OK)**:
```json
{
  "activity": [
    {
      "id": 456,
      "action_type": "autonomous_reminder_suggested",
      "entity_target": "AutonomousAction:123",
      "reasoning": "Task 'Complete report' due in 2 hours",
      "status": "suggested",
      "timestamp": "2026-01-14T15:30:00Z",
      "result": null
    },
    {
      "id": 457,
      "action_type": "autonomous_reminder_approved",
      "entity_target": "AutonomousAction:123",
      "reasoning": "User approved autonomous reminder",
      "status": "approved",
      "timestamp": "2026-01-14T15:35:00Z",
      "result": {
        "reminder_set": true,
        "reminder_time": "2026-01-14T16:00:00Z"
      }
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

**Response Schema**:
```typescript
interface ActivityResponse {
  activity: ActivityLogEntry[];
  pagination: PaginationInfo;
}

interface ActivityLogEntry {
  id: number;
  action_type: string;
  entity_target: string;
  reasoning: string;
  status: string;
  timestamp: string;
  result?: Record<string, any>;
}
```

#### POST /ai/activity/export
**Description**: Export activity log to various formats.

**Request**:
```http
POST /ai/activity/export
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "format": "json",
  "start_date": "2026-01-01",
  "end_date": "2026-01-14",
  "include_details": true
}
```

**Response (200 OK)**:
```json
{
  "export_id": "export_123",
  "format": "json",
  "download_url": "/ai/activity/downloads/export_123.json",
  "expires_at": "2026-01-15T15:30:00Z"
}
```

### 5. Proactive Notifications API

#### GET /ai/notifications
**Description**: Get proactive notifications and suggestions.

**Request**:
```http
GET /ai/notifications?unread_only=true&limit=10
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "notifications": [
    {
      "id": "notif_001",
      "type": "deadline_warning",
      "priority": "high",
      "title": "Task Due Soon",
      "message": "Task 'Complete report' is due in 2 hours",
      "task_id": "task_abc123",
      "created_at": "2026-01-14T15:30:00Z",
      "read": false,
      "dismissed": false
    }
  ],
  "unread_count": 3
}
```

**Response Schema**:
```typescript
interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
}

interface Notification {
  id: string;
  type: string;
  priority: "low" | "medium" | "high";
  title: string;
  message: string;
  task_id?: string;
  created_at: string;
  read: boolean;
  dismissed: boolean;
}
```

#### POST /ai/notifications/{notification_id}/dismiss
**Description**: Dismiss a proactive notification.

**Request**:
```http
POST /ai/notifications/notif_001/dismiss
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "notification_id": "notif_001",
  "dismissed": true,
  "dismissed_at": "2026-01-14T15:45:00Z"
}
```

### 6. Health & Status API

#### GET /ai/health
**Description**: Check AI service status.

**Request**:
```http
GET /ai/health
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "ai_service": "available",
  "analysis_queue": 0,
  "last_analysis": "2026-01-14T15:30:00Z",
  "version": "4.0.0"
}
```

#### GET /ai/rate-limit
**Description**: Get current rate limit status for the user.

**Request**:
```http
GET /ai/rate-limit
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "analysis": {
    "limit": 50,
    "remaining": 45,
    "reset_time": "2026-01-14T16:30:00Z"
  },
  "actions": {
    "limit": 20,
    "remaining": 18,
    "reset_time": "2026-01-14T16:30:00Z"
  },
  "notifications": {
    "limit": 100,
    "remaining": 95,
    "reset_time": "2026-01-14T16:30:00Z"
  }
}
```

## Error Response Format

All error responses follow a standardized format:

```json
{
  "detail": "Error description or array of validation errors"
}
```

### Common Error Codes

| Status Code | Description | Example |
|------------|-------------|---------|
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | User lacks required permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource state conflict |
| `422` | Unprocessable Entity | Validation errors |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | AI service temporarily down |

### Error Response Examples

**400 Bad Request**:
```json
{
  "detail": [
    {
      "loc": ["body", "autonomy_level"],
      "msg": "value is not a valid enumeration member; permitted: 'low', 'medium', 'high'",
      "type": "type_error.enum"
    }
  ]
}
```

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

**429 Too Many Requests**:
```json
{
  "detail": "Rate limit exceeded. Try again in 600 seconds.",
  "retry_after": 600
}
```

## Webhook Events

### Autonomous Action Events
The system can send webhook events for important autonomous actions:

**Event Schema**:
```json
{
  "event_id": "event_123",
  "event_type": "autonomous_action_completed",
  "timestamp": "2026-01-14T15:45:00Z",
  "user_id": "user_abc123",
  "data": {
    "action_id": 123,
    "action_type": "reminder",
    "status": "executed",
    "result": {
      "reminder_set": true
    }
  }
}
```

**Available Event Types**:
- `autonomous_action_suggested`
- `autonomous_action_approved`
- `autonomous_action_rejected`
- `autonomous_action_executed`
- `autonomy_settings_changed`

## Client SDK Integration

### TypeScript Client Example

```typescript
// AI Analysis Service
interface AIClient {
  getAutonomySettings(): Promise<AutonomySettings>;
  updateAutonomySettings(settings: UpdateAutonomySettings): Promise<AutonomySettings>;
  analyzeTasks(request: AnalyzeRequest): Promise<AnalyzeResponse>;
  getActions(params?: ActionParams): Promise<ActionsResponse>;
  approveAction(actionId: number, reason?: string): Promise<ActionResult>;
  rejectAction(actionId: number, reason: string, feedback?: string): Promise<ActionResult>;
  getActivity(params?: ActivityParams): Promise<ActivityResponse>;
  dismissNotification(notificationId: string): Promise<DismissResult>;
}
```

### Error Handling Patterns

```typescript
try {
  const result = await aiClient.analyzeTasks(request);
  // Handle success
} catch (error) {
  if (error.response?.status === 429) {
    // Handle rate limiting
    const retryAfter = error.response.headers['retry-after'];
    setTimeout(() => retry(), retryAfter * 1000);
  } else if (error.response?.status === 401) {
    // Handle authentication
    redirectToLogin();
  } else {
    // Handle other errors
    showErrorMessage(error.response?.data?.detail);
  }
}
```

## Security Considerations

### Input Validation
- All inputs validated against schemas
- SQL injection protection via ORM
- XSS protection for user-generated content
- Rate limiting on all endpoints

### Authentication & Authorization
- JWT token validation on all protected endpoints
- User isolation - users can only access their own data
- Role-based access for administrative functions

### Data Protection
- Sensitive data encrypted in transit (HTTPS required)
- Audit logging for all autonomous actions
- Data retention policies for compliance

## Monitoring & Observability

### Metrics
- API response times
- Error rates by endpoint
- Rate limit usage
- AI service availability
- Autonomous action success rates

### Logging
- Request/response logging for debugging
- Audit trails for autonomous actions
- Performance metrics for optimization
- Error tracking and alerting

### Health Checks
- AI service availability
- Database connectivity
- Rate limiting status
- Background job health