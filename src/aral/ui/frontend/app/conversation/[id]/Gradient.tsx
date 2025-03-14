import { useChatTheme } from "@/providers/theme-provider";
import { ReactNode } from "react";

export default function Gradient({ children }: { children: ReactNode }) {
    const { activeTheme } = useChatTheme();
    const { colors, angle = 45 } = activeTheme;
    // Create a gradient that's large enough to cover the entire viewport
    const gradient = `linear-gradient(${angle}deg, ${colors.join(', ')})`;

    return (
        <div className="relative h-full">
            <div
                className="absolute inset-0 w-[200px] h-full pointer-events-none z-10"
                style={{
                    background: gradient,
                    mixBlendMode: 'screen',
                    backgroundAttachment: 'fixed', // This makes the gradient fixed while scrolling
                    backgroundSize: '100vw 50vh' // Ensure the gradient covers the entire viewport
                }}
            />
            <div className="relative z-0">
                {children}
            </div>
        </div>
    );
}