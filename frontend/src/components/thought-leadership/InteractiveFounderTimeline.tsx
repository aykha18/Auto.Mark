import React, { useState, useEffect } from 'react';
import { FounderMilestone } from '../../types';

interface InteractiveFounderTimelineProps {
  milestones: FounderMilestone[];
  className?: string;
}

const InteractiveFounderTimeline: React.FC<InteractiveFounderTimelineProps> = ({
  milestones,
  className = ''
}) => {
  const [selectedMilestone, setSelectedMilestone] = useState<FounderMilestone | null>(null);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Sort milestones by date
  const sortedMilestones = [...milestones].sort((a, b) => a.date.getTime() - b.date.getTime());

  useEffect(() => {
    if (isAutoPlaying) {
      const interval = setInterval(() => {
        setCurrentIndex(prev => {
          const nextIndex = (prev + 1) % sortedMilestones.length;
          setSelectedMilestone(sortedMilestones[nextIndex]);
          return nextIndex;
        });
      }, 4000);

      return () => clearInterval(interval);
    }
  }, [isAutoPlaying, sortedMilestones]);

  const handleMilestoneClick = (milestone: FounderMilestone, index: number) => {
    setSelectedMilestone(milestone);
    setCurrentIndex(index);
    setIsAutoPlaying(false);
  };

  const toggleAutoPlay = () => {
    setIsAutoPlaying(!isAutoPlaying);
    if (!isAutoPlaying && !selectedMilestone) {
      setSelectedMilestone(sortedMilestones[0]);
      setCurrentIndex(0);
    }
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long' 
    });
  };

  const getMetricIcon = (metricKey: string) => {
    switch (metricKey) {
      case 'leadsGenerated': return '🎯';
      case 'crmIntegrations': return '🔗';
      case 'automationLevel': return '⚡';
      case 'timesSaved': return '⏰';
      default: return '📊';
    }
  };

  const formatMetricValue = (key: string, value: number) => {
    switch (key) {
      case 'leadsGenerated':
        return `${value.toLocaleString()} leads`;
      case 'crmIntegrations':
        return `${value} CRM${value !== 1 ? 's' : ''}`;
      case 'automationLevel':
        return `${value}% automated`;
      case 'timesSaved':
        return `${value}x faster`;
      default:
        return value.toString();
    }
  };

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Founder's Journey</h3>
            <p className="text-gray-600">From disconnected tools to unified automation</p>
          </div>
          <button
            onClick={toggleAutoPlay}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isAutoPlaying
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              {isAutoPlaying ? (
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              ) : (
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              )}
            </svg>
            <span>{isAutoPlaying ? 'Pause' : 'Auto Play'}</span>
          </button>
        </div>

        {/* Timeline Navigation */}
        <div className="relative">
          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            {sortedMilestones.map((milestone, index) => (
              <button
                key={milestone.id}
                onClick={() => handleMilestoneClick(milestone, index)}
                className={`flex-shrink-0 relative p-3 rounded-lg border-2 transition-all ${
                  selectedMilestone?.id === milestone.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                } ${isAutoPlaying && currentIndex === index ? 'ring-2 ring-blue-300' : ''}`}
              >
                <div className="text-center">
                  <div className="text-xs font-medium text-gray-600 mb-1">
                    {formatDate(milestone.date)}
                  </div>
                  <div className="text-sm font-semibold text-gray-900 truncate max-w-24">
                    {milestone.title}
                  </div>
                </div>
                
                {/* Connection Line */}
                {index < sortedMilestones.length - 1 && (
                  <div className="absolute top-1/2 -right-2 w-4 h-0.5 bg-gray-300 transform -translate-y-1/2" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-6">
        {selectedMilestone ? (
          <div className="space-y-6">
            {/* Milestone Header */}
            <div className="text-center">
              <h4 className="text-xl font-bold text-gray-900 mb-2">
                {selectedMilestone.title}
              </h4>
              <p className="text-gray-600 mb-4">{selectedMilestone.description}</p>
              <div className="text-sm text-blue-600 font-medium">
                {formatDate(selectedMilestone.date)}
              </div>
            </div>

            {/* Metrics Grid */}
            {Object.keys(selectedMilestone.metrics).length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(selectedMilestone.metrics).map(([key, value]) => (
                  value !== undefined && (
                    <div key={key} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 text-center">
                      <div className="text-2xl mb-2">{getMetricIcon(key)}</div>
                      <div className="text-lg font-bold text-gray-900 mb-1">
                        {formatMetricValue(key, value)}
                      </div>
                      <div className="text-xs text-gray-600 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                      </div>
                    </div>
                  )
                ))}
              </div>
            )}

            {/* Technologies Used */}
            {selectedMilestone.technologies.length > 0 && (
              <div>
                <h5 className="font-semibold text-gray-900 mb-3">Technologies & Tools</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedMilestone.technologies.map((tech, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Integration Challenges */}
            {selectedMilestone.integrationChallenges.length > 0 && (
              <div>
                <h5 className="font-semibold text-gray-900 mb-3">Integration Challenges Overcome</h5>
                <div className="space-y-2">
                  {selectedMilestone.integrationChallenges.map((challenge, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                      <span className="text-yellow-600 mt-0.5">⚠️</span>
                      <span className="text-gray-700 text-sm">{challenge}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Lesson Learned */}
            <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg">
              <div className="flex items-start space-x-3">
                <span className="text-green-600 text-lg">💡</span>
                <div>
                  <h5 className="font-semibold text-green-900 mb-2">Key Lesson Learned</h5>
                  <p className="text-green-800 text-sm">{selectedMilestone.lessonLearned}</p>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between items-center pt-4 border-t">
              <button
                onClick={() => {
                  const prevIndex = currentIndex > 0 ? currentIndex - 1 : sortedMilestones.length - 1;
                  handleMilestoneClick(sortedMilestones[prevIndex], prevIndex);
                }}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Previous</span>
              </button>

              <div className="text-sm text-gray-500">
                {currentIndex + 1} of {sortedMilestones.length}
              </div>

              <button
                onClick={() => {
                  const nextIndex = currentIndex < sortedMilestones.length - 1 ? currentIndex + 1 : 0;
                  handleMilestoneClick(sortedMilestones[nextIndex], nextIndex);
                }}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-medium"
              >
                <span>Next</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🚀</span>
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Explore the Journey
            </h4>
            <p className="text-gray-600 mb-4">
              Click on any milestone above to see the detailed story of how Auto.Mark evolved.
            </p>
            <button
              onClick={() => handleMilestoneClick(sortedMilestones[0], 0)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Start from Beginning
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractiveFounderTimeline;