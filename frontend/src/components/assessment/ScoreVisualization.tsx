import React from 'react';
import { TrendingUp, Target, Zap } from 'lucide-react';

interface ScoreVisualizationProps {
  score: number;
  readinessLevel: string;
  currentCRM: string;
}

const ScoreVisualization: React.FC<ScoreVisualizationProps> = ({
  score,
  readinessLevel,
  currentCRM,
}) => {
  const getScoreColor = () => {
    if (score >= 71) return 'text-green-600';
    if (score >= 41) return 'text-blue-600';
    return 'text-yellow-600';
  };

  const getScoreGradient = () => {
    if (score >= 71) return { from: '#10b981', to: '#059669' }; // green
    if (score >= 41) return { from: '#3b82f6', to: '#2563eb' }; // blue
    return { from: '#f59e0b', to: '#d97706' }; // yellow
  };

  const getScoreIcon = () => {
    if (score >= 71) return <Zap className="w-8 h-8 text-green-600" />;
    if (score >= 41) return <Target className="w-8 h-8 text-blue-600" />;
    return <TrendingUp className="w-8 h-8 text-yellow-600" />;
  };

  const getScoreDescription = () => {
    if (score >= 71) return 'Excellent! You\'re ready for advanced AI automation with predictive insights';
    if (score >= 41) return 'Good foundation! Ready for structured automation with optimization';
    return 'Building phase! Let\'s strengthen your automation foundation step by step';
  };

  const getScoreBreakdown = () => {
    // Simulate score breakdown based on categories
    const breakdown = [
      { category: 'CRM Data Quality', score: Math.min(100, score + Math.random() * 20 - 10) },
      { category: 'Integration Readiness', score: Math.min(100, score + Math.random() * 15 - 7) },
      { category: 'Automation Maturity', score: Math.min(100, score + Math.random() * 25 - 12) },
      { category: 'Technical Setup', score: Math.min(100, score + Math.random() * 18 - 9) }
    ];
    return breakdown.map(item => ({ ...item, score: Math.max(0, Math.round(item.score)) }));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Your AI Readiness Score
        </h2>
        
        {/* Score Circle */}
        <div className="relative inline-flex items-center justify-center">
          <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background Circle */}
            <circle
              cx="50"
              cy="50"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-200"
            />
            {/* Progress Circle */}
            <circle
              cx="50"
              cy="50"
              r="40"
              stroke="url(#scoreGradient)"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 40}`}
              strokeDashoffset={`${2 * Math.PI * 40 * (1 - score / 100)}`}
              className="transition-all duration-1000 ease-out"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={getScoreGradient().from} />
                <stop offset="100%" stopColor={getScoreGradient().to} />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Score Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {getScoreIcon()}
            <span className={`text-4xl font-bold ${getScoreColor()} mt-2`}>
              {score}
            </span>
            <span className="text-gray-600 text-sm">out of 100</span>
          </div>
        </div>

        <p className="text-lg text-gray-700 mt-4">
          {getScoreDescription()}
        </p>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{currentCRM}</div>
          <div className="text-sm text-gray-600">Current CRM</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className={`text-2xl font-bold ${getScoreColor()}`}>
            {readinessLevel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </div>
          <div className="text-sm text-gray-600">Readiness Level</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">
            {score >= 71 ? 'High' : score >= 41 ? 'Medium' : 'Building'}
          </div>
          <div className="text-sm text-gray-600">Priority Level</div>
        </div>
      </div>

      {/* Detailed Score Breakdown */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900 text-center">Score Breakdown by Category</h4>
        {getScoreBreakdown().map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 w-1/3">{item.category}</span>
            <div className="flex-1 mx-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-1000 ease-out ${
                    item.score >= 71 ? 'bg-green-500' : item.score >= 41 ? 'bg-blue-500' : 'bg-yellow-500'
                  }`}
                  style={{ width: `${item.score}%` }}
                ></div>
              </div>
            </div>
            <span className={`text-sm font-bold w-12 text-right ${
              item.score >= 71 ? 'text-green-600' : item.score >= 41 ? 'text-blue-600' : 'text-yellow-600'
            }`}>
              {item.score}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScoreVisualization;