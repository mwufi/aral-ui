"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { fetchConversations, sendMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/ui/avatar";

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
  const [inputValue, setInputValue] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

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

    try {
      setIsSubmitting(true);
      setError(null);

      // Create a new conversation ID
      const newConversationId = uuidv4();

      // Send the message to the API
      await sendMessage(newConversationId, inputValue);

      // Redirect to the conversation page
      router.push(`/conversation/${newConversationId}`);
    } catch (err) {
      console.error("Error starting conversation:", err);
      setError("Failed to start conversation. Please try again.");
      setIsSubmitting(false);
    }
  };

  const handleSelectConversation = (id: string) => {
    router.push(`/conversation/${id}`);
  };

  // Get the last message for each conversation
  const getLastMessage = (conv: Conversation) => {
    if (conv.messages.length === 0) return "No messages";
    const lastMsg = conv.messages[conv.messages.length - 1];
    return lastMsg.content.length > 30
      ? lastMsg.content.substring(0, 30) + "..."
      : lastMsg.content;
  };

  // Get the timestamp for the last message
  const getLastMessageTime = (conv: Conversation) => {
    if (conv.messages.length === 0) return "";
    const lastMsg = conv.messages[conv.messages.length - 1];
    const date = new Date(lastMsg.created_at);

    // If today, show time, otherwise show date
    const now = new Date();
    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className="flex h-full">
      {/* Left sidebar - Conversations */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h1 className="text-xl font-semibold">almostzenbut_no</h1>
          <Button
            variant="ghost"
            className="p-1 h-8 w-8"
            onClick={() => { }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </Button>
        </div>

        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="font-medium">Messages</div>
            <div className="text-blue-500 text-sm font-medium ml-auto">Request (1)</div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="p-3 m-4 text-sm text-red-700 bg-red-100 rounded">
              {error}
            </div>
          )}

          {conversations.length === 0 ? (
            <div className="p-4 text-gray-500 text-sm">No conversations yet. Start a new one!</div>
          ) : (
            <div className="space-y-1">
              {conversations.map((conv: Conversation) => (
                <div
                  key={conv.id}
                  className="px-4 py-3 hover:bg-gray-100 cursor-pointer flex items-center gap-3"
                  onClick={() => handleSelectConversation(conv.id)}
                >
                  <Avatar className="h-12 w-12 bg-blue-500">
                    <span className="text-sm font-medium">
                      {conv.title?.charAt(0) || "C"}
                    </span>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center">
                      <div className="font-medium truncate">{conv.title}</div>
                      <div className="text-xs text-gray-500">{getLastMessageTime(conv)}</div>
                    </div>
                    <div className="text-sm text-gray-500 truncate">
                      {getLastMessage(conv)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* New conversation button */}
        <div className="p-4 border-t border-gray-200">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Start a new conversation..."
              className="flex-1 rounded-full border-gray-300"
              disabled={isSubmitting}
            />
            <Button
              type="submit"
              disabled={isSubmitting}
              className="rounded-full bg-blue-500 hover:bg-blue-600 text-white"
            >
              {isSubmitting ? "..." : "+"}
            </Button>
          </form>
        </div>
      </div>

      {/* Right content - Welcome screen */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 bg-gray-50">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4">Welcome to Aral Chat</h2>
          <p className="text-gray-600 mb-6">
            Select a conversation from the sidebar or start a new one to begin chatting.
          </p>
          <div className="flex justify-center">
            <Avatar className="h-24 w-24 bg-blue-500">
              <span className="text-2xl font-medium">A</span>
            </Avatar>
          </div>
        </div>
      </div>
    </div>
  );
}
