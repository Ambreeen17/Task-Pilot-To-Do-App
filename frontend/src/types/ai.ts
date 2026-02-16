// Phase 3: AI-Assisted Todo - AI Types

export interface ConfidenceScores {
  title: number;
  priority: number;
  due_date: number;
}

export interface ParsedTaskIntent {
  original_text: string;
  extracted_title: string | null;
  extracted_priority: string | null;
  extracted_due_date: string | null;
  extracted_due_time: string | null;
  confidence_scores: ConfidenceScores;
}

export type AIRecommendation = 'auto_accept' | 'review' | 'clarify' | 'fallback_to_manual';

export interface ParseResponse {
  intent: ParsedTaskIntent;
  recommendation: AIRecommendation;
  message: string;
  fallback_url?: string | null;
  error?: string;
}

export interface ConfirmIntentRequest {
  intent_id: number;
  edited_title: string;
  edited_priority: string | null;
  edited_due_date: string | null;
  edited_due_time: string | null;
}

export interface ConfirmIntentResponse {
  task: {
    id: string;
    title: string;
    priority: string;
    due_date: string | null;
    status: string;
    created_at: string;
  };
  intent_id: number;
  message: string;
}

export interface RejectIntentRequest {
  intent_id: number;
  reason?: string;
}

export interface RateLimitStatus {
  user_id: string;
  requests_remaining: number;
  requests_per_day: number;
  window_hours: number;
}

// Chat / Conversation Types
export type ConversationStatus = 'active' | 'closed' | 'timeout';

export interface Conversation {
  id: number;
  user_id: string;
  status: ConversationStatus;
  start_time: string;
  last_activity_time: string;
  context_window: number;
  topic: string | null;
}

export type MessageRole = 'user' | 'assistant';

export interface CreatedTaskInfo {
  id: string;
  title: string;
  priority: string;
  completed: boolean;
  due_date: string | null;
  created_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  timestamp: string;
  token_count?: number;
  created_task?: CreatedTaskInfo;
  deleted_task?: { id: string; title: string };
  completed_task?: { id: string; title: string };
}

export interface SendMessageRequest {
  content: string;
  language?: 'en' | 'ur';
}

export interface StartConversationRequest {
  topic?: string;
  language?: 'en' | 'ur';
}
