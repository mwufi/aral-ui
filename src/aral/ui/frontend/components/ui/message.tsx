"use client";

import { ReactNode, useState, useContext } from "react";
import { Avatar as UIAvatar, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown, ChevronUp, Copy } from "lucide-react";
import { createContext } from "react";
import { GradientTheme } from "@/providers/theme-provider";

// Create a context for the theme
const ChatThemeContext = createContext<GradientTheme | null>(null);

export const ChatThemeProvider = ({ children, theme }: { children: ReactNode, theme: GradientTheme }) => {
    const { colors, angle = 45 } = theme;
    // Create a gradient that's large enough to cover the entire viewport
    const gradient = `linear-gradient(${angle}deg, ${colors.join(', ')})`;

    return (
        <ChatThemeContext.Provider value={theme}>
            <div className="relative w-full h-full">
                {/* Gradient overlay that will blend with black message bubbles */}
                <div
                    className="fixed inset-0 w-full h-full pointer-events-none z-10"
                    style={{
                        background: gradient,
                        mixBlendMode: 'screen',
                        backgroundAttachment: 'fixed', // This makes the gradient fixed while scrolling
                        backgroundSize: '100vw 100vh' // Ensure the gradient covers the entire viewport
                    }}
                />

                {/* Actual chat content */}
                <div className="relative z-0">
                    {children}
                </div>
            </div>
        </ChatThemeContext.Provider>
    );
};

interface MessageBlockProps {
    role: "user" | "assistant";
    children: ReactNode;
}

interface MessageBubbleProps {
    role: "user" | "assistant";
    content: string;
}

interface MessageAvatarProps {
    role: "user" | "assistant";
}

interface CodeBubbleProps {
    language?: string;
    content: string;
    messageId: string;
    blockIdx: number;
}

// Store collapsed state globally to persist between renders
const collapsedCodeBlocks: Record<string, boolean> = {};

const Avatar = ({ role }: MessageAvatarProps) => {
    return (
        <UIAvatar className={`h-8 w-8 ${role === "user" ? "" : "bg-gradient-to-br from-blue-500 to-purple-500"}`}>
            {role === "assistant" ? (
                <AvatarImage src="/favicon-platform.png" alt="Assistant" />
            ) : (
                <span className="text-xs font-medium text-white">A</span>
            )}
        </UIAvatar>
    );
};

const Bubble = ({ role, content }: MessageBubbleProps) => {
    const isUser = role === "user";

    // For user messages, use black background to show the gradient through mix-blend-mode
    // For assistant messages, use a higher z-index to place them above the gradient
    return (
        <div
            className={`rounded-2xl px-3 py-2 max-w-[80%] ${isUser
                ? "bg-black text-white z-0" // User messages: black background to show gradient
                : "bg-zinc-100 text-gray-800 z-20 relative" // Assistant messages: above the gradient
                }`}
        >
            <p className="text-[15px] whitespace-pre-wrap">{content}</p>
        </div>
    );
};

const CodeBubble = ({ language, content, messageId, blockIdx }: CodeBubbleProps) => {
    const blockKey = `${messageId}-${blockIdx}`;
    const [isCollapsed, setIsCollapsed] = useState(collapsedCodeBlocks[blockKey] || false);

    const toggleCodeBlock = () => {
        const newState = !isCollapsed;
        collapsedCodeBlocks[blockKey] = newState;
        setIsCollapsed(newState);
    };

    const copyCodeToClipboard = () => {
        navigator.clipboard.writeText(content);
    };

    return (
        <div className="max-w-[95%] w-full bg-white/80 backdrop-blur-sm rounded-xl overflow-hidden shadow-sm my-1 relative z-20">
            <div className="bg-gray-100 px-4 py-1 flex justify-between items-center">
                <span className="text-xs text-gray-500">
                    {language || 'Code'}
                </span>
                <div className="flex gap-2">
                    <button
                        onClick={copyCodeToClipboard}
                        className="p-1 hover:bg-gray-200 rounded"
                        title="Copy code"
                    >
                        <Copy size={14} />
                    </button>
                    <button
                        onClick={toggleCodeBlock}
                        className="p-1 hover:bg-gray-200 rounded"
                        title={isCollapsed ? "Expand code" : "Collapse code"}
                    >
                        {isCollapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                    </button>
                </div>
            </div>
            {!isCollapsed && (
                <pre className="px-4 py-3 text-sm overflow-x-auto">
                    <code>{content}</code>
                </pre>
            )}
        </div>
    );
};

const Block = ({ role, children }: MessageBlockProps) => {
    const isUser = role === "user";

    return (
        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} gap-1`}>
            {children}
        </div>
    );
};

const Timestamp = ({ timestamp, role }: { timestamp: string, role: "user" | "assistant" }) => {
    return (
        <div className={`flex ${role === "user" ? "justify-end" : "justify-start"} mt-1 relative z-20`}>
            <p className="text-xs text-gray-500">
                {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
        </div>
    );
};

// Export as namespace-like object
const Message = {
    Avatar,
    Bubble,
    CodeBubble,
    Block,
    Timestamp
};

export { Message }; 