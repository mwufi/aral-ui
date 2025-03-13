/**
 * API client for communicating with the Aral backend
 */

// Get the API URL from environment variable or use default
export const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Helper function to build API URLs
export function getApiUrl(path: string): string {
  // If we have a custom API URL (like in dev mode), use it
  if (API_URL) {
    return `${API_URL}${path}`;
  }

  // Otherwise, use relative paths
  return path;
}

// API functions
export async function fetchConversations() {
  const response = await fetch(getApiUrl('/api/conversations'));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function sendMessage(conversationId: string, message: string) {
  const response = await fetch(getApiUrl('/api/message'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
} 