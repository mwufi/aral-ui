"use client";

import { ReactNode } from "react";
import { GradientTheme } from "@/providers/theme-provider";

interface GradientBubbleProps {
    content: string;
    theme: GradientTheme;
}

export const GradientBubble = ({ content, theme }: GradientBubbleProps) => {
    const { colors, angle = 45 } = theme;

    // In CSS, 0deg points to the top and then rotates clockwise
    // So 90deg points to the right, 180deg to the bottom, etc.
    // Create the gradient string with the correct angle
    const gradient = `linear-gradient(${angle}deg, ${colors.join(', ')})`;

    return (
        <div className="relative rounded-2xl max-w-[80%] overflow-hidden shadow-sm">
            {/* Gradient background */}
            <div
                className="absolute inset-0 w-full h-full"
                style={{ background: gradient }}
            />

            {/* Text content with mix-blend-mode */}
            <div className="relative px-3 py-2 mix-blend-screen bg-black">
                <p className="text-[15px] whitespace-pre-wrap text-white font-medium tracking-wide">{content}</p>
            </div>
        </div>
    );
}; 