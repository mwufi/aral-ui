"use client";

import { useLiveUpdates } from "@/lib/websocket-context";
import { CustomToolRenderer } from "@/components/ui/tool-update";
import { Message } from "@/components/ui/message";

interface ToolUpdatesProps {
  conversationId: string;
}

export function ToolUpdates({ conversationId }: ToolUpdatesProps) {
  // Use our custom hook to get updates for this conversation
  const { updates, isConnected } = useLiveUpdates(conversationId);
  
  // If there are no updates, don't render anything
  if (Object.keys(updates).length === 0) {
    return null;
  }
  
  return (
    <>
      {Object.values(updates).map((updateGroup, groupIdx) => {
        // Find the latest update in the group
        const latestUpdate = updateGroup[updateGroup.length - 1];
        
        // Only show if it's for the current conversation
        if (latestUpdate.conversation_id !== conversationId) {
          return null;
        }
        
        return (
          <div key={`tool-${groupIdx}`} className="flex justify-start mb-4">
            <div className="flex gap-2 max-w-[90%] w-full">
              <Message.Avatar role="assistant" />
              <div className="flex-1">
                <CustomToolRenderer update={latestUpdate} />
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}