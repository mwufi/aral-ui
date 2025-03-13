"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { fetchConversations, sendMessage } from "@/lib/api";
import { Avatar } from "@/components/ui/avatar";
import { Sidebar } from "@/components/ui/sidebar";
import { MessageInput } from "@/components/ui/message-input";

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

export default function ConversationPageComponent() {
    const params = useParams();
    const router = useRouter();
    const conversationId = params.id as string;
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);

    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [inputValue, setInputValue] = useState<string>("");
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [initialLoadComplete, setInitialLoadComplete] = useState<boolean>(false);

    // Fetch conversations
    useEffect(() => {
        const getConversations = async () => {
            try {
                setError(null);
                const data = await fetchConversations();
                setConversations(data.conversations || []);

                // If the conversation doesn't exist, redirect to home
                if (data.conversations && !data.conversations.some((conv: Conversation) => conv.id === conversationId)) {
                    router.push("/");
                }

                // Mark initial load as complete after data is fetched
                setInitialLoadComplete(true);
            } catch (err) {
                console.error("Error fetching conversations:", err);
                setError("Failed to load conversation. Please try again.");
                setInitialLoadComplete(true);
            }
        };

        if (conversationId) {
            getConversations();
        }
    }, [conversationId, router]);

    // Handle scrolling behavior
    useEffect(() => {
        // On initial load, scroll to bottom immediately without animation
        if (initialLoadComplete && chatContainerRef.current && conversations.length > 0) {
            const container = chatContainerRef.current;
            container.scrollTop = container.scrollHeight;
        }
    }, [initialLoadComplete, conversations]);

    // Handle smooth scrolling for new messages after user sends a message
    const scrollToBottom = (smooth = true) => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({
                behavior: smooth ? "smooth" : "auto"
            });
        }
    };

    // When conversations update and we're already at the initial load, scroll smoothly
    useEffect(() => {
        if (initialLoadComplete && conversations.length > 0) {
            scrollToBottom(true);
        }
    }, [conversations.length, initialLoadComplete]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputValue.trim() || !conversationId) {
            return;
        }

        try {
            setIsSubmitting(true);
            setError(null);

            // Add user message to UI immediately
            const userMessage: Message = {
                id: uuidv4(),
                content: inputValue,
                role: "user",
                created_at: new Date().toISOString(),
            };

            // Find the active conversation and add the message
            const updatedConversations = conversations.map((conv: Conversation) => {
                if (conv.id === conversationId) {
                    return {
                        ...conv,
                        messages: [...conv.messages, userMessage]
                    };
                }
                return conv;
            });

            setConversations(updatedConversations);

            // Scroll to bottom after adding the message
            setTimeout(() => scrollToBottom(true), 50);

            // Send the message to the API
            await sendMessage(conversationId, inputValue);

            // Clear the input
            setInputValue("");

            // Refresh conversations to get the assistant's response
            const data = await fetchConversations();
            setConversations(data.conversations || []);

            // Scroll to bottom after receiving the response
            setTimeout(() => scrollToBottom(true), 50);
        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to send message. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const currentConversation = conversations.find((conv: Conversation) => conv.id === conversationId);

    return (
        <div className="flex h-full w-full">
            {/* Left sidebar - Conversations */}
            <Sidebar
                conversations={conversations}
                currentConversationId={conversationId}
                error={error}
            />

            {/* Right content - Chat */}
            <div className="flex-1 flex flex-col h-full border-l border-gray-200 bg-gray-50">
                {/* Header */}
                <header className="bg-white border-b border-gray-200 py-4 px-4 flex items-center">
                    <div className="flex items-center max-w-3xl mx-auto w-full">
                        <Avatar className="h-8 w-8 bg-blue-500 mr-2">
                            <span className="text-xs font-medium">
                                {currentConversation?.title?.charAt(0) || "C"}
                            </span>
                        </Avatar>
                        <div>
                            <h1 className="text-base font-semibold">
                                {currentConversation?.title || "Conversation"}
                            </h1>
                            <p className="text-xs text-gray-500">
                                {currentConversation?.messages?.length || 0} messages
                            </p>
                        </div>
                    </div>
                </header>

                {/* Chat area */}
                <div className="flex-1 overflow-y-auto" ref={chatContainerRef}>
                    <div className="max-w-3xl mx-auto w-full p-4 space-y-4">
                        {currentConversation?.messages.map((msg: Message) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                                <div className={`flex gap-2 max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                                    <Avatar className={`h-8 w-8 shrink-0 ${msg.role === "user" ? "bg-blue-500" : "bg-gray-300"}`}>
                                        <span className="text-xs font-medium">
                                            {msg.role === "user" ? "Me" : "A"}
                                        </span>
                                    </Avatar>
                                    <div className={`rounded-2xl px-3 py-2 ${msg.role === "user"
                                        ? "bg-blue-500 text-white"
                                        : "bg-white/80 backdrop-blur-sm text-gray-800 shadow-sm"
                                        }`}>
                                        <p className="text-sm">{msg.content}</p>
                                        <p className="text-xs opacity-70 mt-1">
                                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input area */}
                <div className="p-4 max-w-3xl mx-auto w-full">
                    <div className="bg-white/50 backdrop-blur-sm rounded-xl shadow-sm p-3">
                        <MessageInput
                            value={inputValue}
                            onChange={handleInputChange}
                            onSubmit={handleSubmit}
                            isSubmitting={isSubmitting}
                            autoFocus={true}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
} 