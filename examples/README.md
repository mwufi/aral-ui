# Aral Examples

This directory contains example agents built with Aral.

## SimpleAgent

A basic agent that echoes back messages and keeps track of conversations.

## How Aral Serves Your Agent

By default, Aral serves your agent using a single FastAPI server that:
1. Handles all API requests through FastAPI endpoints
2. Serves a pre-built static export of the Next.js frontend
3. Runs everything on a single port

This approach is optimized for production use, but it has limitations during development:
- Frontend changes require rebuilding the Next.js app and restarting the server
- You don't get access to Next.js development tools and hot reloading
- Debugging frontend issues can be more challenging

### Running in Production Mode

To run the SimpleAgent in production mode (with a single server serving both the API and UI):

```bash
python simple_agent.py
```

This will start a server on port 3000 by default. You can specify a different port:

```bash
python simple_agent.py --port 8000
```

### Running in Development Mode

For frontend development, Aral provides a `--dev` flag that:
1. Starts the FastAPI backend on a separate port
2. Runs the Next.js frontend in development mode with hot reloading
3. Configures the frontend to communicate with the backend API
4. Enables all Next.js development tools and features

```bash
python simple_agent.py --dev
```

This will:
- Start the Next.js dev server on port 3000 (default)
- Start the FastAPI backend on port 4000 (default)

You can customize the ports:

```bash
python simple_agent.py --dev --port 8000 --api-port 9000
```

#### Benefits of Development Mode

- **Hot Reloading**: Changes to frontend code are immediately reflected in the browser
- **Better Debugging**: Improved error messages and source maps
- **Development Tools**: Access to Next.js development features
- **Faster Workflow**: No need to rebuild and restart when making UI changes
- **Separate Concerns**: Develop frontend and backend independently

In development mode, any changes to the frontend code will be automatically reflected in the browser without needing to restart the server.

## Custom Development

If you want more control, you can run the frontend and backend separately manually:

1. Start the backend:
```bash
cd /path/to/your/agent
python your_agent.py --dev --port 3000 --api-port 4000
```

2. In a separate terminal, run the frontend:
```bash
cd src/aral/ui/frontend
NEXT_PUBLIC_API_URL=http://localhost:4000 bun run dev --port 3000
```

This approach gives you full control over both processes and is useful for:
- Running the frontend with custom Next.js configurations
- Using different development tools or environments
- Debugging specific parts of the application
- Testing with different frontend or backend versions 
