# AI Feedback Panel UI Contract

**Component**: AIInterpretationPanel
**Parent**: ChatInterface → MessageBubble (assistant)
**Phase**: 3 — AI-Assisted Todo
**Date**: 2026-01-10

## Overview

Displays AI's interpretation of natural language input, showing extracted task attributes with confidence indicators. Allows user to review, edit, confirm, or reject the parsed intent before task creation.

**Purpose**: Build user trust in AI by showing explainability and allowing corrections (FR-002, FR-003 from spec).

## Component Structure

```tsx
<AIInterpretationPanel>
  <Header>
    <Icon>📝</Icon>
    <Title>Parsed Task</Title>
    <Badge recommendation={recommendation} />
  </Header>

  <FieldList>
    <InterpretationField
      label="Title"
      value={extractedTitle}
      confidence={confidence.title}
      editable={isEditing}
    />
    <InterpretationField
      label="Priority"
      value={extractedPriority || "Not specified"}
      confidence={confidence.priority}
      editable={isEditing}
    />
    <InterpretationField
      label="Due Date"
      value={formatDate(extractedDueDate) || "Not specified"}
      confidence={confidence.due_date}
      editable={isEditing}
    />
    <InterpretationField
      label="Due Time"
      value={formatTime(extractedDueTime) || "Not specified"}
      confidence={confidence.due_date}
      editable={isEditing}
    />
  </FieldList>

  <Actions>
    <Button variant="secondary" onClick={onEdit} disabled={isEditing}>
      <Icon>✏️</Icon> Edit
    </Button>
    <Button variant="success" onClick={onConfirm} disabled={isEditing}>
      <Icon>✓</Icon> Confirm
    </Button>
    <Button variant="danger" onClick={onReject}>
      <Icon>✗</Icon> Reject
    </Button>
  </Actions>

  {isEditing && (
    <EditForm>
      {/* Edit form fields - see Edit Mode section */}
    </EditForm>
  )}
</AIInterpretationPanel>
```

## Visual Design

### Desktop Layout (≥768px)

```
┌───────────────────────────────────────────┐
│ 📝 Parsed Task              [Auto-accept] │ ← Header (40px)
├───────────────────────────────────────────┤
│                                           │
│  Title: Buy groceries           ██████ 95%│ ← Field + confidence bar
│  Priority: Not specified        ░░░░░░  0%│
│  Due Date: Tomorrow (Jan 11)    ██████ 98%│
│  Due Time: Not specified        ░░░░░░  0%│
│                                           │
├───────────────────────────────────────────┤
│  [✏️ Edit]   [✓ Confirm]   [✗ Reject]    │ ← Actions (48px)
└───────────────────────────────────────────┘
```

**Dimensions**:
- Width: 100% of message bubble (max 600px)
- Padding: 16px
- Border: 2px solid amber-500
- Border radius: 12px
- Background: amber-50

### Mobile Layout (320px - 767px)

```
┌──────────────────────────┐
│ 📝 Parsed    [Review]    │ ← Compact header
├──────────────────────────┤
│ Title: Buy groceries 95% │ ← Inline confidence
│ Priority: None        0% │
│ Due: Tomorrow        98% │
│ Time: None            0% │
├──────────────────────────┤
│ [Edit] [✓][✗]           │ ← Compact actions
└──────────────────────────┘
```

**Dimensions**:
- Width: 100% of message bubble
- Padding: 12px
- Compact spacing (8px between fields)

## Component Props

```typescript
interface AIInterpretationPanelProps {
  intent: ParsedTaskIntent;
  recommendation: 'auto_confirm' | 'review_required' | 'clarification_needed';
  onConfirm: (editedIntent: Partial<ParsedTaskIntent>) => Promise<void>;
  onReject: (intentId: number, reason?: string) => Promise<void>;
  onEdit?: (intentId: number) => void;
  isLoading?: boolean;
  className?: string;
}

interface ParsedTaskIntent {
  id: number;
  original_text: string;
  extracted_title: string | null;
  extracted_priority: 'Low' | 'Medium' | 'High' | null;
  extracted_due_date: string | null; // ISO 8601
  extracted_due_time: string | null; // HH:MM
  confidence_scores: {
    title: number;      // 0.0-1.0
    priority: number;   // 0.0-1.0
    due_date: number;   // 0.0-1.0
  };
}
```

## Recommendation Badge

Visual indicator of AI confidence level (from research.md thresholds).

### Auto-Accept (≥0.9 all fields)

```tsx
<Badge variant="success">
  <Icon>✨</Icon>
  <Text>Auto-accept</Text>
</Badge>
```

**Style**:
- Background: green-100
- Border: green-500
- Text: green-900
- Display: "High confidence - ready to create"

### Review Required (0.7-0.89 any field)

```tsx
<Badge variant="warning">
  <Icon>👀</Icon>
  <Text>Review</Text>
</Badge>
```

**Style**:
- Background: amber-100
- Border: amber-500
- Text: amber-900
- Display: "Please review before confirming"

### Clarification Needed (<0.7 any field)

```tsx
<Badge variant="danger">
  <Icon>❓</Icon>
  <Text>Needs review</Text>
</Badge>
```

**Style**:
- Background: red-100
- Border: red-500
- Text: red-900
- Display: "Low confidence - please review carefully"

## Confidence Indicator

Visual representation of AI confidence for each field.

### Component

```tsx
<ConfidenceIndicator score={0.95}>
  <Label>Title</Label>
  <Value>{extractedTitle || "Not specified"}</Value>
  <ProgressBar>
    <Fill width={`${score * 100}%`} color={getConfidenceColor(score)} />
  </ProgressBar>
  <Score>{Math.round(score * 100)}%</Score>
</ConfidenceIndicator>
```

### Color Mapping

```typescript
function getConfidenceColor(score: number): string {
  if (score >= 0.9) return 'green-500';   // High confidence
  if (score >= 0.7) return 'amber-500';   // Medium confidence
  return 'red-500';                       // Low confidence
}
```

### Visual Representation

**High Confidence (≥0.9)**:
```
Title: Buy groceries          ██████████ 95%
                              ↑ green bar
```

**Medium Confidence (0.7-0.89)**:
```
Priority: Medium              ██████░░░░ 75%
                              ↑ amber bar
```

**Low Confidence (<0.7)**:
```
Due Date: Maybe tomorrow?     ████░░░░░░ 55%
                              ↑ red bar
```

### Progress Bar Styles

```css
.confidence-bar {
  height: 4px;
  background: #e5e7eb; /* gray-200 */
  border-radius: 2px;
  overflow: hidden;
  margin: 4px 0;
}

.confidence-fill {
  height: 100%;
  transition: width 0.5s ease-out, background-color 0.3s;
  border-radius: 2px;
}

.confidence-fill.high {
  background: #10b981; /* green-500 */
}

.confidence-fill.medium {
  background: #f59e0b; /* amber-500 */
}

.confidence-fill.low {
  background: #ef4444; /* red-500 */
}
```

## Edit Mode

When user clicks [Edit], panel expands to show editable form.

### Edit Form Layout

```
┌───────────────────────────────────────────┐
│ 📝 Edit Task Details                      │
├───────────────────────────────────────────┤
│                                           │
│  Title *                                  │
│  ┌─────────────────────────────────────┐ │
│  │ Buy groceries                       │ │
│  └─────────────────────────────────────┘ │
│  0/200                                    │
│                                           │
│  Priority                                 │
│  ┌─────────────────────────────────────┐ │
│  │ [None ▼]                            │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  Due Date                                 │
│  ┌─────────────────────────────────────┐ │
│  │ 📅 01/11/2026                       │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  Due Time                                 │
│  ┌─────────────────────────────────────┐ │
│  │ 🕐 --:-- (Not set)                  │ │
│  └─────────────────────────────────────┘ │
│                                           │
├───────────────────────────────────────────┤
│  [Cancel]                     [💾 Save]  │
└───────────────────────────────────────────┘
```

### Form Fields

```tsx
<EditForm onSubmit={handleSave}>
  <Field>
    <Label required>Title</Label>
    <Input
      type="text"
      value={editedTitle}
      onChange={e => setEditedTitle(e.target.value)}
      maxLength={200}
      required
      placeholder="Task title"
    />
    <CharCount>{editedTitle.length}/200</CharCount>
  </Field>

  <Field>
    <Label>Priority</Label>
    <Select
      value={editedPriority}
      onChange={e => setEditedPriority(e.target.value)}
      options={[
        { value: null, label: 'None' },
        { value: 'Low', label: 'Low' },
        { value: 'Medium', label: 'Medium' },
        { value: 'High', label: 'High' }
      ]}
    />
  </Field>

  <Field>
    <Label>Due Date</Label>
    <DatePicker
      value={editedDueDate}
      onChange={setEditedDueDate}
      minDate={new Date()}
      placeholder="Select date"
    />
  </Field>

  <Field>
    <Label>Due Time</Label>
    <TimePicker
      value={editedDueTime}
      onChange={setEditedDueTime}
      format="24h"
      placeholder="Select time"
    />
  </Field>

  <Actions>
    <Button type="button" variant="secondary" onClick={onCancel}>
      Cancel
    </Button>
    <Button type="submit" variant="primary" disabled={!editedTitle.trim()}>
      💾 Save
    </Button>
  </Actions>
</EditForm>
```

### Form Validation

```typescript
interface ValidationRules {
  title: {
    required: true;
    minLength: 1;
    maxLength: 200;
  };
  priority: {
    enum: ['Low', 'Medium', 'High', null];
  };
  due_date: {
    format: 'YYYY-MM-DD';
    minDate: 'today'; // Can't set due date in past
  };
  due_time: {
    format: 'HH:MM';
    require_date: true; // Can't set time without date
  };
}
```

**Validation Messages**:
- Title empty: "Task title is required"
- Title > 200 chars: "Title must be 200 characters or less"
- Time without date: "Please set a due date before adding a time"

### After Edit Save

```
┌───────────────────────────────────────────┐
│ 📝 Parsed Task (Edited)      [Review]    │
├───────────────────────────────────────────┤
│  Title: Buy groceries           ████ 100% │ ← 100% confidence (user-edited)
│  Priority: High                 ████ 100% │
│  Due Date: Tomorrow (Jan 11)    ████ 100% │
│  Due Time: 18:00                ████ 100% │
├───────────────────────────────────────────┤
│  [✏️ Edit Again]   [✓ Confirm]   [✗ Reject] │
└───────────────────────────────────────────┘
```

**Behavior**:
- All edited fields show 100% confidence (user override)
- "(Edited)" badge shown in header
- Can edit again if needed

## Interaction States

### 1. Initial Display (Review Mode)

```tsx
<AIInterpretationPanel
  intent={parsedIntent}
  recommendation="review_required"
  onConfirm={handleConfirm}
  onReject={handleReject}
  onEdit={handleEdit}
/>
```

**State**:
- All fields read-only
- Actions enabled: [Edit], [Confirm], [Reject]
- Confidence bars visible

### 2. Edit Mode

```tsx
<AIInterpretationPanel
  intent={parsedIntent}
  recommendation="review_required"
  isEditing={true}
  onConfirm={handleConfirm}
  onReject={handleReject}
/>
```

**State**:
- Edit form visible
- Actions: [Cancel], [Save]
- Confidence bars hidden
- [Confirm] and [Reject] disabled

### 3. Loading (Confirming)

```tsx
<AIInterpretationPanel
  intent={parsedIntent}
  recommendation="review_required"
  isLoading={true}
  onConfirm={handleConfirm}
  onReject={handleReject}
/>
```

**State**:
- All actions disabled
- Loading spinner on [Confirm] button
- "Creating task..." text

### 4. Confirmed (Success)

```tsx
<SuccessMessage>
  <Icon>✅</Icon>
  <Text>Task created: {taskTitle}</Text>
  <Link to={`/tasks/${taskId}`}>View task →</Link>
</SuccessMessage>
```

**Behavior**:
- AIInterpretationPanel disappears
- Success message appears in same location
- Auto-dismiss after 5 seconds (message stays, panel gone)

### 5. Rejected

```tsx
<RejectedMessage>
  <Icon>❌</Icon>
  <Text>Task not created</Text>
</RejectedMessage>
```

**Behavior**:
- AIInterpretationPanel disappears
- Rejected message appears briefly
- AI responds: "No problem. What would you like to do?"

## Accessibility

### Keyboard Navigation

```
Tab Order (Review Mode):
1. [Edit] button
2. [Confirm] button
3. [Reject] button

Tab Order (Edit Mode):
1. Title input
2. Priority dropdown
3. Due Date picker
4. Due Time picker
5. [Cancel] button
6. [Save] button

Shortcuts:
- Enter: Confirm (if in review mode, not editing)
- Escape: Cancel edit / close modal
- E: Focus edit button
```

### ARIA Labels

```tsx
<div
  role="complementary"
  aria-label="AI Task Interpretation"
  aria-describedby="interpretation-help"
>
  <p id="interpretation-help" className="sr-only">
    Review the AI's interpretation of your task. You can edit any field before confirming.
  </p>

  <div role="group" aria-label="Extracted task details">
    <div role="status" aria-label={`Title confidence: ${titleScore * 100}%`}>
      <span aria-label="Field name">Title:</span>
      <span aria-label="Extracted value">{title}</span>
      <span aria-hidden="true">{titleScore * 100}%</span>
    </div>
    {/* ... other fields */}
  </div>

  <div role="group" aria-label="Actions">
    <button aria-label="Edit task details">Edit</button>
    <button aria-label="Confirm and create task">Confirm</button>
    <button aria-label="Reject interpretation">Reject</button>
  </div>
</div>
```

### Screen Reader Announcements

```typescript
// On panel appear
announceToScreenReader("Task interpretation ready for review");

// On edit
announceToScreenReader("Editing task details");

// On save edit
announceToScreenReader("Task details updated. All fields now 100% confidence.");

// On confirm (loading)
announceToScreenReader("Creating task...");

// On confirm (success)
announceToScreenReader(`Task created: ${taskTitle}`);

// On reject
announceToScreenReader("Task not created");
```

## Error Handling

### Confirm Failed

```tsx
<ErrorMessage severity="error">
  <Icon>⚠️</Icon>
  <Text>Failed to create task. Please try again.</Text>
  <Actions>
    <Button onClick={retryConfirm}>Retry</Button>
    <Button variant="link" onClick={editManually}>Edit Manually</Button>
  </Actions>
</ErrorMessage>
```

### Edit Save Failed (Validation)

```tsx
<ValidationError>
  <Icon>❗</Icon>
  <Text>Please fix the following errors:</Text>
  <List>
    <Item>• Title is required</Item>
    <Item>• Title must be 200 characters or less</Item>
  </List>
</ValidationError>
```

## Performance

**Requirements**:
- Render time: <50ms (initial)
- Edit form open: <100ms
- Confidence bar animation: 500ms (smooth)
- No layout shift on edit mode toggle

**Optimizations**:
- Memoize confidence color calculation
- Debounce edit form character count updates
- Use CSS transforms for animations (GPU-accelerated)

## Testing

### Unit Tests

```typescript
describe('AIInterpretationPanel', () => {
  it('displays all extracted fields', () => {
    render(<AIInterpretationPanel intent={mockIntent} ... />);
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
  });

  it('shows correct confidence colors', () => {
    const { container } = render(<AIInterpretationPanel intent={mockIntent} ... />);
    const highConfidenceBar = container.querySelector('.confidence-fill.high');
    expect(highConfidenceBar).toHaveStyle({ width: '95%' });
  });

  it('enables edit mode on edit click', async () => {
    render(<AIInterpretationPanel intent={mockIntent} ... />);
    await userEvent.click(screen.getByText('Edit'));
    expect(screen.getByLabelText('Title')).toBeInTheDocument();
  });

  it('calls onConfirm with edited values', async () => {
    const onConfirm = jest.fn();
    render(<AIInterpretationPanel intent={mockIntent} onConfirm={onConfirm} ... />);

    await userEvent.click(screen.getByText('Edit'));
    await userEvent.clear(screen.getByLabelText('Title'));
    await userEvent.type(screen.getByLabelText('Title'), 'New title');
    await userEvent.click(screen.getByText('Save'));
    await userEvent.click(screen.getByText('Confirm'));

    expect(onConfirm).toHaveBeenCalledWith({
      extracted_title: 'New title',
      // ... other fields
    });
  });
});
```

### Integration Tests

```typescript
describe('AIInterpretationPanel Integration', () => {
  it('confirms intent and creates task', async () => {
    const { user } = renderWithProviders(<ChatInterface />);

    // Send message
    await user.type(screen.getByPlaceholderText('Type your message'), 'Buy groceries tomorrow');
    await user.click(screen.getByText('Send'));

    // Wait for AI response with interpretation
    await waitFor(() => {
      expect(screen.getByText('Parsed Task')).toBeInTheDocument();
    });

    // Confirm
    await user.click(screen.getByText('Confirm'));

    // Verify task created
    await waitFor(() => {
      expect(screen.getByText('Task created: Buy groceries')).toBeInTheDocument();
    });
  });

  it('rejects intent and continues conversation', async () => {
    // ... similar test for rejection
  });
});
```

## Related Components

- **ConfidenceIndicator**: Visual confidence score (progress bar + percentage)
- **InterpretationField**: Single field display with label, value, confidence
- **EditIntentForm**: Form for editing extracted task details
- **RecommendationBadge**: Visual indicator of AI confidence level

See: `chat-interface.md` for parent component details
