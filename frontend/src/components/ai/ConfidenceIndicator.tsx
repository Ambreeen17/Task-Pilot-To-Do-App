// Phase 3: AI-Assisted Todo - Confidence Indicator

import React from "react";

interface ConfidenceIndicatorProps {
  score: number; // 0.0 to 1.0
  label?: string;
  showValue?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  score,
  label,
  showValue = true,
  className = "",
}: ConfidenceIndicatorProps) {
  // Determine color based on score
  // >= 0.9: Green (Auto-accept)
  // 0.7 - 0.89: Amber (Review)
  // < 0.7: Red (Low confidence)
  let colorClass = "bg-red-500";
  let textColorClass = "text-red-700";

  if (score >= 0.9) {
    colorClass = "bg-green-500";
    textColorClass = "text-green-700";
  } else if (score >= 0.7) {
    colorClass = "bg-amber-500";
    textColorClass = "text-amber-700";
  }

  // Convert to percentage for display
  const percentage = Math.round(score * 100);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {label && <span className="text-sm text-gray-600 w-20">{label}</span>}

      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClass} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {showValue && (
        <span className={`text-xs font-medium w-8 text-right ${textColorClass}`}>
          {percentage}%
        </span>
      )}
    </div>
  );
}
