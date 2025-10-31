import React, { useState } from 'react';

interface RoadmapItem {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in_progress' | 'planned' | 'future';
  quarter: string;
  features: string[];
  impact: string;
  foundingUserInfluence?: boolean;
}

interface RoadmapPresentationProps {
  title: string;
  subtitle: string;
  roadmapItems: RoadmapItem[];
  className?: string;
}

const RoadmapPresentation: React.FC<RoadmapPresentationProps> = ({
  title,
  subtitle,
  roadmapItems,
  className = ''
}) => {
  const [selectedItem, setSelectedItem] = useState<RoadmapItem | null>(null);
  const [filter, setFilter] = useState<'all' | 'completed' | 'in_progress' | 'planned'>('all');

  const filteredItems = roadmapItems.filter(item => 
    filter === 'all' || item.status === filter
  );

  const getStatusColor = (status: RoadmapItem['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'planned':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'future':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: RoadmapItem['status']) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '🚧';
      case 'planned':
        return '📋';
      case 'future':
        return '🔮';
      default:
        return '❓';
    }
  };

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 mb-4">{subtitle}</p>
        
        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-2">
          {[
            { key: 'all', label: 'All Items' },
            { key: 'completed', label: 'Completed' },
            { key: 'in_progress', label: 'In Progress' },
            { key: 'planned', label: 'Planned' }
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {/* Roadmap Timeline */}
        <div className="space-y-6">
          {filteredItems.map((item, index) => (
            <div key={item.id} className="relative">
              {/* Timeline Line */}
              {index < filteredItems.length - 1 && (
                <div className="absolute left-6 top-12 w-0.5 h-16 bg-gray-300" />
              )}
              
              <div className="flex items-start space-x-4">
                {/* Status Icon */}
                <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center text-lg ${getStatusColor(item.status)}`}>
                  {getStatusIcon(item.status)}
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-lg font-semibold text-gray-900">
                        {item.title}
                      </h4>
                      <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {item.quarter}
                      </span>
                      {item.foundingUserInfluence && (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                          👥 Co-Creator Input
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => setSelectedItem(selectedItem?.id === item.id ? null : item)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      {selectedItem?.id === item.id ? 'Hide Details' : 'View Details'}
                    </button>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{item.description}</p>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Impact: {item.impact}</span>
                    <span>•</span>
                    <span>{item.features.length} features</span>
                  </div>

                  {/* Expanded Details */}
                  {selectedItem?.id === item.id && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-3">Key Features:</h5>
                      <ul className="space-y-2">
                        {item.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-start space-x-2">
                            <span className="text-blue-600 mt-1">•</span>
                            <span className="text-gray-700">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      
                      {item.foundingUserInfluence && (
                        <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="text-purple-600">👥</span>
                            <span className="font-medium text-purple-800">Co-Creator Influence</span>
                          </div>
                          <p className="text-sm text-purple-700">
                            This roadmap item can be influenced by our founding co-creators through 
                            feature voting and direct feedback sessions.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="mt-8 pt-6 border-t">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Completed', count: roadmapItems.filter(i => i.status === 'completed').length, color: 'text-green-600' },
              { label: 'In Progress', count: roadmapItems.filter(i => i.status === 'in_progress').length, color: 'text-blue-600' },
              { label: 'Planned', count: roadmapItems.filter(i => i.status === 'planned').length, color: 'text-yellow-600' },
              { label: 'Future', count: roadmapItems.filter(i => i.status === 'future').length, color: 'text-gray-600' }
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className={`text-2xl font-bold ${stat.color}`}>{stat.count}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoadmapPresentation;
