"use client";

import { ReactNode, createContext, useState, useEffect, useContext } from "react";

// Define the GradientTheme type and export it
export type GradientTheme = {
    name: string;
    colors: string[];
    angle?: number;
    assistantMessages: boolean;
};

// Define the default themes
const defaultThemes: GradientTheme[] = [
    {
        name: 'Messenger',
        colors: ['#00c6ff', '#0072ff'],
        angle: 135, // Diagonal from top-right to bottom-left
        assistantMessages: true,
    },
    {
        name: 'Instagram',
        colors: ['#833ab4', '#fd1d1d', '#fcb045'],
        angle: 45, // Diagonal from top-left to bottom-right
        assistantMessages: true,
    },
    {
        name: 'Sunset',
        colors: ['#ff7e5f', '#feb47b'],
        angle: 180, // Horizontal from left to right
        assistantMessages: true,
    },
    {
        name: 'Ocean',
        colors: ['#2193b0', '#6dd5ed'],
        angle: 135, // Diagonal from top-right to bottom-left
        assistantMessages: true,
    },
    {
        name: 'Forest',
        colors: ['#11998e', '#38ef7d'],
        angle: 120, // Diagonal angle
        assistantMessages: true,
    },
    {
        name: 'Neon',
        colors: ['#f953c6', '#b91d73', '#00f2fe'],
        angle: 60, // Diagonal angle
        assistantMessages: true,
    },
];

// Define the context type
type ThemeContextType = {
    activeTheme: GradientTheme;
    setTheme: (theme: GradientTheme) => void;
    availableThemes: GradientTheme[];
    customTheme: GradientTheme;
    updateCustomTheme: (newCustomTheme: Partial<GradientTheme>) => void;
    addCustomThemeToAvailable: () => void;
};

// Create the context
const ThemeContext = createContext<ThemeContextType | null>(null);

// Provider component
export function ThemeProvider({ children }: { children: ReactNode }) {
    // Start with the Instagram theme as default since it's more visually striking
    const [activeTheme, setActiveTheme] = useState<GradientTheme>(defaultThemes[1]);
    const [customTheme, setCustomTheme] = useState<GradientTheme>({
        name: 'Custom',
        colors: ['#00c6ff', '#0072ff'],
        angle: 135,
        assistantMessages: true,
    });
    const [availableThemes, setAvailableThemes] = useState<GradientTheme[]>(defaultThemes);

    // Load theme from localStorage on initial render
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const savedTheme = localStorage.getItem('chatTheme');
            if (savedTheme) {
                try {
                    const parsedTheme = JSON.parse(savedTheme);
                    setActiveTheme(parsedTheme);
                } catch (e) {
                    console.error('Failed to parse saved theme', e);
                }
            }
        }
    }, []);

    // Save theme to localStorage when it changes
    useEffect(() => {
        if (typeof window !== 'undefined') {
            localStorage.setItem('chatTheme', JSON.stringify(activeTheme));
        }
    }, [activeTheme]);

    const setTheme = (theme: GradientTheme) => {
        setActiveTheme(theme);
    };

    const updateCustomTheme = (newCustomTheme: Partial<GradientTheme>) => {
        const updated = { ...customTheme, ...newCustomTheme };
        setCustomTheme(updated);

        // If we're currently using the custom theme, update the active theme too
        if (activeTheme.name === 'Custom') {
            setActiveTheme(updated);
        }
    };

    const addCustomThemeToAvailable = () => {
        if (!availableThemes.some(theme => theme.name === customTheme.name)) {
            setAvailableThemes([...availableThemes, customTheme]);
        }
        setActiveTheme(customTheme);
    };

    return (
        <ThemeContext.Provider
            value={{
                activeTheme,
                setTheme,
                availableThemes,
                customTheme,
                updateCustomTheme,
                addCustomThemeToAvailable,
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
}

// Hook to use the theme context
export function useChatTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useChatTheme must be used within a ThemeProvider');
    }
    return context;
} 