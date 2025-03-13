import { useEffect, useState } from "react";

interface LoadingDotsProps {
    className?: string;
}

export function LoadingDots({ className = "" }: LoadingDotsProps) {
    const [dots, setDots] = useState(".");

    useEffect(() => {
        const interval = setInterval(() => {
            setDots((prevDots) => {
                if (prevDots === "...") return ".";
                return prevDots + ".";
            });
        }, 500);

        return () => clearInterval(interval);
    }, []);

    return (
        <span className={`inline-block min-w-[24px] text-left ${className}`}>
            {dots}
        </span>
    );
} 