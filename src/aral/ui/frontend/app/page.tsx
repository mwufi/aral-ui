"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { fetchConversations, sendMessage } from "@/lib/api";
import { Avatar } from "@/components/ui/avatar";
import { Sidebar } from "@/components/ui/sidebar";
import { MessageInput } from "@/components/ui/message-input";
import { LoadingDots } from "@/components/ui/loading-dots";

// Define types for our data
interface Message {
  id: string;
  content: string;
  role: string;
  created_at: string;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}

export default function Home() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState<boolean>(false);

  // Fetch conversations
  useEffect(() => {
    const getConversations = async () => {
      try {
        setError(null);
        const data = await fetchConversations();
        setConversations(data.conversations || []);
      } catch (err) {
        console.error("Error fetching conversations:", err);
        setError("Failed to load conversations. Please try again.");
      }
    };

    getConversations();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) {
      return;
    }

    // Store the message content before clearing the input
    const messageContent = inputValue;

    // Clear the input immediately to allow the MessageInput component to refocus
    setInputValue("");

    try {
      // Don't disable the input while waiting for a response
      setError(null);

      // Store the message to display while waiting
      setPendingMessage(messageContent);

      // Show loading indicator
      setIsWaitingForResponse(true);

      // Create a new conversation ID
      const newConversationId = uuidv4();

      // Send the message to the API
      await sendMessage(newConversationId, messageContent);

      // Redirect to the conversation page
      router.push(`/conversation/${newConversationId}`);
    } catch (err) {
      console.error("Error starting conversation:", err);
      setError("Failed to start conversation. Please try again.");
      // Reset pending message if there's an error
      setPendingMessage(null);
      setIsWaitingForResponse(false);
    }
    // Don't set isSubmitting to false here, as we're redirecting anyway
  };

  return (
    <div className="flex h-full">
      {/* Left sidebar - Conversations */}
      <Sidebar
        conversations={conversations}
        error={error}
      />

      {/* Right content - Welcome screen with input */}
      <div className="flex-1 flex flex-col h-full border-l border-gray-200 bg-gray-50">
        <div className="flex-1 flex flex-col items-center justify-center p-6">
          <div className="text-center max-w-md">
            <div className="flex justify-center mb-8">
              <Avatar className="h-24 w-24 bg-blue-500">
                <span className="text-2xl font-medium">A</span>
              </Avatar>
            </div>
            <h2 className="text-2xl font-bold mb-4">Start a new conversation</h2>

            {/* Show pending message and loading state if applicable */}
            {pendingMessage && (
              <div className="max-w-3xl mx-auto w-full mb-4">
                <div className="flex justify-end mb-4">
                  <div className="flex flex-row-reverse gap-2 max-w-[80%]">
                    <Avatar className="h-8 w-8 shrink-0">
                      <span className="text-xs font-medium text-white">A</span>
                    </Avatar>
                    <div className="rounded-2xl px-3 py-2 bg-blue-500 text-white">
                      <p className="text-sm">{pendingMessage}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                </div>

                {isWaitingForResponse && (
                  <div className="flex justify-start mb-4">
                    <div className="flex gap-2 max-w-[80%]">
                      <Avatar className="h-8 w-8 shrink-0 bg-gradient-to-br from-blue-500 to-purple-500">
                        <span className="text-xs font-medium text-white">A</span>
                      </Avatar>
                      <div className="rounded-2xl px-3 py-2 bg-white/80 backdrop-blur-sm text-gray-800 shadow-sm">
                        <p className="text-sm flex items-center">
                          <LoadingDots />
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Input area in the middle */}
            <div className="max-w-3xl mx-auto w-full mb-8">
              <div className="bg-white/50 backdrop-blur-sm rounded-xl shadow-sm p-4">
                <MessageInput
                  value={inputValue}
                  onChange={handleInputChange}
                  onSubmit={handleSubmit}
                  isSubmitting={false}
                  placeholder="What do you want to know?"
                  submitLabel="Send"
                  autoFocus={true}
                />
              </div>
            </div>

            <p className="text-gray-600">
              Select a conversation from the sidebar or start a new one above.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
