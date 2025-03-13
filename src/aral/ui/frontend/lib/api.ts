/**
 * API client for communicating with the Aral backend
 */

// Get the API URL from the environment variable or default to the current origin
const getApiBaseUrl = () => {
  // In the browser, use the environment variable if available
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || '';
  }
  // In server-side rendering, we don't have access to the browser's origin
  return process.env.NEXT_PUBLIC_API_URL || '';
};

export async function sendMessage(conversationId: string, message: string) {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/api/message`, {
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
    throw new Error('Failed to send message');
  }

  return response.json();
}

export async function getConversations() {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/api/conversations`);

  if (!response.ok) {
    throw new Error('Failed to fetch conversations');
  }

  return response.json();
} 