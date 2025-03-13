import React from "react";

export default function ConversationLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex h-full">
            {children}
        </div>
    );
} 