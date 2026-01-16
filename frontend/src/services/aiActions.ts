// Accept/Reject handlers for AI suggestions

export const acceptSuggestion = async (suggestionId: string, userToken: string): Promise<boolean> => {
  try {
    const response = await fetch('/api/ai/accept', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${userToken}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_id: suggestionId })
    });
    return response.ok;
  } catch {
    return false;
  }
};

export const rejectSuggestion = async (suggestionId: string, userToken: string): Promise<boolean> => {
  try {
    const response = await fetch('/api/ai/reject', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${userToken}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_id: suggestionId })
    });
    return response.ok;
  } catch {
    return false;
  }
};