"use client";

import { useState, useRef, useEffect } from "react";
import { Message } from "@/components/ui/message";
import { ToolUpdates } from "@/components/ui/tool-updates";
import { LoadingDots } from "@/components/ui/loading-dots";
import { useLiveUpdates } from "@/lib/websocket-context";
import { CustomToolRenderer } from "@/components/ui/tool-update";

interface ConversationMessage {
  id: string;
  content: any; // Can be string or array of content blocks
  role: string;
  created_at: string;
}

interface ConversationFlowProps {
  conversationId: string;
  messages: ConversationMessage[];
  isWaitingForResponse: boolean;
  parseMessageContent?: (content: any) => any[];
}

export function ConversationFlow({ 
  conversationId, 
  messages, 
  isWaitingForResponse,
  parseMessageContent = (content) => {
    // Handle different content formats
    if (typeof content === 'string') {
      return [{ type: 'text', content }];
    } else if (Array.isArray(content)) {
      // Format expected from Claude API with content blocks
      return content.map(block => {
        if (block.type === 'text') {
          return { type: 'text', content: block.text };
        }
        return block;
      });
    }
    return [{ type: 'text', content: String(content) }];
  }
}: ConversationFlowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { updates } = useLiveUpdates(conversationId);
  
  // This triggers a scroll to the bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isWaitingForResponse]);

  // Process messages and tool updates into a unified timeline
  const timelineItems = messages.flatMap((msg, index) => {
    const messageBlocks = parseMessageContent(msg.content);
    const role = msg.role as "user" | "assistant";
    const timelineItems = [];
    
    // First add the message itself
    timelineItems.push({
      type: 'message',
      id: msg.id,
      role,
      messageBlocks,
      timestamp: new Date(msg.created_at).getTime(),
      created_at: msg.created_at
    });
    
    // If this is an assistant message, check for tool_use blocks and matching updates
    if (role === 'assistant') {
      // Handle content blocks (potential tool_use blocks)
      if (Array.isArray(msg.content)) {
        // Find any tool_use blocks and add them as tool updates immediately after the message
        msg.content.forEach(block => {
          if (block.type === 'tool_use') {
            // Find corresponding tool updates for this tool_use_id
            const toolUpdatesForBlock = Object.values(updates)
              .flat()
              .filter(update => 
                update.tool_use_id === block.id || 
                update.tool === block.name
              );
            
            if (toolUpdatesForBlock.length > 0) {
              timelineItems.push({
                type: 'tool_update',
                toolUpdates: toolUpdatesForBlock,
                timestamp: new Date(msg.created_at).getTime() + 1 // Ensure it appears after the message
              });
            }
          }
        });
      }
    }
    
    return timelineItems;
  });
  
  // Sort timeline items by timestamp
  timelineItems.sort((a, b) => a.timestamp - b.timestamp);
  
  return (
    <div className="flex-1 overflow-y-auto" ref={containerRef}>
      <div className="max-w-3xl mx-auto w-full p-4">
        {timelineItems.map((item, index) => {
          if (item.type === 'message') {
            return (
              <div key={`msg-${item.id}`} className="mb-6">
                <div className="flex gap-2">
                  <div className={`shrink-0 ${item.role === "user" ? "order-last" : "order-first"}`}>
                    <Message.Avatar role={item.role} />
                  </div>
                  <div className="flex-1">
                    <Message.Block role={item.role}>
                      {item.messageBlocks
                        .filter(block => block.type !== 'tool_use') // Don't render tool_use blocks directly
                        .map((block, idx) => (
                          <div key={idx} className={`flex ${item.role === "user" ? "justify-end" : "justify-start"} w-full`}>
                            {block.type === 'code' ? (
                              <Message.CodeBubble
                                language={block.language}
                                content={block.content}
                                messageId={item.id}
                                blockIdx={idx}
                              />
                            ) : (
                              <Message.Bubble
                                role={item.role}
                                content={block.content}
                              />
                            )}
                          </div>
                        ))}
                    </Message.Block>
                    <Message.Timestamp timestamp={item.created_at} role={item.role} />
                  </div>
                </div>
              </div>
            );
          } else if (item.type === 'tool_update') {
            return (
              <div key={`tool-${index}`} className="flex justify-start mb-4 ml-12">
                <div className="flex gap-2 max-w-[90%] w-full">
                  <div className="flex-1">
                    <CustomToolRenderer updates={item.toolUpdates} />
                  </div>
                </div>
              </div>
            );
          }
          return null;
        })}

        {/* Legacy tool updates - can be removed once migration is complete */}
        {messages.map((msg, index) => {
          const role = msg.role as "user" | "assistant";
          if (role === "assistant") {
            const isLastAssistantMessage = role === "assistant" && 
              index === messages.length - 1 && 
              messages.filter(m => m.role === "assistant").length > 0;
              
            // Only show for the last assistant message and only for backwards compatibility
            if (isLastAssistantMessage && !Array.isArray(msg.content)) {
              return (
                <div key={`legacy-tools-${msg.id}`} className="mt-2 ml-12">
                  <ToolUpdates conversationId={conversationId} messageId={msg.id} />
                </div>
              );
            }
          }
          return null;
        })}

        {/* Loading indicator when waiting for response */}
        {isWaitingForResponse && (
          <div className="flex justify-start">
            <div className="flex gap-2 max-w-[80%]">
              <Message.Avatar role="assistant" />
              <div className="rounded-2xl px-3 py-2 bg-white/80 backdrop-blur-sm text-gray-800 shadow-sm">
                <p className="text-sm flex items-center">
                  <LoadingDots />
                </p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}