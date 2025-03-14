import { useState } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

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

interface SidebarProps {
    conversations: Conversation[];
    currentConversationId?: string;
    error: string | null;
}

export function Sidebar({ conversations, currentConversationId, error }: SidebarProps) {
    const router = useRouter();

    const handleNewConversation = () => {
        // Create a new conversation ID
        const newConversationId = uuidv4();

        // Redirect to the conversation page
        router.push(`/conversation/${newConversationId}`);
    };

    const handleSelectConversation = (id: string) => {
        if (id !== currentConversationId) {
            router.push(`/conversation/${id}`);
        }
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
        <div className="hidden md:block w-90 bg-white flex flex-col rounded-lg">
            <div className="p-4 flex justify-between items-center">
                <h1 className="text-xl font-semibold">almostzenbut_no</h1>
                <Button
                    variant="ghost"
                    className="p-2 h-10 w-10 rounded-full hover:bg-gray-100"
                    onClick={handleNewConversation}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                </Button>
            </div>

            <div className="p-4">
                <div className="font-medium text-lg">Messages</div>
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
                    <div className="p-1">
                        {conversations.map((conv: Conversation) => (
                            <div
                                key={conv.id}
                                className={`px-4 py-3 my-1 hover:bg-zinc-50 rounded-lg cursor-pointer flex items-center gap-3 ${conv.id === currentConversationId ? 'bg-zinc-50' : ''}`}
                                onClick={() => handleSelectConversation(conv.id)}
                            >
                                <Avatar className="h-12 w-12 bg-blue-500">
                                    <span className="text-sm font-medium">
                                        {conv.title?.charAt(0) || "C"}
                                    </span>
                                </Avatar>
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium truncate">{conv.title}</div>
                                    <div className="flex justify-between items-center">
                                        <div className="text-sm text-gray-500 truncate">
                                            {getLastMessage(conv)}
                                        </div>
                                        <div className="text-xs text-gray-500 w-20 text-right">{getLastMessageTime(conv)}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
} 