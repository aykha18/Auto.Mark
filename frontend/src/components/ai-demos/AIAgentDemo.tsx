import React, { useState, useEffect } from 'react';
import { Brain, Activity, Zap, TrendingUp } from 'lucide-react';

interface AIDecision {
  id: string;
  timestamp: string;
  action: string;
  impact: string;
  confidence: number;
}

const AIAgentDemo: React.FC = () => {
  const [decisions, setDecisions] = useState<AIDecision[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [metrics, setMetrics] = useState({
    decisionsPerHour: 0,
    activeOptimizations: 0,
    performanceImprovement: 0
  });

  const sampleDecisions = [
    {
      action: 'Increased Facebook ad budget by 15%',
      impact: 'Expected 23% CTR improvement',
      confidence: 94
    },
    {
      action: 'Shifted email send time to 2:30 PM',
      impact: 'Predicted 18% open rate boost',
      confidence: 87
    },
    {
      action: 'Updated landing page CTA color',
      impact: 'Forecasted 12% conversion lift',
      confidence: 91
    },
    {
      action: 'Paused underperforming Google Ads',
      impact: 'Saved $340 in wasted spend',
      confidence: 96
    },
    {
      action: 'Activated retargeting sequence',
      impact: 'Targeting 1,247 warm prospects',
      confidence: 89
    }
  ];

  useEffect(() => {
    if (isActive) {
      const interval = setInterval(() => {
        const randomDecision = sampleDecisions[Math.floor(Math.random() * sampleDecisions.length)];
        const newDecision: AIDecision = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          action: randomDecision.action,
          impact: randomDecision.impact,
          confidence: randomDecision.confidence
        };

        setDecisions(prev => [newDecision, ...prev.slice(0, 4)]);
        
        setMetrics(prev => ({
          decisionsPerHour: prev.decisionsPerHour + Math.floor(Math.random() * 50) + 25,
          activeOptimizations: Math.floor(Math.random() * 15) + 8,
          performanceImprovement: Math.min(prev.performanceImprovement + Math.random() * 2, 100)
        }));
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [isActive]);

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Brain className="w-6 h-6 text-blue-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">
            Autonomous AI Agent - Live Demo
          </h3>
        </div>
        <button
          onClick={() => setIsActive(!isActive)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isActive 
              ? 'bg-red-100 text-red-700 hover:bg-red-200' 
              : 'bg-green-100 text-green-700 hover:bg-green-200'
          }`}
        >
          {isActive ? 'Stop AI' : 'Start AI'}
        </button>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <Activity className="w-5 h-5 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-blue-600">
            {metrics.decisionsPerHour.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600">Decisions/Hour</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <Zap className="w-5 h-5 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-green-600">
            {metrics.activeOptimizations}
          </div>
          <div className="text-xs text-gray-600">Active Optimizations</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <TrendingUp className="w-5 h-5 text-purple-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-purple-600">
            +{metrics.performanceImprovement.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-600">Performance Boost</div>
        </div>
      </div>

      {/* AI Decisions Feed */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900 mb-3">Recent AI Decisions</h4>
        {decisions.length === 0 && !isActive && (
          <div className="text-center py-8 text-gray-500">
            Click "Start AI" to see autonomous decisions in real-time
          </div>
        )}
        {decisions.map((decision) => (
          <div
            key={decision.id}
            className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500 animate-fadeIn"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm font-medium text-gray-900">
                {decision.action}
              </span>
              <span className="text-xs text-gray-500">{decision.timestamp}</span>
            </div>
            <div className="text-sm text-gray-600 mb-2">{decision.impact}</div>
            <div className="flex items-center">
              <div className="text-xs text-gray-500 mr-2">Confidence:</div>
              <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${decision.confidence}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-700">
                {decision.confidence}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {isActive && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
            <span className="text-sm text-green-700 font-medium">
              AI Agent is actively monitoring and optimizing your campaigns
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAgentDemo;
