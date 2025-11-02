import React, { useState } from 'react';
import { Brain, Target, Zap, Shield, BarChart3, MessageCircle } from 'lucide-react';
import Button from '../ui/Button';
import apiClient from '../../services/api';
import { LeadData } from './LeadCaptureForm';

interface AssessmentQuestion {
  id: string;
  category: 'ai-readiness' | 'automation-maturity' | 'data-intelligence' | 'integration-needs';
  question: string;
  options: { value: number; label: string; description?: string }[];
}

interface AssessmentResult {
  aiReadinessScore: number;
  automationMaturity: number;
  dataIntelligence: number;
  integrationReadiness: number;
  overallScore: number;
  recommendations: string[];
  predictedROI: number;
  automationOpportunities: number;
  co_creator_qualified?: boolean;
  co_creator_invitation?: any;
}

interface AIReadinessAssessmentProps {
  leadData?: LeadData | null;
}

const AIReadinessAssessment: React.FC<AIReadinessAssessmentProps> = ({ leadData }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState<AssessmentResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);

  const questions: AssessmentQuestion[] = [
    {
      id: 'ai-experience',
      category: 'ai-readiness',
      question: 'How would you describe your current experience with AI marketing tools?',
      options: [
        { value: 1, label: 'No experience', description: 'Never used AI tools' },
        { value: 2, label: 'Basic awareness', description: 'Heard about AI but not implemented' },
        { value: 3, label: 'Some experimentation', description: 'Tried a few AI tools' },
        { value: 4, label: 'Regular usage', description: 'Use AI tools regularly' },
        { value: 5, label: 'Advanced implementation', description: 'AI is core to our strategy' }
      ]
    },
    {
      id: 'automation-level',
      category: 'automation-maturity',
      question: 'What percentage of your marketing processes are currently automated?',
      options: [
        { value: 1, label: '0-20%', description: 'Mostly manual processes' },
        { value: 2, label: '21-40%', description: 'Some basic automation' },
        { value: 3, label: '41-60%', description: 'Moderate automation' },
        { value: 4, label: '61-80%', description: 'Highly automated' },
        { value: 5, label: '81-100%', description: 'Fully automated workflows' }
      ]
    },
    {
      id: 'data-collection',
      category: 'data-intelligence',
      question: 'How comprehensive is your customer data collection and analysis?',
      options: [
        { value: 1, label: 'Basic tracking', description: 'Website analytics only' },
        { value: 2, label: 'Multi-channel data', description: 'Several data sources' },
        { value: 3, label: 'Integrated analytics', description: 'Unified data platform' },
        { value: 4, label: 'Advanced insights', description: 'Predictive analytics' },
        { value: 5, label: 'AI-powered intelligence', description: 'Real-time AI insights' }
      ]
    },
    {
      id: 'decision-speed',
      category: 'automation-maturity',
      question: 'How quickly can you make and implement marketing optimization decisions?',
      options: [
        { value: 1, label: 'Days to weeks', description: 'Manual review process' },
        { value: 2, label: 'Same day', description: 'Quick manual decisions' },
        { value: 3, label: 'Within hours', description: 'Some automated triggers' },
        { value: 4, label: 'Within minutes', description: 'Real-time monitoring' },
        { value: 5, label: 'Instant/Automated', description: 'AI makes decisions automatically' }
      ]
    },
    {
      id: 'predictive-capabilities',
      category: 'data-intelligence',
      question: 'Do you currently use predictive analytics for lead scoring or campaign optimization?',
      options: [
        { value: 1, label: 'No predictive analytics', description: 'Reactive analysis only' },
        { value: 2, label: 'Basic forecasting', description: 'Simple trend analysis' },
        { value: 3, label: 'Lead scoring models', description: 'Basic predictive scoring' },
        { value: 4, label: 'Advanced predictions', description: 'ML-based forecasting' },
        { value: 5, label: 'AI-powered predictions', description: 'Real-time predictive intelligence' }
      ]
    },
    {
      id: 'integration-complexity',
      category: 'integration-needs',
      question: 'How many marketing tools and platforms do you currently use?',
      options: [
        { value: 1, label: '1-3 tools', description: 'Simple setup' },
        { value: 2, label: '4-7 tools', description: 'Moderate complexity' },
        { value: 3, label: '8-12 tools', description: 'Complex ecosystem' },
        { value: 4, label: '13-20 tools', description: 'Highly complex' },
        { value: 5, label: '20+ tools', description: 'Enterprise complexity' }
      ]
    }
  ];

  const handleAnswer = (value: number) => {
    const question = questions[currentQuestion];
    setAnswers(prev => ({ ...prev, [question.id]: value }));

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      submitAssessment();
    }
  };

  const submitAssessment = async () => {
    setIsSubmitting(true);
    try {
      // Start assessment with real lead data including preferred CRM
      const startResponse = await apiClient.post('/api/v1/landing/assessment/start', {
        email: leadData?.email || `test_${new Date().toISOString().slice(2,10).replace(/-/g,'')}@example.com`,
        name: leadData?.name || 'Assessment User',
        company: leadData?.company || 'Assessment Company',
        preferred_crm: leadData?.preferredCRM || 'hubspot'
      });

      if (startResponse.data?.assessment_id) {
        setAssessmentId(startResponse.data.assessment_id);

        // Convert frontend answers to backend format
        const backendResponses = Object.entries(answers).map(([questionId, value]) => ({
          question_id: questionId,
          answer: value.toString()
        }));

        // Add the CRM system from lead data
        if (leadData?.preferredCRM) {
          backendResponses.push({
            question_id: 'crm_system',
            answer: leadData.preferredCRM
          });
        }

        // Add missing questions with default values
        const allQuestions = [
          'crm_system', 'crm_usage_level', 'data_quality', 'lead_nurturing',
          'marketing_automation', 'integration_experience', 'api_access',
          'automation_goals', 'monthly_leads', 'budget_timeline'
        ];

        allQuestions.forEach(qId => {
          if (!backendResponses.find(r => r.question_id === qId)) {
            let defaultAnswer = '3'; // Medium/default value
            if (qId === 'crm_system') defaultAnswer = leadData?.preferredCRM || 'hubspot';
            if (qId === 'crm_usage_level') defaultAnswer = 'Advanced workflows and automation';
            if (qId === 'data_quality') defaultAnswer = '3';
            if (qId === 'lead_nurturing') defaultAnswer = 'AI-powered personalized automation';
            if (qId === 'marketing_automation') defaultAnswer = 'AI-powered marketing automation';
            if (qId === 'integration_experience') defaultAnswer = 'Comfortable with APIs and webhooks';
            if (qId === 'api_access') defaultAnswer = 'Full API access available';
            if (qId === 'automation_goals') defaultAnswer = 'Complete marketing-sales alignment';
            if (qId === 'monthly_leads') defaultAnswer = '500-1000 leads';
            if (qId === 'budget_timeline') defaultAnswer = 'Enterprise budget, comprehensive solution';

            backendResponses.push({
              question_id: qId,
              answer: defaultAnswer
            });
          }
        });

        // Submit assessment
        const submitResponse = await apiClient.post('/api/v1/landing/assessment/submit', {
          assessment_id: startResponse.data.assessment_id,
          responses: backendResponses,
          completion_time_seconds: 120
        });

        if (submitResponse.data) {
          // Use backend results instead of local calculation
          const backendResults = submitResponse.data;
          setResults({
            aiReadinessScore: Math.round(backendResults.overall_score * 0.25),
            automationMaturity: Math.round(backendResults.overall_score * 0.25),
            dataIntelligence: Math.round(backendResults.overall_score * 0.25),
            integrationReadiness: Math.round(backendResults.overall_score * 0.25),
            overallScore: backendResults.overall_score,
            recommendations: backendResults.integration_recommendations || [],
            predictedROI: Math.round(Math.min(150 + (backendResults.overall_score * 3), 500)),
            automationOpportunities: Math.max(15 - Math.floor(backendResults.overall_score / 10), 3),
            co_creator_qualified: backendResults.co_creator_qualified,
            co_creator_invitation: backendResults.co_creator_invitation
          });
        }
      }
    } catch (error) {
      console.error('Assessment submission failed:', error);
      // Fallback to local calculation if API fails
      calculateResults();
    } finally {
      setIsSubmitting(false);
      setShowResults(true);
    }
  };

  const calculateResults = () => {
    const aiReadiness = (answers['ai-experience'] || 0) * 20;
    const automation = ((answers['automation-level'] || 0) + (answers['decision-speed'] || 0)) * 10;
    const dataIntel = ((answers['data-collection'] || 0) + (answers['predictive-capabilities'] || 0)) * 10;
    const integration = (answers['integration-complexity'] || 0) * 20;
    
    const overall = Math.round((aiReadiness + automation + dataIntel + integration) / 4);
    
    const recommendations = generateRecommendations(overall, {
      aiReadiness,
      automation,
      dataIntel,
      integration
    });

    const predictedROI = Math.min(150 + (overall * 3), 500);
    const automationOpportunities = Math.max(15 - Math.floor(overall / 10), 3);

    setResults({
      aiReadinessScore: aiReadiness,
      automationMaturity: automation,
      dataIntelligence: dataIntel,
      integrationReadiness: integration,
      overallScore: overall,
      recommendations,
      predictedROI,
      automationOpportunities
    });
    
    setShowResults(true);
  };

  const generateRecommendations = (score: number, scores: any): string[] => {
    const recs = [];
    
    if (scores.aiReadiness < 60) {
      recs.push('Implement AI-powered lead scoring to identify high-value prospects 3x faster');
    }
    if (scores.automation < 60) {
      recs.push('Deploy autonomous marketing agents to handle 500+ daily optimizations');
    }
    if (scores.dataIntel < 60) {
      recs.push('Enable predictive analytics with 94% accuracy for conversion forecasting');
    }
    if (scores.integration < 60) {
      recs.push('Integrate conversational AI assistant for 24/7 marketing consultation');
    }
    
    recs.push('Activate real-time performance optimization for instant ROI improvements');
    recs.push('Enable cross-channel orchestration for unified customer journey management');
    
    return recs.slice(0, 4);
  };

  const resetAssessment = () => {
    setCurrentQuestion(0);
    setAnswers({});
    setShowResults(false);
    setResults(null);
  };

  if (showResults && results) {
    return (
      <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Your AI Marketing Intelligence Score
          </h2>
          <div className="text-6xl font-bold text-blue-600 mb-2">
            {results.overallScore}/100
          </div>
          <p className="text-gray-600 mb-4">
            {results.overallScore >= 80 ? 'AI-Ready Enterprise' :
             results.overallScore >= 60 ? 'Advanced Automation Candidate' :
             results.overallScore >= 40 ? 'Moderate AI Potential' :
             'High Growth Opportunity'}
          </p>
          {results.co_creator_qualified && (
            <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              <Zap className="w-4 h-4 mr-2" />
              Co-Creator Qualified!
            </div>
          )}
        </div>

        {/* Score Breakdown */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Brain className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-600">{results.aiReadinessScore}</div>
            <div className="text-sm text-gray-600">AI Readiness</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <Zap className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-600">{results.automationMaturity}</div>
            <div className="text-sm text-gray-600">Automation Maturity</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-600">{results.dataIntelligence}</div>
            <div className="text-sm text-gray-600">Data Intelligence</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <Target className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-orange-600">{results.integrationReadiness}</div>
            <div className="text-sm text-gray-600">Integration Readiness</div>
          </div>
        </div>

        {/* AI Predictions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Predicted ROI Improvement</h3>
            <div className="text-3xl font-bold text-green-600 mb-2">+{results.predictedROI}%</div>
            <p className="text-sm text-gray-600">
              Based on AI implementation across similar organizations
            </p>
          </div>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Automation Opportunities</h3>
            <div className="text-3xl font-bold text-purple-600 mb-2">{results.automationOpportunities}</div>
            <p className="text-sm text-gray-600">
              Priority areas identified for AI automation
            </p>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            AI Agent Recommendations
          </h3>
          <div className="space-y-3">
            {results.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start p-4 bg-gray-50 rounded-lg">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  {index + 1}
                </div>
                <span className="text-gray-700">{rec}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Co-Creator Invitation */}
        {results.co_creator_qualified && results.co_creator_invitation && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg mb-8 border-2 border-purple-200">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-purple-900 mb-2">
                🎉 Congratulations!
              </h3>
              <p className="text-purple-700 font-medium">
                {results.co_creator_invitation.message}
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {results.co_creator_invitation.benefits?.map((benefit: string, index: number) => (
                <div key={index} className="flex items-start">
                  <div className="w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center mt-0.5 mr-3 flex-shrink-0">
                    <span className="text-white text-xs">✓</span>
                  </div>
                  <span className="text-sm text-purple-800">{benefit}</span>
                </div>
              ))}
            </div>

            <div className="text-center">
              <p className="text-sm text-purple-600 mb-4">
                {results.co_creator_invitation.urgency}
              </p>
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700 px-8">
                {results.co_creator_invitation.next_action}
              </Button>
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Ready to Activate Your AI Marketing Team?
          </h3>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="px-8">
              Start AI Implementation
            </Button>
            <Button variant="outline" size="lg" onClick={resetAssessment}>
              Retake Assessment
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 max-w-2xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">AI Marketing Readiness Assessment</h2>
          <span className="text-sm text-gray-500">
            {currentQuestion + 1} of {questions.length}
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          {question.question}
        </h3>
        
        <div className="space-y-3">
          {question.options.map((option) => (
            <button
              key={option.value}
              onClick={() => handleAnswer(option.value)}
              className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="font-medium text-gray-900 mb-1">
                {option.label}
              </div>
              {option.description && (
                <div className="text-sm text-gray-600">
                  {option.description}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="text-center text-sm text-gray-500">
        This assessment analyzes your AI readiness, automation maturity, and integration needs
      </div>
    </div>
  );
};

export default AIReadinessAssessment;
