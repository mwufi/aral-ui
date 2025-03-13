"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { resetWebSocketConnection, subscribeToUpdates, ToolUpdate } from '@/lib/api';

// Define the context types
type WebSocketContextType = {
  subscribe: (conversationId: string, listener: (update: any) => void) => () => void;
  isConnected: boolean;
  setInitialUpdates?: (updates: Record<string, any[]>) => void;
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
  
  // Function to set initial updates loaded from storage
  const setInitialUpdates = useCallback((initialUpdates: Record<string, any[]>) => {
    console.log('Setting initial updates from storage:', initialUpdates);
    setUpdates(initialUpdates);
  }, []);
  
  // Callback for receiving updates
  const onUpdate = useCallback((update: ToolUpdate) => {
    // Log all updates we receive
    console.log('Received update in hook:', update);
    
    // Handle all types of updates (tool_start, progress_update, tool_result)
    if (update.id) {
      setUpdates(prev => {
        console.log('Current updates state:', prev);
        
        // Group updates by their ID to track all updates for a tool
        const updatedMap = { ...prev };
        
        if (!updatedMap[update.id]) {
          updatedMap[update.id] = [];
        }
        
        // Check if we already have this update type for this ID
        const existingUpdateIndex = updatedMap[update.id].findIndex(
          u => u.type === update.type && u.id === update.id
        );
        
        // If this update has a tool_use_id, store it for later reference
        if (update.tool_use_id) {
          update.related_tool_use_id = update.tool_use_id;
        }
        
        if (existingUpdateIndex >= 0 && update.type === 'progress_update') {
          // Replace the existing progress update
          const newUpdates = [...updatedMap[update.id]];
          newUpdates[existingUpdateIndex] = update;
          updatedMap[update.id] = newUpdates;
        } else {
          // Add the new update to the list for this ID
          updatedMap[update.id] = [...updatedMap[update.id], update];
        }
        
        console.log('New updates state:', updatedMap);
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
    
    // Note: We don't clear updates here anymore, as we want to keep any initial updates loaded from storage
    // Subscribe to updates for new real-time messages
    const unsubscribe = subscribe(conversationId, onUpdate);
    
    // Clean up when unmounting or changing conversation
    return () => {
      console.log(`Cleaning up subscription for conversation: ${conversationId}`);
      unsubscribe();
    };
  }, [conversationId, subscribe, onUpdate]);
  
  return { updates, isConnected, setInitialUpdates };
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
    
    // Set up debug event listener for testing
    const handleTestToolUpdate = (event: any) => {
      const update = event.detail;
      console.log('Received test tool update via custom event:', update);
      
      // Call all relevant listeners
      if (update && update.conversation_id) {
        const convoListeners = listenersRef.current.get(update.conversation_id);
        if (convoListeners) {
          convoListeners.forEach(listener => listener(update));
        }
      }
    };
    
    // Add event listener
    window.addEventListener('tool_update', handleTestToolUpdate);
    
    return () => {
      setIsConnected(false);
      // Remove event listener
      window.removeEventListener('tool_update', handleTestToolUpdate);
    };
  }, []);
  
  // Provide the context to children - note we don't actually provide setInitialUpdates
  // because it's part of the hook, not the shared context
  return (
    <WebSocketContext.Provider value={{ subscribe, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
}