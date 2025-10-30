import React from 'react';
import { CRMAssessmentResult } from '../../types';
import { TrendingUp, Target, Zap, Clock, DollarSign, Users } from 'lucide-react';

interface ResultsSummaryCardProps {
  result: CRMAssessmentResult;
}

const ResultsSummaryCard: React.FC<ResultsSummaryCardProps> = ({ result }) => {
  // Normalize property names to handle both camelCase and snake_case
  const normalizedResult = {
    currentCRM: result.currentCRM || (result as any).current_crm || 'Unknown',
    integrationScore: result.integrationScore || (result as any).overall_score || 0,
    readinessLevel: result.readinessLevel || (result as any).readiness_level || 'nurture_with_guides',
    automationOpportunities: result.automationOpportunities || (result as any).automation_opportunities || [],
    nextSteps: result.nextSteps || (result as any).next_steps || []
  };

  const getReadinessColor = () => {
    switch (normalizedResult.readinessLevel) {
      case 'priority_integration': return 'text-green-600 bg-green-50 border-green-200';
      case 'co_creator_qualified': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'nurture_with_guides': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getReadinessIcon = () => {
    switch (normalizedResult.readinessLevel) {
      case 'priority_integration': return <Zap className="w-5 h-5" />;
      case 'co_creator_qualified': return <Target className="w-5 h-5" />;
      case 'nurture_with_guides': return <TrendingUp className="w-5 h-5" />;
      default: return <Target className="w-5 h-5" />;
    }
  };

  const getReadinessTitle = () => {
    switch (normalizedResult.readinessLevel) {
      case 'priority_integration': return 'Priority Integration Ready';
      case 'co_creator_qualified': return 'Co-Creator Qualified';
      case 'nurture_with_guides': return 'Foundation Building';
      default: return 'Assessment Complete';
    }
  };

  const getEstimatedValue = () => {
    const baseValue = normalizedResult.integrationScore * 50; // $50 per point
    return Math.round(baseValue);
  };

  const getTimeToValue = () => {
    switch (normalizedResult.readinessLevel) {
      case 'priority_integration': return '1-2 weeks';
      case 'co_creator_qualified': return '2-4 weeks';
      case 'nurture_with_guides': return '4-8 weeks';
      default: return '4-6 weeks';
    }
  };

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Assessment Summary</h3>
        <div className={`inline-flex items-center px-3 py-1 rounded-full border ${getReadinessColor()}`}>
          {getReadinessIcon()}
          <span className="font-medium ml-2 text-sm">{getReadinessTitle()}</span>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-white rounded-lg shadow-sm">
          <div className="text-2xl font-bold text-primary-600">{normalizedResult.integrationScore}</div>
          <div className="text-xs text-gray-600">AI Readiness Score</div>
        </div>
        
        <div className="text-center p-3 bg-white rounded-lg shadow-sm">
          <div className="text-2xl font-bold text-green-600">${getEstimatedValue().toLocaleString()}</div>
          <div className="text-xs text-gray-600">Monthly Value Potential</div>
        </div>
        
        <div className="text-center p-3 bg-white rounded-lg shadow-sm">
          <div className="text-2xl font-bold text-blue-600">{normalizedResult.automationOpportunities?.length || 0}</div>
          <div className="text-xs text-gray-600">Automation Opportunities</div>
        </div>
        
        <div className="text-center p-3 bg-white rounded-lg shadow-sm">
          <div className="text-2xl font-bold text-purple-600">{getTimeToValue()}</div>
          <div className="text-xs text-gray-600">Time to Value</div>
        </div>
      </div>

      {/* Quick Insights */}
      <div className="space-y-3">
        <div className="flex items-center text-sm">
          <Target className="w-4 h-4 text-primary-600 mr-3 flex-shrink-0" />
          <span className="text-gray-700">
            <strong>Current CRM:</strong> {normalizedResult.currentCRM} - Ready for integration
          </span>
        </div>
        
        <div className="flex items-center text-sm">
          <Clock className="w-4 h-4 text-green-600 mr-3 flex-shrink-0" />
          <span className="text-gray-700">
            <strong>Time Savings:</strong> 15-25 hours/week through automation
          </span>
        </div>
        
        <div className="flex items-center text-sm">
          <DollarSign className="w-4 h-4 text-blue-600 mr-3 flex-shrink-0" />
          <span className="text-gray-700">
            <strong>ROI Potential:</strong> 250-400% within 6 months
          </span>
        </div>
        
        <div className="flex items-center text-sm">
          <Users className="w-4 h-4 text-purple-600 mr-3 flex-shrink-0" />
          <span className="text-gray-700">
            <strong>Lead Increase:</strong> 40-60% more qualified leads
          </span>
        </div>
      </div>

      {/* Next Action */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600 mb-2">Recommended Next Step:</div>
        <div className="font-medium text-gray-900">
          {normalizedResult.nextSteps?.[0] || 'Review detailed recommendations below'}
        </div>
      </div>
    </div>
  );
};

export default ResultsSummaryCard;