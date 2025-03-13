"use client";

import { useLiveUpdates } from "@/lib/websocket-context";
import { CustomToolRenderer } from "@/components/ui/tool-update";
import { Message } from "@/components/ui/message";
import { useEffect, useMemo } from "react";

interface ToolUpdatesProps {
  conversationId: string;
  messageId?: string; // Message ID to show updates associated with a specific message
  afterTimestamp?: string; // Show updates after a certain timestamp
  beforeTimestamp?: string; // Show updates before a certain timestamp
}

export function ToolUpdates({ 
  conversationId, 
  messageId,
  afterTimestamp,
  beforeTimestamp
}: ToolUpdatesProps) {
  // Use our custom hook to get all updates for this conversation
  const { updates, isConnected } = useLiveUpdates(conversationId);
  
  // Debug log
  console.log('ToolUpdates rendered for conversation:', conversationId);
  console.log('Available updates:', updates);
  
  // Group updates by tool ID for progressive display
  const groupedUpdates = useMemo(() => {
    const result = new Map();
    
    // First pass: group by ID
    Object.values(updates).forEach(updateGroup => {
      // Check if it's for the current conversation
      if (updateGroup.length === 0 || updateGroup[0].conversation_id !== conversationId) {
        return;
      }
      
      // Get the tool ID (should be the same for all updates in the group)
      const toolId = updateGroup[0].id;
      const relatedMessageId = updateGroup[0].related_message_id;
      
      // Filter by messageId if provided
      if (messageId && relatedMessageId && relatedMessageId !== messageId) {
        return;
      }
      
      // Filter by timestamps if provided
      if (afterTimestamp || beforeTimestamp) {
        const timestamp = updateGroup[0].timestamp;
        if (timestamp) {
          if (afterTimestamp && timestamp < afterTimestamp) {
            return;
          }
          if (beforeTimestamp && timestamp > beforeTimestamp) {
            return;
          }
        }
      }
      
      // Group by ID
      if (!result.has(toolId)) {
        result.set(toolId, updateGroup);
      } else {
        // Merge with existing group
        const existing = result.get(toolId);
        result.set(toolId, [...existing, ...updateGroup]);
      }
    });
    
    // Sort updates within each group by timestamp or sequence
    result.forEach((group, id) => {
      group.sort((a, b) => {
        // If we have timestamp, use it
        if (a.timestamp && b.timestamp) {
          return a.timestamp - b.timestamp;
        }
        
        // Otherwise sort by type: tool_start -> progress_update -> tool_result
        const typeOrder = { 
          'tool_start': 0, 
          'progress_update': 1, 
          'tool_result': 2 
        };
        return (typeOrder[a.type] || 0) - (typeOrder[b.type] || 0);
      });
    });
    
    return result;
  }, [updates, conversationId, messageId, afterTimestamp, beforeTimestamp]);
  
  // If there are no updates, don't render anything
  if (groupedUpdates.size === 0) {
    return null;
  }
  
  // Sort tool groups by their first update's timestamp
  // This ensures tools appear in the order they were introduced
  const sortedToolEntries = useMemo(() => {
    return Array.from(groupedUpdates.entries())
      .sort(([, groupA], [, groupB]) => {
        const timestampA = groupA[0]?.timestamp || 0;
        const timestampB = groupB[0]?.timestamp || 0;
        return timestampA - timestampB;
      });
  }, [groupedUpdates]);

  return (
    <>
      {sortedToolEntries.map(([toolId, updateGroup]) => (
        <div key={`tool-${toolId}`} className="flex justify-start mb-4">
          <div className="flex gap-2 max-w-[90%] w-full">
            <Message.Avatar role="assistant" />
            <div className="flex-1">
              <CustomToolRenderer updates={updateGroup} />
            </div>
          </div>
        </div>
      ))}
    </>
  );
}