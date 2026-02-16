import React from 'react';
import { useAutonomy } from '../../context/AutonomyContext';

interface Suggestion {
  task_id: string;
  reason: string;
  urgency: 'high' | 'medium' | 'low';
}

const SuggestionPanel: React.FC = () => {
  const { suggestions } = useAutonomy();

  if (suggestions.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 w-80 max-h-96 overflow-y-auto border">
      <h3 className="font-bold mb-3">AI Suggestions</h3>
      {suggestions.map((suggestion, index) => (
        <div key={index} className={`p-3 mb-2 rounded ${suggestion.urgency === 'high' ? 'bg-red-50 border-red-200' : 'bg-blue-50'}`}>
          <p className="text-sm font-medium">{suggestion.reason}</p>
          <div className="flex gap-2 mt-2">
            <button className="text-xs bg-green-500 text-white px-2 py-1 rounded">Accept</button>
            <button className="text-xs bg-gray-500 text-white px-2 py-1 rounded">Dismiss</button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SuggestionPanel;