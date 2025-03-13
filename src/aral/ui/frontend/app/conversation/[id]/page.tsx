import ConversationPageComponent from "./component";

// This function is required for static site generation with dynamic routes
// It will only be used in production builds
export function generateStaticParams() {
    // Return an empty array since we don't know the conversation IDs at build time
    // The server.py file will handle serving the correct page for dynamic routes
    return [];
}

export default function ConversationPage() {
    return <ConversationPageComponent />;
} 