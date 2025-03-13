"use client";

import { useState } from 'react';
import { ToolUpdate } from '@/lib/api';

interface ToolCardProps {
  updates: ToolUpdate[];
  isInConversation?: boolean;
}

// Generic Tool Card component that shows a tool's status and details
export function ToolCard({ updates }: ToolCardProps) {
  const [showContent, setShowContent] = useState(true);
  
  if (!updates || updates.length === 0) {
    console.error('No updates provided to ToolCard');
    return null;
  }
  
  // Get the latest update
  const latestUpdate = updates[updates.length - 1];
  
  // Determine the state of the tool
  const isStarting = latestUpdate.type === 'tool_start';
  const isInProgress = latestUpdate.type === 'progress_update';
  const isComplete = latestUpdate.type === 'tool_result';
  
  // Get the progress percentage if available
  const progress = isInProgress 
    ? (latestUpdate.progress ? Math.round(latestUpdate.progress * 100) : 0) 
    : (isComplete ? 100 : 0);
  
  // Style based on state
  let cardStyle = 'bg-blue-50 border-blue-500'; // default/starting
  
  if (isInProgress) {
    cardStyle = 'bg-blue-50 border-yellow-500';
  } else if (isComplete) {
    cardStyle = 'bg-green-50 border-green-500';
  }
  
  // Format a value for display
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };
  
  // Get the first update for the arguments
  const firstUpdate = updates[0];
  
  // Get all the unique arguments from all updates
  const args = firstUpdate?.args || {};
  
  // Get the result if complete
  const result = isComplete ? latestUpdate.result : null;
  
  // Show error if any
  const error = latestUpdate.error;
  
  console.log('Rendering ToolCard with state:', { 
    isStarting, isInProgress, isComplete, 
    tool: latestUpdate.tool,
    progress,
    updates: updates.length
  });
  
  return (
    <div className={`mb-2 rounded-md ${cardStyle} border-l-4 shadow-sm overflow-hidden transition-all duration-300`}>
      <div className="px-4 py-2 flex justify-between items-center">
        <div className="flex items-center">
          {/* Tool Icon with state indicator */}
          {isStarting && (
            <div className="w-5 h-5 mr-2 rounded-full bg-blue-500 animate-pulse"></div>
          )}
          {isInProgress && (
            <div className="w-5 h-5 mr-2 rounded-full bg-yellow-500 animate-pulse"></div>
          )}
          {isComplete && (
            <div className="w-5 h-5 mr-2 rounded-full bg-green-500"></div>
          )}
          
          <div>
            <h3 className="font-medium text-sm flex items-center">
              <span className="truncate">{latestUpdate.tool || 'Tool'}</span>
              {isStarting && <span className="ml-1">(Running...)</span>}
              {isInProgress && <span className="ml-1">({progress}%)</span>}
              {isComplete && <span className="ml-1">(Complete)</span>}
            </h3>
          </div>
        </div>
        
        <button 
          onClick={() => setShowContent(!showContent)}
          className="text-gray-500 hover:text-gray-700 text-xs"
        >
          {showContent ? 'Hide' : 'Show'}
        </button>
      </div>
      
      {/* Progress bar */}
      {(isStarting || isInProgress) && (
        <div className="w-full h-1 bg-gray-200">
          <div 
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
      
      {showContent && (
        <div className="px-4 py-2 text-xs">
          {/* Tool arguments */}
          {Object.keys(args).length > 0 && (
            <div className="mb-2">
              <div className="font-medium text-gray-700">Arguments:</div>
              <pre className="bg-white/50 p-2 rounded mt-1 overflow-x-auto">
                {Object.entries(args).map(([key, value]) => (
                  <div key={key}>
                    <span className="text-blue-600">{key}:</span> {formatValue(value)}
                  </div>
                ))}
              </pre>
            </div>
          )}
          
          {/* Progress message if available */}
          {isInProgress && latestUpdate.message && (
            <div className="mb-2">
              <div className="font-medium text-gray-700">Status:</div>
              <div className="p-2">{latestUpdate.message}</div>
            </div>
          )}
          
          {/* Tool result - only show if completed */}
          {isComplete && result && (
            <div>
              <div className="font-medium text-gray-700">Result:</div>
              <pre className="bg-white/50 p-2 rounded mt-1 overflow-x-auto">
                {typeof result === 'object'
                  ? JSON.stringify(result, null, 2)
                  : result}
              </pre>
            </div>
          )}
          
          {/* Show error if any */}
          {error && (
            <div>
              <div className="font-medium text-red-700">Error:</div>
              <pre className="bg-red-50 text-red-700 p-2 rounded mt-1 overflow-x-auto">
                {error}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Custom renderer for weather tool
function WeatherToolCard({ updates }: ToolCardProps) {
  const latestUpdate = updates[updates.length - 1];
  const result = latestUpdate.type === 'tool_result' ? latestUpdate.result : null;
  
  if (!result) {
    return <ToolCard updates={updates} />;
  }
  
  return (
    <div className="mb-2 rounded-md bg-gradient-to-r from-blue-500 to-blue-300 text-white shadow-md overflow-hidden">
      <div className="px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <div className="text-lg mr-3">🌤️</div>
          <div>
            <h3 className="font-medium text-lg">{result.location}</h3>
            <div className="text-2xl font-bold">{result.temperature}°F</div>
            <div className="text-sm">{result.conditions}</div>
          </div>
        </div>
        <div className="text-right">
          <div>Humidity: {result.humidity}%</div>
          <div>Wind: {result.wind}</div>
        </div>
      </div>
    </div>
  );
}

// Component to render a custom visualization based on the tool type
export function CustomToolRenderer({ updates }: { updates: ToolUpdate[] }) {
  if (!updates || updates.length === 0) {
    console.error('No updates provided to CustomToolRenderer');
    return null;
  }
  
  const toolName = updates[0].tool;
  console.log('Rendering tool with name:', toolName);
  
  // Choose a specific renderer based on the tool type
  switch (toolName) {
    case 'weather':
      return <WeatherToolCard updates={updates} />;
    default:
      return <ToolCard updates={updates} />;
  }
}