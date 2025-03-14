"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { fetchConversations, sendMessage } from "@/lib/api";
import { Sidebar } from "@/components/ui/sidebar";
import { MessageInput } from "@/components/ui/message-input";
import { LoadingDots } from "@/components/ui/loading-dots";
import { Message, ChatThemeProvider } from "@/components/ui/message";
import { useChatTheme } from "@/providers/theme-provider";
import { ThemeSettings } from "@/components/ui/theme-settings";

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

    const { activeTheme } = useChatTheme();

    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [inputValue, setInputValue] = useState<string>("");
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [initialLoadComplete, setInitialLoadComplete] = useState<boolean>(false);
    const [isWaitingForResponse, setIsWaitingForResponse] = useState<boolean>(false);

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

        // Store the message content before clearing the input
        const messageContent = inputValue;

        // Clear the input immediately to allow the MessageInput component to refocus
        setInputValue("");

        try {
            // Only set isSubmitting for the current message, not for the entire UI
            // This allows sending new messages while waiting for a response
            setError(null);

            // Add user message to UI immediately
            const userMessage: Message = {
                id: uuidv4(),
                content: messageContent,
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

            // Show loading indicator for this specific message
            setIsWaitingForResponse(true);

            // Send the message to the API
            await sendMessage(conversationId, messageContent);

            // Refresh conversations to get the assistant's response
            const data = await fetchConversations();
            setConversations(data.conversations || []);

            // Scroll to bottom after receiving the response
            setTimeout(() => scrollToBottom(true), 50);
        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to send message. Please try again.");
        } finally {
            setIsWaitingForResponse(false);
        }
    };
    const currentConversation = conversations.find((conv: Conversation) => conv.id === conversationId);

    const parseMessageContent = (content: string) => {
        const blocks: { type: 'text' | 'code', content: string, language?: string }[] = [];
        const lines = content.split('\n');

        let currentBlock: typeof blocks[0] | null = null;
        let inCodeBlock = false;
        let codeLanguage = '';

        lines.forEach(line => {
            const codeBlockMatch = line.match(/^```(\w*)$/);

            if (codeBlockMatch) {
                if (inCodeBlock) {
                    // End code block
                    if (currentBlock) blocks.push(currentBlock);
                    currentBlock = null;
                    inCodeBlock = false;
                } else {
                    // Start code block
                    if (currentBlock) blocks.push(currentBlock);
                    inCodeBlock = true;
                    codeLanguage = codeBlockMatch[1];
                    currentBlock = { type: 'code', content: '', language: codeLanguage };
                }
            } else if (inCodeBlock) {
                // Add to current code block
                if (currentBlock) {
                    currentBlock.content += (currentBlock.content ? '\n' : '') + line;
                }
            } else {
                // Regular text line
                if (line.trim()) {
                    blocks.push({ type: 'text', content: line });
                }
            }
        });

        if (currentBlock) blocks.push(currentBlock);
        return blocks;
    };

    return (
        <div className="flex h-full w-full gap-4">
            {/* Left sidebar - Conversations */}
            <Sidebar
                conversations={conversations}
                currentConversationId={conversationId}
                error={error}
            />

            {/* Right content - Chat */}
            <div className="flex-1 flex flex-col h-full bg-gray-50">
                {/* Header */}
                <header className="bg-white py-4 px-4 flex items-center rounded-t-lg">
                    <div className="flex items-center mx-auto w-full">
                        <Message.Avatar role="assistant" />
                        <div className="ml-2 flex-1">
                            <h1 className="text-base font-semibold">
                                {currentConversation?.title || "Conversation"}
                            </h1>
                            <p className="text-xs text-gray-500">
                                {currentConversation?.messages?.length || 0} messages
                            </p>
                        </div>

                        {/* Theme settings */}
                        <ThemeSettings />
                    </div>
                </header>

                {/* Chat area */}
                <div className="flex-1 overflow-y-auto bg-white" ref={chatContainerRef}>
                    <ChatThemeProvider theme={activeTheme}>
                        <div className="mx-auto w-full p-4">
                            {currentConversation?.messages.map((msg: Message) => {
                                const messageBlocks = parseMessageContent(msg.content);
                                const role = msg.role as "user" | "assistant";

                                return (
                                    <div key={msg.id} className="mb-6">
                                        <div className="flex gap-2">
                                            <div className={`shrink-0 ${role === "user" ? "hidden md:block order-last" : "order-first"}`}>
                                                <Message.Avatar role={role} />
                                            </div>
                                            <div className="flex-1">
                                                <Message.Block role={role}>
                                                    {messageBlocks.map((block, idx) => (
                                                        <div key={idx} className={`flex ${role === "user" ? "justify-end" : "justify-start"} w-full`}>
                                                            {block.type === 'code' ? (
                                                                <Message.CodeBubble
                                                                    language={block.language}
                                                                    content={block.content}
                                                                    messageId={msg.id}
                                                                    blockIdx={idx}
                                                                />
                                                            ) : (
                                                                <Message.Bubble
                                                                    role={role}
                                                                    content={block.content}
                                                                />
                                                            )}
                                                        </div>
                                                    ))}
                                                </Message.Block>
                                                <Message.Timestamp timestamp={msg.created_at} role={role} />
                                            </div>
                                        </div>
                                    </div>
                                );
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
                    </ChatThemeProvider>
                </div>

                {/* Input area */}
                <div className="p-4 mx-auto w-full">
                    <div className="bg-white/50 backdrop-blur-sm rounded-xl shadow-sm p-3">
                        <MessageInput
                            value={inputValue}
                            onChange={handleInputChange}
                            onSubmit={handleSubmit}
                            isSubmitting={false} // Never disable the input
                            autoFocus={true}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
} 