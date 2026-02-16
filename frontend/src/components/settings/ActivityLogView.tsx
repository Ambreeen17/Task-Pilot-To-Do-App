'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

interface ActivityLog {
  action_type: string;
  reasoning: string;
  status: string;
}

const ActivityLogView: React.FC = () => {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;
    fetch('/api/monitor/logs', {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(res => res.json()).then(data => setLogs(data.logs || []));
  }, [token]);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">AI Activity Log</h2>
      <ul className="space-y-2">
        {logs.map((log, i) => (
          <li key={i} className="p-3 bg-gray-50 rounded">
            <span className="font-medium">{log.action_type}</span> - {log.reasoning} ({log.status})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActivityLogView;
