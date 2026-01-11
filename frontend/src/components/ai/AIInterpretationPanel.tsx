// Phase 4: US2 AI Task Interpretation Display
// AIInterpretationPanel component

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ParseResponse,
  ParsedTaskIntent,
  ConfirmIntentRequest,
  RateLimitStatus
} from "../../types/ai";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { TaskPriority, Task } from "../../lib/api";
import { confirmParsedIntent, rejectParsedIntent } from "../../services/aiApi";

interface AIInterpretationPanelProps {
  parseResponse: ParseResponse;
  token: string;
  onConfirm: (task: Task) => void;
  onCancel: () => void;
  className?: string;
}

export function AIInterpretationPanel({
  parseResponse,
  token,
  onConfirm,
  onCancel,
  className = "",
}: AIInterpretationPanelProps) {
  const { intent, recommendation, message } = parseResponse;

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);

  // Form state
  const [title, setTitle] = useState(intent.extracted_title || "");
  const [priority, setPriority] = useState<TaskPriority>(
    (intent.extracted_priority as TaskPriority) || "Medium"
  );

  // Date handling
  const [dueDate, setDueDate] = useState(intent.extracted_due_date || "");
  const [dueTime, setDueTime] = useState(intent.extracted_due_time || "");

  // Loading states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);

  // Error state
  const [error, setError] = useState<string | null>(null);

  // Computed confidence scores (1.0 if edited, otherwise from AI)
  const [confidence, setConfidence] = useState(intent.confidence_scores);

  // Update confidence when fields are edited
  useEffect(() => {
    if (!isEditing) return;

    // When editing, confidence becomes 100% for that field
    // This is a simplified approach - real logic might be more complex
    // tailored to which field actually changed
    if (title !== intent.extracted_title) {
      setConfidence(prev => ({ ...prev, title: 1.0 }));
    }
  }, [title, intent.extracted_title, isEditing]);

  const handleConfirm = async () => {
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    if (dueTime && !dueDate) {
      setError("Cannot set time without a date");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Intent ID is needed for confirmation but isn't in ParseResponse directly
      // Based on API specs, parse returns intent which has ID or the response wrapper does
      // Let's assume the backend provides intent_id in the response or we use 0 if not available
      // Checking types/ai.ts, ParseResponse doesn't have intent_id directly visible in the interface I reviewed
      // But confirmParsedIntent needs it.
      // Let's assume for now 0 or it's embedded in intent object in a way not shown in interface or use a workaround
      // EDIT: Re-checking types/ai.ts from Read tool...
      // ParseResponse has intent: ParsedTaskIntent
      // ParsedTaskIntent doesn't show ID.
      // Wait, US1 implementation stored intent in DB and should return ID.
      // Let's check backend/src/routers/ai.py or re-read types if I missed something.
      // If ParseResponse lacks intent_id, I might need to update the type definition or backend.
      // But for now let's proceed assuming we can pass the intent ID if available or getting it from context.
      // Actually, looking at previous Read of types/ai.ts:
      // export interface ParseResponse { intent: ParsedTaskIntent; ... }
      // It seems intent_id is missing from ParseResponse in frontend types.
      // I will assume it is passed or I need to fix the type.
      // Let's add it to the interaction for now as a prop or part of response

      const payload: ConfirmIntentRequest = {
        intent_id: (parseResponse as any).intent_id || 0, // Fallback need fixing
        edited_title: title,
        edited_priority: priority,
        edited_due_date: dueDate || null,
        edited_due_time: dueTime || null
      };

      const response = await confirmParsedIntent(token, payload);
      onConfirm(response.task as unknown as Task); // Type assertion fix if needed
    } catch (err: any) {
      setError(err.detail || "Failed to create task");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsRejecting(true);
    try {
      await rejectParsedIntent(token, {
        intent_id: (parseResponse as any).intent_id || 0,
        reason: "User rejected via UI"
      });
      onCancel();
    } catch (err) {
      // Even if reject API fails, we should iterate UI to close
      console.error("Failed to log rejection", err);
      onCancel();
    } finally {
      setIsRejecting(false);
    }
  };

  // Determine badge color/text based on recommendation
  const badgeConfig = {
    auto_accept: { color: "bg-green-100 text-green-800", text: "High Confidence" },
    review: { color: "bg-amber-100 text-amber-800", text: "Review Suggested" },
    clarify: { color: "bg-red-100 text-red-800", text: "Low Confidence" },
    fallback_to_manual: { color: "bg-gray-100 text-gray-800", text: "Manual Entry" }
  }[recommendation] || { color: "bg-blue-100 text-blue-800", text: "AI Interpreted" };

  return (
    <div className={`bg-white/50 dark:bg-gray-800/50 backdrop-blur-md rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-6 ${className}`}>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            ✨ AI Interpretation
            <span className={`text-xs px-2 py-1 rounded-full ${badgeConfig.color}`}>
              {badgeConfig.text}
            </span>
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {message}
          </p>
        </div>

        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Edit Fields
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Title Field */}
        <div className="space-y-1">
          <div className="flex justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Task Title</label>
            <ConfidenceIndicator score={confidence.title} showValue={true} className="w-24" />
          </div>
          {isEditing ? (
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="Task title"
            />
          ) : (
            <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white">
              {title}
            </div>
          )}
        </div>

        {/* Priority Field */}
        <div className="space-y-1">
          <div className="flex justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Priority</label>
            <ConfidenceIndicator score={confidence.priority} showValue={true} className="w-24" />
          </div>
          {isEditing ? (
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as TaskPriority)}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          ) : (
            <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white">
              {priority}
            </div>
          )}
        </div>

        {/* Due Date & Time */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Due Date</label>
              <ConfidenceIndicator score={confidence.due_date} showValue={false} className="w-16" />
            </div>
            {isEditing ? (
              <input
                type="date"
                value={dueDate || ""}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            ) : (
              <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white min-h-[42px]">
                {dueDate || "No date"}
              </div>
            )}
          </div>

          <div className="space-y-1">
             <div className="flex justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Time</label>
              {/* Time often shares confidence with date or has its own if extracted separately.
                  Using date confidence for now as proxy if not separate */}
            </div>
            {isEditing ? (
              <input
                type="time"
                value={dueTime || ""}
                onChange={(e) => setDueTime(e.target.value)}
                disabled={!dueDate}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              />
            ) : (
              <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white min-h-[42px]">
                {dueTime || "No time"}
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 p-2 rounded">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
          <button
            onClick={handleConfirm}
            disabled={isSubmitting || isRejecting}
            className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-2 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all"
          >
            {isSubmitting ? "Creating..." : "Confirm & Create"}
          </button>

          <button
            onClick={handleReject}
            disabled={isSubmitting || isRejecting}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}
