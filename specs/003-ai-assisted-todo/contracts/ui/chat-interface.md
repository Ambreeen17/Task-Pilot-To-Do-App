# Chat Interface UI Contract

**Component**: ChatInterface
**Route**: `/chat`
**Phase**: 3 — AI-Assisted Todo
**Date**: 2026-01-10

## Overview

Primary conversational interface for AI-assisted task management. Provides multi-turn dialogue, task creation via natural language, and context-aware responses.

## Component Hierarchy

```
ChatInterface (page)
├── ChatHeader
│   ├── ConversationStatus (active/timeout indicator)
│   └── ContextControls (clear context, close conversation)
├── MessageList (scrollable)
│   ├── MessageBubble (user) × N
│   ├── MessageBubble (assistant) × N
│   └── AIInterpretationPanel (when parsing detected)
│       ├── ConfidenceIndicator × 3 (title, priority, date)
│       └── InterpretationActions (edit, confirm, reject)
└── MessageInput
    ├── TextArea (auto-expand, max 10k chars)
    ├── CharacterCount
    └── SendButton (disabled when empty or over limit)
```

## Layout Specifications

### Desktop (≥1024px)

```
┌────────────────────────────────────────────┐
│  Chat Header         [Context] [Close]     │ ← 64px height
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ User: Buy groceries tomorrow         │ │ ← User bubble (right-aligned)
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Assistant: I'll help you create...   │ │ ← AI bubble (left-aligned)
│  │                                      │ │
│  │ ┌────────────────────────────────┐   │ │
│  │ │ 📝 Parsed Task                 │   │ │ ← AIInterpretationPanel
│  │ │ Title: Buy groceries (95%)     │   │ │
│  │ │ Priority: None (0%)            │   │ │
│  │ │ Due: Tomorrow (98%)            │   │ │
│  │ │ [Edit] [✓ Confirm] [✗ Reject] │   │ │
│  │ └────────────────────────────────┘   │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ... more messages (scrollable) ...       │
│                                            │
├────────────────────────────────────────────┤
│  ┌────────────────────────────────────┐   │ ← MessageInput
│  │ Type your message...               │   │   min: 80px
│  │                                    │   │   max: 200px
│  └────────────────────────────────────┘   │
│  0/10,000                        [Send →]  │ ← 48px height
└────────────────────────────────────────────┘
```

**Dimensions**:
- Max width: 800px (centered)
- Message list: calc(100vh - 64px - 48px - input height)
- Padding: 16px (messages), 24px (outer container)

### Mobile (320px - 767px)

```
┌────────────────────┐
│ Chat    [Clear][x] │ ← 56px header
├────────────────────┤
│                    │
│  ┌──────────────┐  │ ← User bubble
│  │ Buy groceries│  │   (full width - 32px)
│  └──────────────┘  │
│                    │
│┌────────────────┐  │ ← AI bubble
││ I'll help...   │  │
││                │  │
││ 📝 Parsed Task │  │
││ Title: Buy...  │  │
││ Due: Tomorrow  │  │
││ [Edit][✓][✗]  │  │
│└────────────────┘  │
│                    │
│  ... messages ...  │
│                    │
├────────────────────┤
│ Type message...    │ ← Input (auto-expand)
│ 0/10k       [Send] │
└────────────────────┘
```

**Dimensions**:
- Full viewport width
- Message bubbles: max 80% width
- Padding: 12px
- Input: min 64px, max 120px height

## State Management

### Component State (useChat hook)

```typescript
interface ChatState {
  conversation: Conversation | null;
  messages: Message[];
  pendingIntents: ParsedTaskIntent[];
  isLoading: boolean;
  error: string | null;
  rateLimitStatus: RateLimitStatus;
}

interface Conversation {
  id: number;
  status: 'active' | 'closed' | 'timeout';
  start_time: string;
  last_activity_time: string;
  context_window: number;
  topic: string | null;
}

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  parsed_intent?: ParsedTaskIntent;
}

interface ParsedTaskIntent {
  id: number;
  original_text: string;
  extracted_title: string | null;
  extracted_priority: 'Low' | 'Medium' | 'High' | null;
  extracted_due_date: string | null;
  extracted_due_time: string | null;
  confidence_scores: {
    title: number;
    priority: number;
    due_date: number;
  };
}

interface RateLimitStatus {
  requests_remaining: number;
  requests_max: number;
  reset_time: string;
}
```

### Actions (useChat hook)

```typescript
const {
  // State
  conversation,
  messages,
  pendingIntents,
  isLoading,
  error,
  rateLimitStatus,

  // Actions
  sendMessage: (content: string) => Promise<void>,
  confirmIntent: (intentId: number, editedFields: Partial<ParsedTaskIntent>) => Promise<void>,
  rejectIntent: (intentId: number, reason?: string) => Promise<void>,
  clearContext: () => Promise<void>,
  closeConversation: () => Promise<void>,

  // Utilities
  getMessagesByRole: (role: 'user' | 'assistant') => Message[],
  hasActiveConversation: () => boolean,
} = useChat();
```

## Interaction Patterns

### 1. Send Message

**User Flow**:
1. User types in MessageInput textarea
2. Character count updates live (0/10,000)
3. User clicks Send or presses Enter (Shift+Enter for newline)
4. Message sent to API
5. User bubble appears immediately (optimistic)
6. Loading indicator shown
7. AI response appears (typewriter effect optional)

**API Call**:
```typescript
POST /chat/conversations/{conversation_id}/messages
Body: { content: string }
Response: {
  user_message: Message,
  assistant_message: Message,
  parsed_intent?: ParsedTaskIntent,
  context_updated: boolean
}
```

**Loading State**:
- Send button disabled
- Pulsing indicator in assistant bubble area
- User can't send new messages until response received

**Error Handling**:
- Rate limit (429): Show "Daily limit reached" with reset time, link to manual task creation
- AI unavailable (503): Show "AI offline, use manual entry" with fallback link
- Network error: Show retry button

### 2. Confirm Parsed Intent

**User Flow**:
1. AI response includes AIInterpretationPanel
2. User reviews extracted fields with confidence indicators
3. User optionally clicks [Edit] to modify fields
4. User clicks [✓ Confirm]
5. Task created via API
6. Success message shown
7. Intent panel disappears, replaced with "Task created" message

**API Call**:
```typescript
POST /ai/parse/confirm
Body: {
  intent_id: number,
  edited_title: string,
  edited_priority: string | null,
  edited_due_date: string | null,
  edited_due_time: string | null
}
Response: {
  task: Task,
  intent_id: number,
  message: string
}
```

**Success Feedback**:
- Green checkmark animation
- "Task created: {title}" message
- Link to view task details

### 3. Edit Parsed Intent

**User Flow**:
1. User clicks [Edit] in AIInterpretationPanel
2. Panel expands to show editable form fields
3. User modifies title, priority, due date, due time
4. User clicks [Save] or [Cancel]
5. If Save: Updated fields shown with 100% confidence
6. User can then confirm

**Form Fields**:
```tsx
<EditIntentForm>
  <Input label="Title" value={title} onChange={...} maxLength={200} required />
  <Select label="Priority" value={priority} options={['Low', 'Medium', 'High']} />
  <DatePicker label="Due Date" value={dueDate} />
  <TimePicker label="Due Time" value={dueTime} />
  <Actions>
    <Button variant="secondary" onClick={onCancel}>Cancel</Button>
    <Button variant="primary" onClick={onSave}>Save</Button>
  </Actions>
</EditIntentForm>
```

### 4. Reject Parsed Intent

**User Flow**:
1. User clicks [✗ Reject] in AIInterpretationPanel
2. Optional modal: "Why reject? (helps improve AI)"
3. User optionally provides feedback
4. Intent marked as rejected
5. Panel disappears
6. AI responds: "No problem. What would you like to do?"

**API Call**:
```typescript
POST /ai/parse/reject
Body: {
  intent_id: number,
  reason?: string
}
Response: { message: string }
```

### 5. Clear Context

**User Flow**:
1. User clicks [Clear] in ChatHeader
2. Confirmation modal: "Clear conversation context? (resets AI memory)"
3. User confirms
4. Context cleared via API
5. Conversation continues but AI "forgets" previous messages
6. Visual indicator: "Context reset" message in chat

**API Call**:
```typescript
DELETE /chat/context
Response: { message: "Context cleared" }
```

### 6. Close Conversation

**User Flow**:
1. User clicks [Close] in ChatHeader
2. Confirmation modal: "Close conversation? (can reopen later)"
3. User confirms
4. Conversation status → 'closed'
5. Redirect to /tasks or show new conversation option

**API Call**:
```typescript
DELETE /chat/conversations/{conversation_id}
Response: { message: "Conversation closed" }
```

## Visual Design

### Color Palette

```css
/* Message Bubbles */
--user-bubble-bg: #3b82f6;        /* Blue 500 */
--user-bubble-text: #ffffff;
--assistant-bubble-bg: #f3f4f6;   /* Gray 100 */
--assistant-bubble-text: #111827; /* Gray 900 */

/* Interpretation Panel */
--interpretation-bg: #fef3c7;     /* Amber 100 (warm, informative) */
--interpretation-border: #f59e0b; /* Amber 500 */
--interpretation-text: #78350f;   /* Amber 900 */

/* Confidence Indicators */
--confidence-high: #10b981;       /* Green 500 (≥0.9) */
--confidence-medium: #f59e0b;     /* Amber 500 (0.7-0.89) */
--confidence-low: #ef4444;        /* Red 500 (<0.7) */

/* Actions */
--confirm-btn: #10b981;           /* Green 500 */
--reject-btn: #ef4444;            /* Red 500 */
--edit-btn: #6366f1;              /* Indigo 500 */
```

### Typography

```css
/* Message Content */
.message-content {
  font-size: 15px;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Interpretation Panel */
.interpretation-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--interpretation-text);
}

.interpretation-field {
  font-size: 13px;
  line-height: 1.4;
}

/* Confidence Score */
.confidence-score {
  font-size: 12px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
```

### Spacing

```css
/* Message Bubbles */
.message-bubble {
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 16px;
  max-width: 80%;
}

/* Interpretation Panel */
.interpretation-panel {
  padding: 16px;
  margin-top: 8px;
  border-radius: 12px;
  border: 2px solid var(--interpretation-border);
}

/* Input Area */
.message-input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #3b82f6;
  outline: none;
}
```

### Animations

```css
/* Message Appearance */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble {
  animation: slideIn 0.2s ease-out;
}

/* Loading Indicator */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-indicator {
  animation: pulse 1.5s ease-in-out infinite;
}

/* Confidence Indicator */
@keyframes fillBar {
  from { width: 0; }
  to { width: var(--confidence-value); }
}

.confidence-bar {
  animation: fillBar 0.5s ease-out;
}
```

## Accessibility

### Keyboard Navigation

```
Tab Order:
1. Message input textarea
2. Send button
3. Messages (scrollable area, Tab to focus)
4. Interpretation panel actions (Edit, Confirm, Reject)
5. Header controls (Clear, Close)

Shortcuts:
- Enter: Send message (if input focused)
- Shift+Enter: New line in input
- Escape: Close modals/cancel edits
- Ctrl+K: Clear context (with confirmation)
```

### ARIA Labels

```tsx
<div role="log" aria-label="Chat messages" aria-live="polite">
  {messages.map(msg => (
    <div role="article" aria-label={`Message from ${msg.role}`}>
      {msg.content}
    </div>
  ))}
</div>

<textarea
  aria-label="Type your message"
  aria-describedby="char-count"
  aria-invalid={charCount > 10000}
/>

<div role="status" aria-live="polite">
  {isLoading && "AI is typing..."}
</div>

<div role="complementary" aria-label="Task interpretation">
  <span aria-label={`Title confidence: ${score * 100}%`}>
    Title: {title} ({score * 100}%)
  </span>
</div>
```

### Screen Reader Support

- Announce new messages: `aria-live="polite"` on message list
- Announce loading state: "AI is typing..."
- Announce intent parsed: "Task interpretation ready for review"
- Announce actions: "Task created", "Intent rejected", "Context cleared"

## Error States

### 1. Rate Limit Exceeded

```tsx
<ErrorBanner severity="warning">
  <Icon>⏳</Icon>
  <Message>
    You've reached your daily limit of 100 AI requests.
    Resets at {formatTime(resetTime)}.
  </Message>
  <Action>
    <Link to="/tasks/create">Use Manual Entry</Link>
  </Action>
</ErrorBanner>
```

### 2. AI Service Unavailable

```tsx
<ErrorBanner severity="error">
  <Icon>⚠️</Icon>
  <Message>
    AI service is temporarily unavailable.
  </Message>
  <Action>
    <Button onClick={retry}>Retry</Button>
    <Link to="/tasks/create">Manual Entry</Link>
  </Action>
</ErrorBanner>
```

### 3. Conversation Timeout

```tsx
<InfoBanner>
  <Icon>💤</Icon>
  <Message>
    Your conversation timed out after 10 minutes of inactivity.
    Previous messages are saved.
  </Message>
  <Action>
    <Button onClick={startNewConversation}>Start New Conversation</Button>
  </Action>
</InfoBanner>
```

### 4. Network Error

```tsx
<ErrorBanner severity="error">
  <Icon>🔌</Icon>
  <Message>
    Connection lost. Check your internet connection.
  </Message>
  <Action>
    <Button onClick={retry}>Retry</Button>
  </Action>
</ErrorBanner>
```

## Performance Requirements

- **Initial Load**: <1s (conversation history)
- **Message Send**: <3s (AI response, 95th percentile)
- **Scroll Performance**: 60 FPS (even with 100+ messages)
- **Memory**: <50 MB (100 messages in viewport)

**Optimization Strategies**:
- Virtual scrolling for long conversation histories (>50 messages)
- Lazy load images/attachments (Phase 4)
- Debounce character count updates (200ms)
- Request cancellation on unmount

## Testing Checklist

### Unit Tests
- [ ] Message rendering (user/assistant bubbles)
- [ ] Character count updates correctly
- [ ] Send button disabled when input empty or over limit
- [ ] Confidence indicators display correct color based on score
- [ ] Edit intent form validation

### Integration Tests
- [ ] Send message → receive AI response
- [ ] Parse intent → confirm → task created
- [ ] Parse intent → edit → confirm
- [ ] Parse intent → reject → no task created
- [ ] Rate limit exceeded → show error banner
- [ ] AI unavailable → show fallback

### E2E Tests (Playwright)
- [ ] Complete conversation flow (5 messages)
- [ ] Create task via NL → appears in task list
- [ ] Edit parsed intent before confirm
- [ ] Clear context → AI forgets previous messages
- [ ] Close conversation → redirect to tasks
- [ ] Mobile responsive (320px - 768px)

### Accessibility Tests
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces new messages
- [ ] ARIA labels present on interactive elements
- [ ] Color contrast ≥4.5:1 (WCAG AA)
- [ ] Focus indicators visible

## Related Components

- **MessageBubble**: Individual message display
- **AIInterpretationPanel**: Parsed task preview
- **ConfidenceIndicator**: Visual confidence score
- **MessageInput**: Text input with character count
- **ChatHeader**: Conversation controls

See: `ai-feedback-panel.md` for AIInterpretationPanel details
