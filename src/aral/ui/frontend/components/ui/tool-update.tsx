"use client";

import { useEffect, useState } from 'react';
import { ToolUpdate } from '@/lib/api';

interface ToolCardProps {
  update: ToolUpdate;
}

// Component to display a tool card with spinner or result
const ToolCard = ({ update }: ToolCardProps) => {
  const [showContent, setShowContent] = useState(true);

  const isStarting = update.type === 'tool_start';
  const cardStyle = isStarting ? 'bg-blue-50' : 'bg-green-50';
  const borderStyle = isStarting 
    ? 'border-l-4 border-blue-500' 
    : 'border-l-4 border-green-500';

  // Function to format tool arguments for display
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  return (
    <div className={`mb-2 rounded-md ${cardStyle} ${borderStyle} shadow-sm overflow-hidden`}>
      <div className="px-4 py-2 flex justify-between items-center">
        <div className="flex items-center">
          {/* Tool Icon - could be customized based on tool type */}
          {isStarting ? (
            <div className="w-5 h-5 mr-2 rounded-full bg-blue-500 animate-pulse"></div>
          ) : (
            <div className="w-5 h-5 mr-2 rounded-full bg-green-500"></div>
          )}
          
          <div>
            <h3 className="font-medium text-sm">
              {update.tool || 'Tool'} 
              {isStarting ? ' (Running...)' : ' (Complete)'}
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
      
      {showContent && (
        <div className="px-4 py-2 text-xs">
          {/* Tool arguments */}
          {update.args && (
            <div className="mb-2">
              <div className="font-medium text-gray-700">Arguments:</div>
              <pre className="bg-white/50 p-2 rounded mt-1 overflow-x-auto">
                {Object.entries(update.args).map(([key, value]) => (
                  <div key={key}>
                    <span className="text-blue-600">{key}:</span> {formatValue(value)}
                  </div>
                ))}
              </pre>
            </div>
          )}
          
          {/* Tool result - only show if completed */}
          {!isStarting && update.result && (
            <div>
              <div className="font-medium text-gray-700">Result:</div>
              <pre className="bg-white/50 p-2 rounded mt-1 overflow-x-auto">
                {typeof update.result === 'object'
                  ? JSON.stringify(update.result, null, 2)
                  : update.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Component to render a custom visualization based on the tool type
const CustomToolRenderer = ({ update }: { update: ToolUpdate }) => {
  // You can add custom renderers for specific tools here
  // For example, a weather card, a map, a chart, etc.
  
  // In this example, we'll just render a generic card
  return <ToolCard update={update} />;
};

export { ToolCard, CustomToolRenderer };