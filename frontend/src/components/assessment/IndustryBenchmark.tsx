import React from 'react';
import { TrendingUp, Users, Award, Target } from 'lucide-react';

interface IndustryBenchmarkProps {
  score: number;
  currentCRM: string;
  readinessLevel: string;
}

const IndustryBenchmark: React.FC<IndustryBenchmarkProps> = ({
  score,
  currentCRM,
  readinessLevel,
}) => {
  const getBenchmarkData = () => {
    return {
      industryAverage: 45,
      topPerformers: 78,
      crmSpecificAverage: getCRMSpecificAverage(),
      yourPercentile: calculatePercentile(score),
    };
  };

  const getCRMSpecificAverage = () => {
    const crmAverages: Record<string, number> = {
      'HubSpot': 52,
      'Salesforce': 58,
      'Pipedrive': 48,
      'Zoho': 46,
      'Monday': 44,
    };
    return crmAverages[currentCRM] || 45;
  };

  const calculatePercentile = (userScore: number) => {
    // Simulate percentile calculation based on score
    if (userScore >= 80) return 95;
    if (userScore >= 70) return 85;
    if (userScore >= 60) return 70;
    if (userScore >= 50) return 55;
    if (userScore >= 40) return 40;
    return 25;
  };

  const getComparisonMessage = () => {
    const benchmark = getBenchmarkData();
    const diff = score - benchmark.industryAverage;
    
    if (diff > 20) {
      return `Exceptional! You're ${diff} points above industry average and in the top 15% of businesses.`;
    } else if (diff > 0) {
      return `Great job! You're ${diff} points above the industry average of ${benchmark.industryAverage}.`;
    } else if (diff > -10) {
      return `You're close to industry average (${benchmark.industryAverage}). Small improvements will make a big difference.`;
    } else {
      return `There's room for improvement. Focus on the recommendations to reach industry standards.`;
    }
  };

  const benchmark = getBenchmarkData();

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <TrendingUp className="w-6 h-6 text-primary-600 mr-3" />
        <h3 className="text-xl font-bold text-gray-900">Industry Benchmark Comparison</h3>
      </div>

      {/* Comparison Message */}
      <div className="mb-6 p-4 bg-primary-50 rounded-lg border border-primary-100">
        <p className="text-primary-800 font-medium">{getComparisonMessage()}</p>
      </div>

      {/* Benchmark Visualization */}
      <div className="space-y-6">
        {/* Your Score vs Industry */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Your Score</span>
            <span className="text-lg font-bold text-primary-600">{score}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-primary-600 h-3 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${score}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Industry Average</span>
            <span className="text-lg font-bold text-gray-600">{benchmark.industryAverage}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gray-400 h-3 rounded-full"
              style={{ width: `${benchmark.industryAverage}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">{currentCRM} Users Average</span>
            <span className="text-lg font-bold text-blue-600">{benchmark.crmSpecificAverage}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-500 h-3 rounded-full"
              style={{ width: `${benchmark.crmSpecificAverage}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Top Performers</span>
            <span className="text-lg font-bold text-green-600">{benchmark.topPerformers}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-green-500 h-3 rounded-full"
              style={{ width: `${benchmark.topPerformers}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <Users className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{benchmark.yourPercentile}th</div>
          <div className="text-sm text-gray-600">Percentile</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <Target className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {benchmark.topPerformers - score > 0 ? `+${benchmark.topPerformers - score}` : '✓'}
          </div>
          <div className="text-sm text-gray-600">
            {benchmark.topPerformers - score > 0 ? 'Points to Top 15%' : 'Top Performer'}
          </div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <Award className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {readinessLevel === 'priority_integration' ? 'Elite' : 
             readinessLevel === 'co_creator_qualified' ? 'Advanced' : 'Growing'}
          </div>
          <div className="text-sm text-gray-600">Readiness Tier</div>
        </div>
      </div>

      {/* Improvement Potential */}
      <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
        <h4 className="font-semibold text-gray-900 mb-2">Improvement Potential</h4>
        <p className="text-sm text-gray-700">
          {score < benchmark.topPerformers ? (
            `Reaching top performer level (${benchmark.topPerformers}) could increase your lead generation by 40-60% and save 20+ hours per week through automation.`
          ) : (
            'You\'re already performing at an elite level! Focus on maintaining your competitive advantage and exploring advanced automation features.'
          )}
        </p>
      </div>
    </div>
  );
};

export default IndustryBenchmark;
