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

// Helper function to build WebSocket URLs
export function getWsUrl(path: string): string {
  // If we have a custom API URL (like in dev mode), use it
  if (API_URL) {
    const wsUrl = API_URL.replace(/^http/, 'ws');
    return `${wsUrl}${path}`;
  }

  // Otherwise, use relative paths with the current host
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}${path}`;
}

// WebSocket connection types
export type WebSocketUpdateListener = (update: any) => void;
export type ToolUpdate = {
  id: string;
  type: string;
  conversation_id: string;
  tool?: string;
  args?: any;
  result?: any;
  tool_use_id?: string;    // ID of the original tool_use block
  related_tool_use_id?: string; // For tracking related updates
  related_message_id?: string;  // For relating to specific messages
  [key: string]: any;
};

// WebSocket connection management
let wsConnection: WebSocket | null = null;
const listeners: Map<string, Set<WebSocketUpdateListener>> = new Map();

/**
 * Subscribe to updates for a specific conversation
 * @param conversationId The conversation ID to subscribe to
 * @param listener The callback function that will receive updates
 * @returns A function to unsubscribe
 */
export function subscribeToUpdates(
  conversationId: string,
  listener: WebSocketUpdateListener
): () => void {
  // Initialize the connection if it doesn't exist
  if (!wsConnection) {
    initWebSocket();
  }

  // Register the listener
  if (!listeners.has(conversationId)) {
    listeners.set(conversationId, new Set());
  }
  listeners.get(conversationId)!.add(listener);

  // Return unsubscribe function
  return () => {
    const conversationListeners = listeners.get(conversationId);
    if (conversationListeners) {
      conversationListeners.delete(listener);
      if (conversationListeners.size === 0) {
        listeners.delete(conversationId);
      }
    }
  };
}

/**
 * Reset the WebSocket connection
 * This is useful when changing conversations
 */
export function resetWebSocketConnection() {
  console.log('Resetting WebSocket connection');
  if (wsConnection) {
    // Only reset if we have an active connection
    initWebSocket();
  }
}

/**
 * Initialize the WebSocket connection
 */
function initWebSocket() {
  // Close existing connection if it exists
  if (wsConnection) {
    wsConnection.close();
  }

  // Create a new connection
  wsConnection = new WebSocket(getWsUrl('/ws'));

  // Set up event handlers
  wsConnection.onopen = () => {
    console.log('WebSocket connection established');
    // Subscribe to all active conversations
    const activeConversations = Array.from(listeners.keys()).filter(id => id !== 'global');
    if (activeConversations.length > 0 && wsConnection) {
      console.log(`Subscribing to conversation: ${activeConversations[0]}`);
      // Subscribe to the first conversation in our listeners
      wsConnection.send(JSON.stringify({
        conversation_id: activeConversations[0]
      }));
    }
  };

  wsConnection.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket received:', data);
      
      // Check if this is a conversation-specific update
      if (data.conversation_id) {
        // Notify conversation-specific listeners
        const conversationListeners = listeners.get(data.conversation_id);
        if (conversationListeners) {
          conversationListeners.forEach(listener => listener(data));
        }
        
        // Also notify global listeners (if any)
        const globalListeners = listeners.get('global');
        if (globalListeners) {
          globalListeners.forEach(listener => listener(data));
        }
      } else {
        // Broadcast to all listeners
        listeners.forEach(conversationListeners => {
          conversationListeners.forEach(listener => listener(data));
        });
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  wsConnection.onclose = () => {
    console.log('WebSocket connection closed');
    // Attempt to reconnect after a delay
    setTimeout(() => {
      if (listeners.size > 0) {
        initWebSocket();
      }
    }, 2000);
  };

  wsConnection.onerror = (error) => {
    console.error('WebSocket error:', error);
    wsConnection?.close();
  };
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