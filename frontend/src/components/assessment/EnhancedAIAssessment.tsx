import React, { useState } from 'react';
import { Brain, Target, Zap, Shield, BarChart3, MessageCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import Button from '../ui/Button';
import AIReadinessAssessment from './AIReadinessAssessment';
import { LeadData } from './LeadCaptureForm';

interface AssessmentStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

interface EnhancedAIAssessmentProps {
  onComplete?: (results: any) => void;
  onClose?: () => void;
  leadData?: LeadData | null;
}

const EnhancedAIAssessment: React.FC<EnhancedAIAssessmentProps> = ({ onComplete, onClose, leadData }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [assessmentData, setAssessmentData] = useState<Record<string, any>>({});
  const [showResults, setShowResults] = useState(false);

  const steps: AssessmentStep[] = [
    {
      id: 'welcome',
      title: 'AI Marketing Intelligence Assessment',
      description: 'Discover your AI readiness and unlock autonomous marketing potential',
      icon: <Brain className="w-8 h-8" />,
      component: (
        <div className="text-center py-12">
          <div className="mb-8">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Marketing Intelligence Unity Assessment
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Discover how Unitasa can replace your fragmented marketing tools with one unified platform. 
              Get your personalized marketing unity roadmap in just 3 minutes.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <Target className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">AI Readiness Score</h3>
              <p className="text-sm text-gray-600">Assess your current AI maturity level</p>
            </div>
            <div className="bg-green-50 p-6 rounded-lg">
              <Zap className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">ROI Prediction</h3>
              <p className="text-sm text-gray-600">Forecast your AI implementation impact</p>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg">
              <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Custom Roadmap</h3>
              <p className="text-sm text-gray-600">Get your personalized AI strategy</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">What You'll Discover:</h3>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <div className="flex items-start">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Your AI Marketing IQ Score (0-100)</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Predicted ROI improvement potential</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Priority automation opportunities</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Personalized AI agent recommendations</span>
              </div>
            </div>
          </div>

          <Button 
            size="lg" 
            onClick={() => setCurrentStep(1)}
            className="px-8 py-4 text-lg"
          >
            Start AI Assessment
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )
    },
    {
      id: 'ai-readiness',
      title: 'AI Readiness Assessment',
      description: 'Evaluate your current AI and automation capabilities',
      icon: <Brain className="w-8 h-8" />,
      component: <AIReadinessAssessment leadData={leadData} />
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleStepData = (stepId: string, data: any) => {
    setAssessmentData(prev => ({
      ...prev,
      [stepId]: data
    }));
  };

  if (showResults) {
    return (
      <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Assessment Complete!
          </h2>
          <p className="text-xl text-gray-600">
            Your AI Marketing Intelligence Report is ready
          </p>
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
            Next Steps: Activate Your AI Marketing Team
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <MessageCircle className="w-8 h-8 text-blue-600 mb-3" />
              <h4 className="font-semibold text-gray-900 mb-2">
                Schedule AI Strategy Session
              </h4>
              <p className="text-sm text-gray-600 mb-4">
                Get a personalized 30-minute consultation to discuss your AI implementation roadmap
              </p>
              <Button size="sm" className="w-full">
                Book Free Session
              </Button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-purple-200">
              <div className="flex items-center justify-between mb-3">
                <Zap className="w-8 h-8 text-purple-600" />
                <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-semibold">
                  LIMITED TIME
                </span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Join 25 Founding Co-Creators
              </h4>
              <div className="mb-3">
                <div className="text-2xl font-bold text-purple-600">$497</div>
                <div className="text-xs text-gray-500 line-through">Regular: $2,000+</div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Lifetime access to AI platform + direct product influence + priority support
              </p>
              <Button size="sm" className="w-full bg-purple-600 hover:bg-purple-700">
                Secure Founding Spot
              </Button>
              <div className="text-xs text-center text-gray-500 mt-2">
                ⚡ Only 12 spots remaining
              </div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Button onClick={onClose} variant="outline" className="mr-4">
            Close Assessment
          </Button>
          <Button onClick={() => onComplete?.(assessmentData)}>
            Get Full AI Report
          </Button>
        </div>
      </div>
    );
  }

  const currentStepData = steps[currentStep];

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 max-w-4xl mx-auto">
      {/* Progress Header */}
      {currentStep > 0 && (
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {currentStepData.title}
            </h2>
            <span className="text-sm text-gray-500">
              Step {currentStep} of {steps.length - 1}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Step Content */}
      <div className="p-6">
        {currentStepData.component}
      </div>

      {/* Navigation */}
      {currentStep > 0 && (
        <div className="p-6 border-t border-gray-200 flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          <Button onClick={handleNext}>
            {currentStep === steps.length - 1 ? 'Complete Assessment' : 'Continue'}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default EnhancedAIAssessment;
