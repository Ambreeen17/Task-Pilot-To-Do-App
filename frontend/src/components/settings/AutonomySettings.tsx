import React from 'react';
import { useAutonomy } from '../../context/AutonomyContext';

const AutonomySettings: React.FC = () => {
  const { autonomyLevel, updateAutonomyLevel, suggestions } = useAutonomy();

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">AI Autonomy Settings</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Autonomy Level</label>
          <select
            value={autonomyLevel}
            onChange={(e) => updateAutonomyLevel(e.target.value as any)}
            className="w-full p-2 border rounded"
          >
            <option value="low">Low (Suggestions only)</option>
            <option value="medium">Medium (Auto-schedule drafts)</option>
            <option value="high">High (Execute with approval)</option>
          </select>
        </div>
        <div className="text-sm text-gray-600">
          Active suggestions: {suggestions.length}
        </div>
      </div>
    </div>
  );
};

export default AutonomySettings;