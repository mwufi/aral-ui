"use client";

import { useState } from "react";
import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useChatTheme, GradientTheme } from "@/providers/theme-provider";

export function ThemeSettings() {
    const { activeTheme, setTheme, availableThemes } = useChatTheme();

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" title="Theme Settings">
                    <Settings size={18} />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <div className="px-2 py-1.5 text-sm font-semibold">
                    Message Theme
                </div>
                {availableThemes.map((theme) => (
                    <DropdownMenuItem
                        key={theme.name}
                        onClick={() => setTheme(theme)}
                        className="flex items-center gap-2"
                    >
                        <div
                            className="w-4 h-4 rounded-full"
                            style={{
                                background: `linear-gradient(${theme.angle || 45}deg, ${theme.colors.join(', ')})`
                            }}
                        />
                        <span>{theme.name}</span>
                        {theme.name === activeTheme.name && (
                            <span className="ml-auto">✓</span>
                        )}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
} 