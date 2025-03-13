"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { resetWebSocketConnection, subscribeToUpdates, ToolUpdate } from '@/lib/api';

// Define the context types
type WebSocketContextType = {
  subscribe: (conversationId: string, listener: (update: any) => void) => () => void;
  isConnected: boolean;
};

// Create the context with a default value
const WebSocketContext = createContext<WebSocketContextType>({
  subscribe: () => () => {},
  isConnected: false,
});

// Hook to use the WebSocket context
export const useWebSocket = () => useContext(WebSocketContext);

// Custom hook for listening to updates for a specific conversation
export function useLiveUpdates(conversationId?: string) {
  const { subscribe, isConnected } = useWebSocket();
  const [updates, setUpdates] = useState<Record<string, ToolUpdate[]>>({});
  
  // Callback for receiving updates
  const onUpdate = useCallback((update: ToolUpdate) => {
    if (update.type === 'tool_start' || update.type === 'tool_result') {
      setUpdates(prev => {
        // Group updates by their ID to track start/result pairs
        const updatedMap = { ...prev };
        
        if (!updatedMap[update.id]) {
          updatedMap[update.id] = [];
        }
        
        // Add the update to the list for this ID
        updatedMap[update.id] = [...updatedMap[update.id], update];
        
        return updatedMap;
      });
    }
  }, []);
  
  // Set up subscription when conversation ID changes
  useEffect(() => {
    if (!conversationId) {
      setUpdates({});
      return;
    }
    
    console.log(`Setting up subscription for conversation: ${conversationId}`);
    
    // Clear updates when switching conversations
    setUpdates({});
    
    // Subscribe to updates
    const unsubscribe = subscribe(conversationId, onUpdate);
    
    // Clean up when unmounting or changing conversation
    return () => {
      console.log(`Cleaning up subscription for conversation: ${conversationId}`);
      unsubscribe();
    };
  }, [conversationId, subscribe, onUpdate]);
  
  return { updates, isConnected };
}

// WebSocket Provider Component
export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const listenersRef = useRef<Map<string, Set<(update: any) => void>>>(new Map());
  
  // Function to subscribe to updates for a conversation
  const subscribe = useCallback((conversationId: string, listener: (update: any) => void) => {
    console.log(`WebSocketProvider: Adding listener for ${conversationId}`);
    
    // Initialize the set for this conversation if it doesn't exist
    if (!listenersRef.current.has(conversationId)) {
      listenersRef.current.set(conversationId, new Set());
    }
    
    // Add the listener
    listenersRef.current.get(conversationId)!.add(listener);
    
    // Subscribe to the conversation via the API
    const unsubFromApi = subscribeToUpdates(conversationId, (update) => {
      // Get all listeners for this conversation
      const listeners = listenersRef.current.get(conversationId);
      if (listeners) {
        // Notify all listeners
        listeners.forEach(l => l(update));
      }
    });
    
    // Return a function to unsubscribe
    return () => {
      console.log(`WebSocketProvider: Removing listener for ${conversationId}`);
      const listeners = listenersRef.current.get(conversationId);
      if (listeners) {
        listeners.delete(listener);
        if (listeners.size === 0) {
          listenersRef.current.delete(conversationId);
        }
      }
      unsubFromApi();
    };
  }, []);
  
  // Initialize WebSocket connection on mount
  useEffect(() => {
    // Reset WebSocket connection when the app starts
    resetWebSocketConnection();
    setIsConnected(true);
    
    return () => {
      setIsConnected(false);
    };
  }, []);
  
  // Provide the context to children
  return (
    <WebSocketContext.Provider value={{ subscribe, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
}