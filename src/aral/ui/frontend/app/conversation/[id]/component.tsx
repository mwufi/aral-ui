"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { fetchConversations, sendMessage } from "@/lib/api";
import { Sidebar } from "@/components/ui/sidebar";
import { MessageInput } from "@/components/ui/message-input";
import { ConversationFlow } from "@/components/ui/conversation-flow";
import { Message } from "@/components/ui/message";
import { ToolUpdates } from "@/components/ui/tool-updates";
import { useLiveUpdates } from "@/lib/websocket-context";

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
    actions?: any[];
}

export default function ConversationPageComponent() {
    const params = useParams();
    const router = useRouter();
    const conversationId = params.id as string;

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
    
    // Find the current conversation
    const currentConversation = conversations.find((conv: Conversation) => conv.id === conversationId);
    
    // Use the live updates hook for this conversation
    const { updates: toolUpdates, isConnected, setInitialUpdates } = useLiveUpdates(conversationId);
    
    // Process stored actions into tool updates when conversation changes
    useEffect(() => {
        if (currentConversation?.actions && Array.isArray(currentConversation.actions)) {
            console.log('Found stored actions:', currentConversation.actions.length);
            
            // Filter for tool update actions
            const toolUpdates = currentConversation.actions
                .filter(action => 
                    action.action_type === 'tool_start' || 
                    action.action_type === 'progress_update' || 
                    action.action_type === 'tool_result'
                )
                .map(action => action.data);
            
            // Group updates by their ID
            const groupedUpdates: Record<string, any[]> = {};
            toolUpdates.forEach(update => {
                if (update && update.id) {
                    if (!groupedUpdates[update.id]) {
                        groupedUpdates[update.id] = [];
                    }
                    groupedUpdates[update.id].push(update);
                }
            });
            
            // Initialize the tool updates in the context
            if (setInitialUpdates && Object.keys(groupedUpdates).length > 0) {
                console.log('Setting initial tool updates:', Object.keys(groupedUpdates).length);
                setInitialUpdates(groupedUpdates);
            }
        }
    }, [currentConversation, setInitialUpdates]);


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

            // Show loading indicator for this specific message
            setIsWaitingForResponse(true);

            // Send the message to the API
            await sendMessage(conversationId, messageContent);

            // Refresh conversations to get the assistant's response
            const data = await fetchConversations();
            setConversations(data.conversations || []);
        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to send message. Please try again.");
        } finally {
            setIsWaitingForResponse(false);
        }
    };

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
                        <Message.Avatar role="assistant" />
                        <div className="ml-2">
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
                <div className="flex-1 flex flex-col">
                    <ConversationFlow 
                        conversationId={conversationId}
                        messages={currentConversation?.messages || []}
                        isWaitingForResponse={isWaitingForResponse}
                        parseMessageContent={parseMessageContent}
                    />
                </div>

                {/* Input area */}
                <div className="p-4 max-w-3xl mx-auto w-full">
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