# Research & Decisions - Phase 4

## 1. Client-Side Trigger Technology

**Decision:** Use React `useEffect` with `setInterval` and `Page Visibility API` (via `react-use` or custom hook) in a dedicated top-level Provider (`AutonomyProvider`).

**Rationale:**
- **Simplicity:** No need for Service Workers (which add deployment complexity and caching issues).
- **User Presence:** We only want to notify the user if they are actually using the app. Background processing when the tab is closed is distinct from "Proactive Assistant while working" and likely out of scope for Phase 4 web-only context.
- **Cost:** Zero server load for inactive users.

**Alternatives Considered:**
- Service Workers: Overkill for "while usage" monitoring. Better for PWA push notifications (out of scope for now).
- Backend Cron: Too expensive and complex to manage "connected user" state.

## 2. State Management for Autonomy

**Decision:** Use centralized **Context API** (`AutonomyContext`) to share state between the hidden Orchestrator and visible UI components (Toasts/Panels).

**Rationale:**
- Prevents prop drilling.
- Allows the Evaluation Loop to run independently from the UI rendering.
- UI components (SuggestionPanel) can simply `useAutonomy()` to get current suggestions.

## 3. Storage for Patterns

**Decision:** Store `pattern_detection` in PostgreSQL (backend) rather than LocalStorage.

**Rationale:**
- **Cross-Device:** Start habit on mobile, get suggestions on desktop.
- **Data Safety:** AI logic runs on backend; easier to query DB natively than sync local state up.
- **Persistence:** LocalStorage is ephemeral and insecure for sensitive habit data.
