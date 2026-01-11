// Phase 3: AI-Assisted Todo - AI API Wrappers

import { apiFetch } from "../lib/api";
import {
  ParseResponse,
  ConfirmIntentRequest,
  ConfirmIntentResponse,
  RejectIntentRequest,
  RateLimitStatus,
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
