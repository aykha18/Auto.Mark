import React from 'react';
import { Clock, DollarSign, TrendingUp, Zap, ArrowRight } from 'lucide-react';
import Button from '../ui/Button';

interface AutomationOpportunity {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  timesSaved: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedROI: string;
  category: 'lead_generation' | 'nurturing' | 'conversion' | 'retention';
}

interface AutomationOpportunityCardProps {
  opportunities: string[];
  currentCRM: string;
  readinessLevel: string;
}

const AutomationOpportunityCard: React.FC<AutomationOpportunityCardProps> = ({
  opportunities,
  currentCRM,
  readinessLevel,
}) => {
  const getEnhancedOpportunities = (): AutomationOpportunity[] => {
    return opportunities.map((opportunity, index) => {
      // Enhanced opportunity data based on the text
      const enhancedOpportunities: Record<string, Partial<AutomationOpportunity>> = {
        'lead scoring': {
          title: 'AI-Powered Lead Scoring',
          description: 'Automatically score and prioritize leads based on behavior and engagement',
          impact: 'high',
          timesSaved: '10-15 hours/week',
          difficulty: 'easy',
          estimatedROI: '300-400%',
          category: 'lead_generation'
        },
        'email automation': {
          title: 'Intelligent Email Sequences',
          description: 'Personalized email campaigns triggered by lead behavior and CRM data',
          impact: 'high',
          timesSaved: '8-12 hours/week',
          difficulty: 'medium',
          estimatedROI: '250-350%',
          category: 'nurturing'
        },
        'follow-up automation': {
          title: 'Smart Follow-up Automation',
          description: 'Automated follow-up sequences based on lead engagement and CRM status',
          impact: 'medium',
          timesSaved: '6-10 hours/week',
          difficulty: 'easy',
          estimatedROI: '200-300%',
          category: 'nurturing'
        },
        'data enrichment': {
          title: 'Automated Data Enrichment',
          description: 'Automatically enrich lead profiles with social and company data',
          impact: 'medium',
          timesSaved: '4-8 hours/week',
          difficulty: 'medium',
          estimatedROI: '150-250%',
          category: 'lead_generation'
        },
        'pipeline management': {
          title: 'Intelligent Pipeline Management',
          description: 'Automated deal progression and stage updates based on activities',
          impact: 'high',
          timesSaved: '5-8 hours/week',
          difficulty: 'medium',
          estimatedROI: '200-300%',
          category: 'conversion'
        }
      };

      // Find matching enhanced opportunity or create default
      const matchingKey = Object.keys(enhancedOpportunities).find(key => 
        opportunity.toLowerCase().includes(key)
      );

      const enhanced = matchingKey ? enhancedOpportunities[matchingKey] : {};

      return {
        title: enhanced.title || opportunity,
        description: enhanced.description || `Implement ${opportunity} to improve efficiency`,
        impact: enhanced.impact || 'medium',
        timesSaved: enhanced.timesSaved || '3-5 hours/week',
        difficulty: enhanced.difficulty || 'medium',
        estimatedROI: enhanced.estimatedROI || '150-200%',
        category: enhanced.category || 'lead_generation'
      } as AutomationOpportunity;
    });
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'hard': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'lead_generation': return <TrendingUp className="w-5 h-5" />;
      case 'nurturing': return <Zap className="w-5 h-5" />;
      case 'conversion': return <DollarSign className="w-5 h-5" />;
      case 'retention': return <Clock className="w-5 h-5" />;
      default: return <Zap className="w-5 h-5" />;
    }
  };

  const enhancedOpportunities = getEnhancedOpportunities();

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <Zap className="w-6 h-6 text-primary-600 mr-3" />
        <h3 className="text-xl font-bold text-gray-900">Automation Opportunities</h3>
        <div className="ml-auto text-sm text-gray-500">
          {enhancedOpportunities.length} opportunities identified
        </div>
      </div>

      <div className="space-y-4">
        {enhancedOpportunities.map((opportunity, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center">
                <div className="text-primary-600 mr-3">
                  {getCategoryIcon(opportunity.category)}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{opportunity.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{opportunity.description}</p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getImpactColor(opportunity.impact)}`}>
                {opportunity.impact.toUpperCase()} IMPACT
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="flex items-center text-sm">
                <Clock className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">Saves: </span>
                <span className="font-medium ml-1">{opportunity.timesSaved}</span>
              </div>
              
              <div className="flex items-center text-sm">
                <DollarSign className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">ROI: </span>
                <span className="font-medium ml-1">{opportunity.estimatedROI}</span>
              </div>
              
              <div className="flex items-center text-sm">
                <span className="text-gray-600">Difficulty: </span>
                <span className={`font-medium ml-1 ${getDifficultyColor(opportunity.difficulty)}`}>
                  {opportunity.difficulty.charAt(0).toUpperCase() + opportunity.difficulty.slice(1)}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500 capitalize">
                {opportunity.category.replace('_', ' ')} automation
              </div>
              <Button
                variant="ghost"
                size="sm"
                icon={ArrowRight}
                iconPosition="right"
                className="text-primary-600 hover:text-primary-700"
              >
                Learn More
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Card */}
      <div className="mt-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg border border-primary-100">
        <h4 className="font-semibold text-gray-900 mb-2">Total Automation Potential</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-600">
              {enhancedOpportunities.reduce((total, opp) => {
                const hours = parseInt(opp.timesSaved.split('-')[0]);
                return total + hours;
              }, 0)}+
            </div>
            <div className="text-sm text-gray-600">Hours Saved/Week</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {enhancedOpportunities.length > 0 ? Math.round(enhancedOpportunities.reduce((total, opp) => {
                const roi = parseInt(opp.estimatedROI.split('-')[0]);
                return total + roi;
              }, 0) / enhancedOpportunities.length) : 0}%
            </div>
            <div className="text-sm text-gray-600">Average ROI</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">
              {enhancedOpportunities.filter(opp => opp.difficulty === 'easy').length}
            </div>
            <div className="text-sm text-gray-600">Quick Wins</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationOpportunityCard;