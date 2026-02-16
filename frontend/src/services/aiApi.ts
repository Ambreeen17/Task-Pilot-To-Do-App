// Phase 3: AI-Assisted Todo - AI API Wrappers

import { apiFetch } from "../lib/api";
import {
  ParseResponse,
  ConfirmIntentRequest,
  ConfirmIntentResponse,
  RejectIntentRequest,
  RateLimitStatus,
  Conversation,
  Message,
  SendMessageRequest,
  StartConversationRequest,
} from "../types/ai";

/**
 * Parse natural language text into structured task intent.
 *
 * @param token User's JWT token
 * @param text Natural language task description
 * @param timezone User's timezone (default: UTC)
 * @returns Parsed intent with confidence scores and recommendation
 */
export async function parseNaturalLanguage(
  token: string,
  text: string,
  timezone: string = "UTC"
): Promise<ParseResponse> {
  return await apiFetch("/ai/parse", {
    method: "POST",
    token,
    body: { text, timezone },
  });
}

/**
 * Confirm parsed intent and create task.
 *
 * @param token User's JWT token
 * @param payload Confirmation payload with edited fields
 * @returns Created task details
 */
export async function confirmParsedIntent(
  token: string,
  payload: ConfirmIntentRequest
): Promise<ConfirmIntentResponse> {
  return await apiFetch("/ai/parse/confirm", {
    method: "POST",
    token,
    body: payload,
  });
}

/**
 * Reject parsed intent.
 *
 * @param token User's JWT token
 * @param payload Rejection payload with optional reason
 * @returns Confirmation message
 */
export async function rejectParsedIntent(
  token: string,
  payload: RejectIntentRequest
): Promise<{ message: string; intent_id: number }> {
  return await apiFetch("/ai/parse/reject", {
    method: "POST",
    token,
    body: payload,
  });
}

/**
 * Get rate limit status for current user.
 *
 * @param token User's JWT token
 * @returns Rate limit status
 */
export async function getRateLimitStatus(token: string): Promise<RateLimitStatus> {
  return await apiFetch("/ai/rate-limit", {
    token,
  });
}

// ==================== Chat / Conversation API ====================

/**
 * Start a new AI conversation session.
 *
 * @param token User's JWT token
 * @param payload Optional topic for the conversation
 * @returns Created conversation details
 */
export async function startConversation(
  token: string,
  payload: StartConversationRequest = {}
): Promise<Conversation> {
  return await apiFetch("/ai/conversations", {
    method: "POST",
    token,
    body: payload,
  });
}

/**
 * List user's conversation history.
 *
 * @param token User's JWT token
 * @param limit Max records to return (default: 20)
 * @param offset Pagination offset (default: 0)
 * @returns List of conversations
 */
export async function listConversations(
  token: string,
  limit: number = 20,
  offset: number = 0
): Promise<Conversation[]> {
  return await apiFetch(`/ai/conversations?limit=${limit}&offset=${offset}`, {
    token,
  });
}

/**
 * Get details of a specific conversation with its messages.
 *
 * @param token User's JWT token
 * @param conversationId Conversation ID
 * @returns Conversation with messages
 */
export async function getConversation(
  token: string,
  conversationId: number
): Promise<Conversation & { messages?: Message[] }> {
  return await apiFetch(`/ai/conversations/${conversationId}`, {
    token,
  });
}

/**
 * Send a message to the AI assistant.
 *
 * @param token User's JWT token
 * @param conversationId Conversation ID
 * @param payload Message content
 * @returns AI response message
 */
export async function sendMessage(
  token: string,
  conversationId: number,
  payload: SendMessageRequest
): Promise<Message> {
  return await apiFetch(`/ai/conversations/${conversationId}/messages`, {
    method: "POST",
    token,
    body: payload,
  });
}

/**
 * Close an active conversation.
 *
 * @param token User's JWT token
 * @param conversationId Conversation ID
 * @returns Closing confirmation
 */
export async function closeConversation(
  token: string,
  conversationId: number
): Promise<{ message: string }> {
  return await apiFetch(`/ai/conversations/${conversationId}`, {
    method: "DELETE",
    token,
  });
}
