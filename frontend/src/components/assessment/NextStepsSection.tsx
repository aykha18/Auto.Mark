import React from 'react';
import { ArrowRight, Calendar, BookOpen, Users, Zap } from 'lucide-react';
import Button from '../ui/Button';

interface NextStepsSectionProps {
  steps: string[];
  readinessLevel: string;
  onStartPayment?: () => void;
}

const NextStepsSection: React.FC<NextStepsSectionProps> = ({
  steps,
  readinessLevel,
  onStartPayment,
}) => {
  const getActionButton = () => {
    switch (readinessLevel) {
      case 'priority_integration':
        return (
          <div className="space-y-3">
            <Button
              variant="primary"
              icon={Calendar}
              iconPosition="left"
              className="w-full"
              onClick={() => window.open('https://calendly.com/automark-founder', '_blank')}
            >
              Book Priority Demo (15 min)
            </Button>
            <Button
              variant="outline"
              icon={Zap}
              iconPosition="left"
              className="w-full"
              onClick={() => {
                console.log('Start Integration Setup clicked');
                if (onStartPayment) {
                  onStartPayment();
                } else {
                  alert('Priority integration setup is being prepared...');
                }
              }}
            >
              Start Integration Setup
            </Button>
            <div className="text-xs text-gray-500 text-center">
              Priority support • Direct founder access • Custom integration
            </div>
          </div>
        );
      case 'co_creator_qualified':
        return (
          <div className="space-y-3">
            <Button
              variant="primary"
              icon={Users}
              iconPosition="left"
              className="w-full"
              onClick={() => {
                console.log('Join Co-Creator Program clicked');
                if (onStartPayment) {
                  onStartPayment();
                } else {
                  alert('Payment system is being initialized...');
                }
              }}
            >
              Join Co-Creator Program ($497)
            </Button>
            <Button
              variant="outline"
              icon={BookOpen}
              iconPosition="left"
              className="w-full"
              onClick={() => {
                console.log('View Integration Guide clicked');
                window.open('/integration-guide', '_blank');
              }}
            >
              View Integration Guide
            </Button>
            <div className="text-xs text-gray-500 text-center">
              Lifetime access • Roadmap influence • Integration support
            </div>
          </div>
        );
      case 'nurture_with_guides':
        return (
          <div className="space-y-3">
            <Button
              variant="primary"
              icon={BookOpen}
              iconPosition="left"
              className="w-full"
            >
              Download Free CRM Strategy Guide
            </Button>
            <Button
              variant="outline"
              icon={ArrowRight}
              iconPosition="left"
              className="w-full"
            >
              Explore CRM Integrations
            </Button>
            <div className="text-xs text-gray-500 text-center">
              Free resources • Step-by-step guides • Foundation building
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  const getTimelineEstimate = () => {
    switch (readinessLevel) {
      case 'priority_integration':
        return 'Ready to launch in 1-2 weeks';
      case 'co_creator_qualified':
        return 'Ready to launch in 2-4 weeks';
      case 'nurture_with_guides':
        return 'Foundation building: 4-8 weeks';
      default:
        return '';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <ArrowRight className="w-6 h-6 text-primary-600 mr-3" />
          <h3 className="text-xl font-bold text-gray-900">Your Next Steps</h3>
        </div>
        {getTimelineEstimate() && (
          <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            {getTimelineEstimate()}
          </div>
        )}
      </div>
      
      <div className="space-y-4 mb-6">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start group hover:bg-gray-50 p-3 rounded-lg transition-colors">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3">
              {index + 1}
            </div>
            <p className="text-gray-700 leading-relaxed pt-1 flex-1">{step}</p>
            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
              <ArrowRight className="w-4 h-4 text-gray-400 mt-1" />
            </div>
          </div>
        ))}
      </div>
      
      {getActionButton()}
    </div>
  );
};

export default NextStepsSection;
