import React, { useState, useEffect } from 'react';

interface Milestone {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in_progress' | 'upcoming';
  completedDate?: Date;
  estimatedDate?: Date;
  progress: number; // 0-100
  category: 'backend' | 'frontend' | 'integration' | 'testing' | 'deployment';
  blockers?: string[];
  dependencies?: string[];
}

interface DevelopmentUpdate {
  id: string;
  date: Date;
  title: string;
  description: string;
  type: 'feature' | 'bugfix' | 'improvement' | 'milestone';
  impact: 'low' | 'medium' | 'high';
}

interface DevelopmentStatusTrackerProps {
  milestones: Milestone[];
  recentUpdates: DevelopmentUpdate[];
  className?: string;
}

const DevelopmentStatusTracker: React.FC<DevelopmentStatusTrackerProps> = ({
  milestones,
  recentUpdates,
  className = ''
}) => {
  const [activeView, setActiveView] = useState<'milestones' | 'updates'>('milestones');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000); // Update every minute
    return () => clearInterval(timer);
  }, []);

  const categories = [
    { key: 'all', label: 'All', icon: '🔄' },
    { key: 'backend', label: 'Backend', icon: '⚙️' },
    { key: 'frontend', label: 'Frontend', icon: '🎨' },
    { key: 'integration', label: 'Integration', icon: '🔗' },
    { key: 'testing', label: 'Testing', icon: '🧪' },
    { key: 'deployment', label: 'Deployment', icon: '🚀' }
  ];

  const filteredMilestones = milestones.filter(milestone => 
    selectedCategory === 'all' || milestone.category === selectedCategory
  );

  const getStatusColor = (status: Milestone['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'in_progress':
        return 'text-blue-600 bg-blue-100';
      case 'upcoming':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getUpdateTypeColor = (type: DevelopmentUpdate['type']) => {
    switch (type) {
      case 'feature':
        return 'text-blue-600 bg-blue-100';
      case 'bugfix':
        return 'text-red-600 bg-red-100';
      case 'improvement':
        return 'text-green-600 bg-green-100';
      case 'milestone':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatRelativeTime = (date: Date) => {
    const now = currentTime.getTime();
    const targetTime = date.getTime();
    const diffInHours = Math.abs(now - targetTime) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else if (diffInHours < 168) { // 7 days
      return `${Math.floor(diffInHours / 24)} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const overallProgress = Math.round(
    milestones.reduce((sum, milestone) => sum + milestone.progress, 0) / milestones.length
  );

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Development Status</h3>
            <p className="text-gray-600">Real-time transparency into our progress</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">{overallProgress}%</div>
            <div className="text-sm text-gray-600">Overall Progress</div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { key: 'milestones', label: 'Milestones', icon: '🎯' },
            { key: 'updates', label: 'Recent Updates', icon: '📝' }
          ].map((view) => (
            <button
              key={view.key}
              onClick={() => setActiveView(view.key as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeView === view.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>{view.icon}</span>
              <span>{view.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {activeView === 'milestones' && (
          <div className="space-y-6">
            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.key}
                  onClick={() => setSelectedCategory(category.key)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span>{category.icon}</span>
                  <span>{category.label}</span>
                </button>
              ))}
            </div>

            {/* Milestones List */}
            <div className="space-y-4">
              {filteredMilestones.map((milestone) => (
                <div key={milestone.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-semibold text-gray-900">{milestone.title}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(milestone.status)}`}>
                          {milestone.status.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {milestone.category}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm">{milestone.description}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-lg font-bold text-blue-600">{milestone.progress}%</div>
                      {milestone.estimatedDate && (
                        <div className="text-xs text-gray-500">
                          ETA: {milestone.estimatedDate.toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${milestone.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Blockers and Dependencies */}
                  {(milestone.blockers?.length || milestone.dependencies?.length) && (
                    <div className="space-y-2">
                      {milestone.blockers && milestone.blockers.length > 0 && (
                        <div>
                          <span className="text-xs font-medium text-red-600">Blockers:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {milestone.blockers.map((blocker, index) => (
                              <span key={index} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                                {blocker}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {milestone.dependencies && milestone.dependencies.length > 0 && (
                        <div>
                          <span className="text-xs font-medium text-yellow-600">Dependencies:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {milestone.dependencies.map((dependency, index) => (
                              <span key={index} className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                                {dependency}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'updates' && (
          <div className="space-y-4">
            {recentUpdates.map((update) => (
              <div key={update.id} className="border-l-4 border-blue-400 pl-4 py-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <h4 className="font-semibold text-gray-900">{update.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUpdateTypeColor(update.type)}`}>
                      {update.type}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      update.impact === 'high' ? 'bg-red-100 text-red-700' :
                      update.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {update.impact} impact
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {formatRelativeTime(update.date)}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{update.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DevelopmentStatusTracker;
