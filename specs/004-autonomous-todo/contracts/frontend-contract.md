# Phase 4: Autonomous & Proactive Todo System - Frontend Contracts

**Feature Branch**: `004-autonomous-todo`
**Status**: DRAFT → IMPLEMENTATION
**Specification**: `specs/004-autonomous-todo/spec.md`
**Plan**: `specs/004-autonomous-todo/plan.md`
**Last Updated**: 2026-01-14

## Overview

This document defines the frontend contracts for the autonomous todo agent system. It includes TypeScript interfaces, component contracts, state management patterns, and integration points with the backend API.

## Technology Stack

- **Framework**: Next.js 16.1.1 with React 19
- **State Management**: React Context + Hooks
- **HTTP Client**: Axios with TypeScript
- **Styling**: Tailwind CSS 4
- **TypeScript**: Strict mode with comprehensive type definitions
- **Animation**: Framer Motion 12.24.10

## Core TypeScript Interfaces

### Autonomy Settings Interface

```typescript
// Core autonomy settings interface
export interface AutonomySettings {
  autonomy_level: 'low' | 'medium' | 'high';
  enabled_categories: string[];
  work_hours: {
    start: number; // 0-23
    end: number;   // 0-23
  };
  timezone: string; // IANA timezone format
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

// Update settings interface
export interface UpdateAutonomySettings {
  autonomy_level?: 'low' | 'medium' | 'high';
  enabled_categories?: string[];
  work_hours?: {
    start?: number;
    end?: number;
  };
  timezone?: string;
}
```

### Autonomous Action Interface

```typescript
// Core action interface
export interface AutonomousAction {
  id: number;
  user_id: string;
  action_type: 'reminder' | 'reschedule' | 'create' | 'insight';
  target_task_id?: string;
  suggested_changes: Record<string, any>;
  reason: string;
  confidence: number; // 0.0-1.0
  status: 'pending' | 'approved' | 'rejected' | 'executed';
  created_at: string; // ISO 8601
  executed_at?: string; // ISO 8601
}

// Action summary for lists
export interface AutonomousActionSummary {
  id: number;
  action_type: string;
  message: string;
  confidence: number;
  status: string;
  reason: string;
  created_at: string;
}

// Action result interface
export interface ActionResult {
  action_id: number;
  status: 'executed' | 'rejected';
  result?: Record<string, any>;
  reasoning?: string;
  execution_time?: number; // seconds
}
```

### AI Analysis Interface

```typescript
// Analysis request interface
export interface AnalyzeRequest {
  include_categories: Array<
    'deadline_risk' |
    'pattern_detection' |
    'workload_optimization' |
    'recurring_tasks' |
    'time_optimization'
  >;
  time_period?: {
    start: string; // ISO 8601
    end: string;   // ISO 8601
  };
}

// Analysis response interface
export interface AnalyzeResponse {
  analysis_id: string;
  timestamp: string; // ISO 8601
  suggestions: Suggestion[];
  metrics: Metrics;
  analysis_duration: number; // seconds
}

// Suggestion interface
export interface Suggestion {
  id: string;
  type: string;
  task_id?: string;
  message: string;
  confidence: number; // 0.0-1.0
  actions: string[];
  priority: 'low' | 'medium' | 'high';
  reasoning: string;
  suggested_changes: Record<string, any>;
}

// Metrics interface
export interface Metrics {
  total_tasks: number;
  overdue_tasks: number;
  tasks_due_today: number;
  workload_score: number; // 0.0-1.0
  risk_level: 'low' | 'medium' | 'high';
}
```

### Activity Log Interface

```typescript
// Activity log entry interface
export interface ActivityLogEntry {
  id: number;
  user_id: string;
  action_type: string;
  entity_target: string;
  reasoning: string;
  status: string;
  timestamp: string; // ISO 8601
  result?: Record<string, any>;
}

// Activity log response interface
export interface ActivityResponse {
  activity: ActivityLogEntry[];
  pagination: PaginationInfo;
}

// Pagination interface
export interface PaginationInfo {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
```

### Notification Interface

```typescript
// Notification interface
export interface Notification {
  id: string;
  type: string;
  priority: 'low' | 'medium' | 'high';
  title: string;
  message: string;
  task_id?: string;
  created_at: string; // ISO 8601
  read: boolean;
  dismissed: boolean;
}

// Notifications response interface
export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
}
```

## React Context Contracts

### Autonomy Context

```typescript
// Autonomy context interface
export interface AutonomyContextType {
  // State
  settings: AutonomySettings | null;
  suggestions: Suggestion[];
  actions: AutonomousActionSummary[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchSettings: () => Promise<void>;
  updateSettings: (updates: UpdateAutonomySettings) => Promise<void>;
  analyzeTasks: (request: AnalyzeRequest) => Promise<AnalyzeResponse>;
  approveAction: (actionId: number, reason?: string) => Promise<ActionResult>;
  rejectAction: (actionId: number, reason: string, feedback?: string) => Promise<ActionResult>;
  dismissNotification: (notificationId: string) => Promise<void>;
  getActivityLog: (params?: ActivityParams) => Promise<ActivityResponse>;
}

// Context provider props
export interface AutonomyProviderProps {
  children: React.ReactNode;
  autoInitialize?: boolean; // Whether to auto-fetch settings on mount
  pollingInterval?: number; // Interval for proactive analysis (ms)
}
```

### Task Context Extension

```typescript
// Extended task context with autonomy features
export interface TaskContextType extends OriginalTaskContextType {
  // New autonomy features
  autonomySettings: AutonomySettings | null;
  proactiveSuggestions: Suggestion[];
  pendingActions: AutonomousActionSummary[];

  // Autonomy actions
  enableAutonomy: (settings: UpdateAutonomySettings) => Promise<void>;
  disableAutonomy: () => Promise<void>;
  getSuggestions: () => Promise<Suggestion[]>;
  executeSuggestion: (suggestionId: string) => Promise<ActionResult>;
}
```

## React Hook Contracts

### useAutonomy Hook

```typescript
// useAutonomy hook interface
export interface UseAutonomyReturn {
  // State
  settings: AutonomySettings | null;
  suggestions: Suggestion[];
  actions: AutonomousActionSummary[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchSettings: () => Promise<void>;
  updateSettings: (updates: UpdateAutonomySettings) => Promise<void>;
  analyzeNow: (categories?: string[]) => Promise<AnalyzeResponse>;
  approveAction: (actionId: number, reason?: string) => Promise<ActionResult>;
  rejectAction: (actionId: number, reason: string, feedback?: string) => Promise<ActionResult>;
  dismissNotification: (notificationId: string) => Promise<void>;
  getActivityLog: (params?: ActivityParams) => Promise<ActivityResponse>;

  // Computed state
  isAutonomyEnabled: boolean;
  canApproveActions: boolean;
  hasHighConfidenceSuggestions: boolean;
  nextSuggestionTime: Date | null;
}

// Hook options interface
export interface UseAutonomyOptions {
  autoFetch?: boolean;
  pollInterval?: number; // ms
  enabledCategories?: string[];
  onError?: (error: Error) => void;
}

// Hook implementation
export function useAutonomy(options?: UseAutonomyOptions): UseAutonomyReturn;
```

### useProactiveSuggestions Hook

```typescript
// Proactive suggestions hook interface
export interface UseProactiveSuggestionsReturn {
  suggestions: Suggestion[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  dismiss: (suggestionId: string) => Promise<void>;
}

export function useProactiveSuggestions(): UseProactiveSuggestionsReturn;
```

## Component Contracts

### AutonomySettings Component

```typescript
// Autonomy settings component props
export interface AutonomySettingsProps {
  className?: string;
  onSubmit?: (settings: AutonomySettings) => void;
  onError?: (error: string) => void;
  variant?: 'modal' | 'page' | 'inline';
  showWorkHours?: boolean;
  showCategories?: boolean;
}

// Component interface
export const AutonomySettings: React.FC<AutonomySettingsProps>;
```

### SuggestionPanel Component

```typescript
// Suggestion panel component props
export interface SuggestionPanelProps {
  suggestions: Suggestion[];
  onApprove: (suggestionId: string) => void;
  onReject: (suggestionId: string, reason: string) => void;
  onDismiss: (suggestionId: string) => void;
  isLoading?: boolean;
  className?: string;
  variant?: 'default' | 'compact' | 'modal';
  enableAnimations?: boolean;
}

// Component interface
export const SuggestionPanel: React.FC<SuggestionPanelProps>;
```

### NotificationToast Component

```typescript
// Notification toast component props
export interface NotificationToastProps {
  notification: Notification;
  onDismiss: (notificationId: string) => void;
  onAction?: (notificationId: string, action: string) => void;
  autoHide?: boolean;
  hideDuration?: number; // ms
  className?: string;
}

// Component interface
export const NotificationToast: React.FC<NotificationToastProps>;
```

### ActionApprovalModal Component

```typescript
// Action approval modal component props
export interface ActionApprovalModalProps {
  action: AutonomousAction;
  isOpen: boolean;
  onClose: () => void;
  onApprove: (reason?: string) => void;
  onReject: (reason: string, feedback?: string) => void;
  isLoading?: boolean;
  className?: string;
}

// Component interface
export const ActionApprovalModal: React.FC<ActionApprovalModalProps>;
```

### ActivityDashboard Component

```typescript
// Activity dashboard component props
export interface ActivityDashboardProps {
  filters?: {
    actionType?: string;
    status?: string;
    dateRange?: { start: Date; end: Date };
  };
  onExport?: (format: 'json' | 'csv') => void;
  className?: string;
  pageSize?: number;
}

// Component interface
export const ActivityDashboard: React.FC<ActivityDashboardProps>;
```

## API Service Contracts

### AI Service Interface

```typescript
// AI service interface
export interface AIService {
  // Autonomy settings
  getAutonomySettings(): Promise<AutonomySettings>;
  updateAutonomySettings(settings: UpdateAutonomySettings): Promise<AutonomySettings>;

  // Analysis
  analyzeTasks(request: AnalyzeRequest): Promise<AnalyzeResponse>;
  analyzeTasksQuick(categories: string[]): Promise<AnalyzeResponse>;

  // Actions
  getActions(params?: ActionParams): Promise<ActionsResponse>;
  approveAction(actionId: number, reason?: string): Promise<ActionResult>;
  rejectAction(actionId: number, reason: string, feedback?: string): Promise<ActionResult>;
  executeAction(actionId: number): Promise<ActionResult>;

  // Activity
  getActivity(params?: ActivityParams): Promise<ActivityResponse>;
  exportActivity(format: 'json' | 'csv', params?: ActivityParams): Promise<ExportResult>;

  // Notifications
  getNotifications(params?: NotificationParams): Promise<NotificationsResponse>;
  dismissNotification(notificationId: string): Promise<DismissResult>;

  // Health
  getHealth(): Promise<HealthStatus>;
  getRateLimit(): Promise<RateLimitStatus>;
}

// Service implementation
export const aiService: AIService;
```

### Service Error Handling

```typescript
// Service error types
export class AIServiceError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AIServiceError';
  }
}

// Error handling utility
export function handleServiceError(error: any): AIServiceError {
  if (error.response) {
    return new AIServiceError(
      error.response.data.detail,
      error.response.status,
      error.response.data.code,
      error.response.data
    );
  }
  return new AIServiceError('Network error', 0);
}
```

## State Management Patterns

### Redux/Context State Structure

```typescript
// State interface
export interface AppState {
  // Existing state (from Phase 3)
  tasks: TaskState;
  auth: AuthState;

  // New autonomy state
  autonomy: AutonomyState;
  suggestions: SuggestionsState;
  notifications: NotificationsState;
  activity: ActivityState;
}

// Autonomy state interface
export interface AutonomyState {
  settings: AutonomySettings | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

// Suggestions state interface
export interface SuggestionsState {
  suggestions: Suggestion[];
  isLoading: boolean;
  error: string | null;
  lastFetched: string | null;
}

// Notifications state interface
export interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}

// Activity state interface
export interface ActivityState {
  logs: ActivityLogEntry[];
  pagination: PaginationInfo;
  isLoading: boolean;
  error: string | null;
}
```

### Action Types

```typescript
// Action types enum
export enum AutonomyActionTypes {
  // Settings actions
  FETCH_SETTINGS_REQUEST = 'autonomy/FETCH_SETTINGS_REQUEST',
  FETCH_SETTINGS_SUCCESS = 'autonomy/FETCH_SETTINGS_SUCCESS',
  FETCH_SETTINGS_FAILURE = 'autonomy/FETCH_SETTINGS_FAILURE',

  UPDATE_SETTINGS_REQUEST = 'autonomy/UPDATE_SETTINGS_REQUEST',
  UPDATE_SETTINGS_SUCCESS = 'autonomy/UPDATE_SETTINGS_SUCCESS',
  UPDATE_SETTINGS_FAILURE = 'autonomy/UPDATE_SETTINGS_FAILURE',

  // Suggestion actions
  FETCH_SUGGESTIONS_REQUEST = 'autonomy/FETCH_SUGGESTIONS_REQUEST',
  FETCH_SUGGESTIONS_SUCCESS = 'autonomy/FETCH_SUGGESTIONS_SUCCESS',
  FETCH_SUGGESTIONS_FAILURE = 'autonomy/FETCH_SUGGESTIONS_FAILURE',

  APPROVE_SUGGESTION_REQUEST = 'autonomy/APPROVE_SUGGESTION_REQUEST',
  APPROVE_SUGGESTION_SUCCESS = 'autonomy/APPROVE_SUGGESTION_SUCCESS',
  APPROVE_SUGGESTION_FAILURE = 'autonomy/APPROVE_SUGGESTION_FAILURE',

  REJECT_SUGGESTION_REQUEST = 'autonomy/REJECT_SUGGESTION_REQUEST',
  REJECT_SUGGESTION_SUCCESS = 'autonomy/REJECT_SUGGESTION_SUCCESS',
  REJECT_SUGGESTION_FAILURE = 'autonomy/REJECT_SUGGESTION_FAILURE',

  // Notification actions
  FETCH_NOTIFICATIONS_REQUEST = 'autonomy/FETCH_NOTIFICATIONS_REQUEST',
  FETCH_NOTIFICATIONS_SUCCESS = 'autonomy/FETCH_NOTIFICATIONS_SUCCESS',
  FETCH_NOTIFICATIONS_FAILURE = 'autonomy/FETCH_NOTIFICATIONS_FAILURE',

  DISMISS_NOTIFICATION_REQUEST = 'autonomy/DISMISS_NOTIFICATION_REQUEST',
  DISMISS_NOTIFICATION_SUCCESS = 'autonomy/DISMISS_NOTIFICATION_SUCCESS',
  DISMISS_NOTIFICATION_FAILURE = 'autonomy/DISMISS_NOTIFICATION_FAILURE',
}
```

## Integration Patterns

### Component Integration Example

```typescript
// Tasks page with autonomy integration
export default function TasksPage() {
  const { tasks, isLoading: tasksLoading } = useTasks();
  const {
    suggestions,
    approveAction,
    rejectAction,
    isLoading: autonomyLoading
  } = useAutonomy();

  const handleApproveSuggestion = async (suggestionId: string) => {
    try {
      await approveAction(suggestionId);
      // Show success toast
    } catch (error) {
      // Show error toast
    }
  };

  const handleRejectSuggestion = async (suggestionId: string, reason: string) => {
    try {
      await rejectAction(suggestionId, reason);
      // Show feedback modal
    } catch (error) {
      // Show error toast
    }
  };

  return (
    <div>
      <TaskList tasks={tasks} isLoading={tasksLoading} />
      <SuggestionPanel
        suggestions={suggestions}
        onApprove={handleApproveSuggestion}
        onReject={handleRejectSuggestion}
        isLoading={autonomyLoading}
      />
    </div>
  );
}
```

### Context Provider Integration

```typescript
// App component with autonomy context
export default function App() {
  return (
    <AuthProvider>
      <TaskProvider>
        <AutonomyProvider
          autoInitialize={true}
          pollingInterval={300000} // 5 minutes
        >
          <Router>
            <Routes>
              <Route path="/tasks" element={<TasksPage />} />
              <Route path="/autonomy/settings" element={<AutonomySettingsPage />} />
              <Route path="/activity" element={<ActivityDashboardPage />} />
            </Routes>
          </Router>
        </AutonomyProvider>
      </TaskProvider>
    </AuthProvider>
  );
}
```

## Testing Contracts

### Unit Test Interfaces

```typescript
// Test utility interfaces
export interface MockAutonomySettings {
  autonomy_level: 'low' | 'medium' | 'high';
  enabled_categories: string[];
}

export interface MockSuggestion {
  id: string;
  type: string;
  confidence: number;
  message: string;
}

// Test utilities
export const createMockAutonomySettings = (
  overrides?: Partial<MockAutonomySettings>
): AutonomySettings => ({
  autonomy_level: 'medium',
  enabled_categories: ['reminders'],
  work_hours: { start: 9, end: 17 },
  timezone: 'UTC',
  created_at: '2026-01-14T10:00:00Z',
  updated_at: '2026-01-14T10:00:00Z',
  ...overrides
});

export const createMockSuggestion = (
  overrides?: Partial<MockSuggestion>
): Suggestion => ({
  id: 'suggestion_001',
  type: 'deadline_risk',
  confidence: 0.85,
  message: 'Task is due soon',
  actions: ['reminder'],
  priority: 'medium',
  reasoning: 'Task due date approaching',
  suggested_changes: {},
  ...overrides
});
```

### Component Test Contracts

```typescript
// Component test interface
export interface ComponentTestProps {
  settings?: AutonomySettings;
  suggestions?: Suggestion[];
  actions?: AutonomousActionSummary[];
  isLoading?: boolean;
  error?: string;
}

// Test wrapper component
export const TestWrapper: React.FC<{
  children: React.ReactNode;
  props?: ComponentTestProps;
}>;

// Test utilities
export const renderWithAutonomy = (
  component: React.ReactElement,
  props?: ComponentTestProps
) => {
  return render(
    <TestWrapper props={props}>
      {component}
    </TestWrapper>
  );
};
```

## Performance Considerations

### Memoization Strategy

```typescript
// Memoized hook implementation
export function useAutonomyMemoized(options?: UseAutonomyOptions) {
  const [state, setState] = useState<AutonomyState>(initialState);

  // Memoize expensive calculations
  const computedState = useMemo(() => ({
    isAutonomyEnabled: state.settings?.autonomy_level !== 'low',
    canApproveActions: state.settings?.autonomy_level === 'high',
    hasHighConfidenceSuggestions: state.suggestions.some(s => s.confidence > 0.8),
    nextSuggestionTime: calculateNextSuggestionTime(state.settings, state.lastAnalysis)
  }), [state.settings, state.suggestions, state.lastAnalysis]);

  return { ...state, ...computedState };
}
```

### Lazy Loading Strategy

```typescript
// Lazy loaded components
const LazySuggestionPanel = lazy(() => import('./components/SuggestionPanel'));
const LazyActivityDashboard = lazy(() => import('./components/ActivityDashboard'));

// Dynamic imports for heavy components
const LazyComponents = {
  SuggestionPanel: LazySuggestionPanel,
  ActivityDashboard: LazyActivityDashboard,
  ActionApprovalModal: lazy(() => import('./components/ActionApprovalModal'))
};
```

### Virtualization Strategy

```typescript
// Virtualized suggestion list
export const VirtualizedSuggestionList: React.FC<{
  suggestions: Suggestion[];
  onApprove: (id: string) => void;
  onReject: (id: string, reason: string) => void;
}> = ({ suggestions, onApprove, onReject }) => {
  return (
    <FixedSizeList
      height={400}
      itemCount={suggestions.length}
      itemSize={80}
      itemData={{ suggestions, onApprove, onReject }}
    >
      {SuggestionItem}
    </FixedSizeList>
  );
};
```

## Security Considerations

### Input Validation

```typescript
// Client-side validation utilities
export const validateAutonomySettings = (
  settings: UpdateAutonomySettings
): ValidationResult => {
  const errors: string[] = [];

  if (settings.autonomy_level && !['low', 'medium', 'high'].includes(settings.autonomy_level)) {
    errors.push('Invalid autonomy level');
  }

  if (settings.work_hours?.start !== undefined && settings.work_hours?.end !== undefined) {
    if (settings.work_hours.start >= settings.work_hours.end) {
      errors.push('Start time must be before end time');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};
```

### XSS Protection

```typescript
// Safe rendering utilities
export const safeRenderText = (text: string): React.ReactNode => {
  return text
    .split('\n')
    .map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
};
```

## Accessibility Contracts

### ARIA Attributes

```typescript
// Accessibility utility types
export interface AccessibleComponentProps {
  'aria-label'?: string;
  'aria-describedby'?: string;
  'aria-labelledby'?: string;
  'aria-expanded'?: boolean;
  'aria-hidden'?: boolean;
  role?: string;
}

// Accessible suggestion panel
export const AccessibleSuggestionPanel: React.FC<SuggestionPanelProps & AccessibleComponentProps> = ({
  suggestions,
  'aria-label': ariaLabel = 'Task suggestions',
  ...props
}) => {
  return (
    <div
      role="list"
      aria-label={ariaLabel}
      className="suggestion-panel"
    >
      {suggestions.map((suggestion) => (
        <SuggestionItem
          key={suggestion.id}
          suggestion={suggestion}
          role="listitem"
          aria-label={`Suggestion: ${suggestion.message}`}
          {...props}
        />
      ))}
    </div>
  );
};
```

This comprehensive frontend contract ensures type safety, maintainability, and consistency across the autonomous todo agent implementation while providing clear integration points for developers.