import { useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface MessageInputProps {
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onSubmit: (e: React.FormEvent) => void;
    isSubmitting: boolean;
    placeholder?: string;
    submitLabel?: string;
    autoFocus?: boolean;
}

export function MessageInput({
    value,
    onChange,
    onSubmit,
    isSubmitting,
    placeholder = "Message...",
    submitLabel = "Send",
    autoFocus = false
}: MessageInputProps) {
    const inputRef = useRef<HTMLInputElement>(null);

    // Focus input on initial render and when value changes to empty (after submit)
    useEffect(() => {
        if (autoFocus && inputRef.current) {
            // Focus on initial render or when value becomes empty
            if (value === "") {
                inputRef.current.focus();
            }
        }
    }, [autoFocus, value]);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Prevent default form submission behavior
        onSubmit(e);

        // Focus the input after submission with a small delay to ensure
        // any state updates have completed
        setTimeout(() => {
            if (inputRef.current) {
                inputRef.current.focus();
            }
        }, 100); // Slightly longer timeout to ensure state updates complete
    };

    return (
        <form onSubmit={handleFormSubmit} className="flex gap-2 items-center">
            <Input
                ref={inputRef}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="flex-1 rounded-full border-gray-200 bg-white/80 backdrop-blur-sm"
                disabled={isSubmitting}
            />
            <Button
                type="submit"
                disabled={isSubmitting || value.trim() === ""} // Disable when empty or submitting
                className="rounded-full bg-blue-500 hover:bg-blue-600 text-white"
            >
                {isSubmitting ? "..." : submitLabel}
            </Button>
        </form>
    );
} 