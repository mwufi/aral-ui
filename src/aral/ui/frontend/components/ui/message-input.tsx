import { useRef, useEffect, useState } from "react";
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
    const [localSubmitting, setLocalSubmitting] = useState(false);

    // Focus input on initial render
    useEffect(() => {
        if (autoFocus && inputRef.current) {
            inputRef.current.focus();
        }
    }, [autoFocus]);

    // Focus input when value changes to empty (after submit)
    useEffect(() => {
        if (value === "" && inputRef.current) {
            inputRef.current.focus();
        }
    }, [value]);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Prevent default form submission behavior

        if (value.trim() === "") {
            return; // Don't submit empty messages
        }

        // Set local submitting state to briefly disable the button
        // This prevents accidental double-submissions
        setLocalSubmitting(true);

        // Call the parent's onSubmit handler
        onSubmit(e);

        // Reset local submitting state after a short delay
        setTimeout(() => {
            setLocalSubmitting(false);

            // Focus the input after submission
            if (inputRef.current) {
                inputRef.current.focus();
            }
        }, 300);
    };

    return (
        <form onSubmit={handleFormSubmit} className="flex gap-2 items-center">
            <Input
                ref={inputRef}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="flex-1 rounded-full border-gray-200 bg-white/80 backdrop-blur-sm"
                disabled={isSubmitting} // Use the parent's isSubmitting prop
            />
            <Button
                type="submit"
                disabled={localSubmitting || isSubmitting || value.trim() === ""} // Disable when empty or submitting
                className="rounded-full bg-blue-500 hover:bg-blue-600 text-white"
            >
                {localSubmitting ? "..." : submitLabel}
            </Button>
        </form>
    );
} 