import React, { useState, useEffect } from 'react';
import { CoCreatorProfile } from '../../types';
import Button from '../ui/Button';
import {
  Rocket,
  CheckCircle,
  Clock,
  Users,
  Star,
  Calendar,
  MessageCircle,
  Settings,
  Crown,
  ExternalLink,
  Play,
  BookOpen,
  Headphones
} from 'lucide-react';

interface OnboardingActivationProps {
  coCreatorId: string;
  onComplete: () => void;
  className?: string;
}

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  status: 'pending' | 'in_progress' | 'completed';
  estimatedTime: string;
  action?: {
    label: string;
    url?: string;
    onClick?: () => void;
  };
  urgent?: boolean;
}

const OnboardingActivation: React.FC<OnboardingActivationProps> = ({
  coCreatorId,
  onComplete,
  className = '',
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<OnboardingStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeOnboarding();
  }, [coCreatorId]);

  const initializeOnboarding = async () => {
    try {
      // Load co-creator profile
      const profileResponse = await fetch(`/api/v1/landing/co-creator-profile/${coCreatorId}`);
      if (!profileResponse.ok) {
        console.error('Failed to load co-creator profile');
      }

      // Initialize onboarding steps
      const onboardingSteps: OnboardingStep[] = [
        {
          id: 'welcome_email',
          title: 'Welcome Email Sent',
          description: 'Exclusive co-creator resources and community access details',
          icon: CheckCircle,
          status: 'completed',
          estimatedTime: 'Instant',
        },
        {
          id: 'platform_access',
          title: 'Platform Access Activated',
          description: 'Lifetime access to Unitasa with all current and future features',
          icon: Rocket,
          status: 'in_progress',
          estimatedTime: '30 seconds',
        },
        {
          id: 'community_invite',
          title: 'Community Invitation',
          description: 'Join exclusive Slack workspace with other co-creators and the founder',
          icon: Users,
          status: 'pending',
          estimatedTime: '1 minute',
          action: {
            label: 'Join Community',
            url: 'https://automark-cocreators.slack.com/join'
          },
          urgent: true
        },
        {
          id: 'integration_consultation',
          title: 'CRM Integration Consultation',
          description: 'Schedule your priority integration setup call with our team',
          icon: Calendar,
          status: 'pending',
          estimatedTime: '2 minutes',
          action: {
            label: 'Schedule Call',
            url: 'https://calendly.com/automark/co-creator-integration'
          },
          urgent: true
        },
        {
          id: 'roadmap_access',
          title: 'Product Roadmap Access',
          description: 'View upcoming features and cast your votes on development priorities',
          icon: Star,
          status: 'pending',
          estimatedTime: '1 minute',
          action: {
            label: 'View Roadmap',
            url: '/co-creator/roadmap'
          }
        },
        {
          id: 'support_channel',
          title: 'Priority Support Channel',
          description: 'Direct communication channel for technical questions and feedback',
          icon: MessageCircle,
          status: 'pending',
          estimatedTime: '30 seconds',
          action: {
            label: 'Access Support',
            url: '/co-creator/support'
          }
        }
      ];

      setSteps(onboardingSteps);
      startActivationSequence(onboardingSteps);
    } catch (error) {
      console.error('Failed to initialize onboarding:', error);
    } finally {
      setLoading(false);
    }
  };

  const startActivationSequence = async (initialSteps: OnboardingStep[]) => {
    const updatedSteps = [...initialSteps];
    
    // Simulate activation sequence
    for (let i = 0; i < updatedSteps.length; i++) {
      if (updatedSteps[i].status === 'pending') {
        updatedSteps[i].status = 'in_progress';
        setSteps([...updatedSteps]);
        setCurrentStep(i);
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
        
        // Complete the step
        updatedSteps[i].status = 'completed';
        setSteps([...updatedSteps]);
        
        // Trigger backend activation if needed
        if (updatedSteps[i].id === 'platform_access') {
          await activatePlatformAccess();
        }
      }
    }
  };

  const activatePlatformAccess = async () => {
    try {
      await fetch(`/api/v1/landing/co-creator-activate/${coCreatorId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lifetimeAccess: true,
          supporterBadge: true,
          activatedAt: new Date().toISOString()
        }),
      });
    } catch (error) {
      console.error('Failed to activate platform access:', error);
    }
  };

  const handleStepAction = (step: OnboardingStep) => {
    if (step.action?.onClick) {
      step.action.onClick();
    } else if (step.action?.url) {
      if (step.action.url.startsWith('http')) {
        window.open(step.action.url, '_blank');
      } else {
        window.location.href = step.action.url;
      }
    }
  };

  const getStepIcon = (step: OnboardingStep) => {
    if (step.status === 'completed') {
      return CheckCircle;
    } else if (step.status === 'in_progress') {
      return Clock;
    }
    return step.icon;
  };

  const getStepColor = (step: OnboardingStep) => {
    if (step.status === 'completed') {
      return 'text-green-400';
    } else if (step.status === 'in_progress') {
      return 'text-yellow-400';
    } else if (step.urgent) {
      return 'text-orange-400';
    }
    return 'text-gray-400';
  };

  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const totalSteps = steps.length;
  const progressPercentage = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 rounded-2xl p-8 text-white ${className}`}>
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-white/20 border-t-white rounded-full mx-auto mb-4"></div>
          <p className="text-lg">Initializing your co-creator experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 rounded-2xl overflow-hidden ${className}`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white rounded-full translate-y-24 -translate-x-24"></div>
      </div>

      <div className="relative z-10 p-8 text-white">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Rocket className="w-10 h-10 text-blue-400 mr-3" />
            <h1 className="text-3xl md:text-4xl font-bold">Activating Your Co-Creator Experience</h1>
          </div>
          
          <p className="text-xl opacity-90 mb-6">
            Setting up your exclusive access and benefits...
          </p>

          {/* Progress Bar */}
          <div className="max-w-md mx-auto">
            <div className="flex justify-between text-sm mb-2">
              <span>Progress</span>
              <span>{completedSteps}/{totalSteps} completed</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-green-400 to-blue-400 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Onboarding Steps */}
        <div className="space-y-4 mb-8">
          {steps.map((step, index) => {
            const StepIcon = getStepIcon(step);
            const isActive = index === currentStep;
            
            return (
              <div key={step.id} className={`bg-white/10 backdrop-blur-sm rounded-xl p-6 border transition-all duration-300 ${
                isActive ? 'border-blue-400 bg-blue-500/10' : 'border-white/20'
              }`}>
                <div className="flex items-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-4 ${
                    step.status === 'completed' ? 'bg-green-500/20' :
                    step.status === 'in_progress' ? 'bg-yellow-500/20' :
                    step.urgent ? 'bg-orange-500/20' : 'bg-gray-500/20'
                  }`}>
                    <StepIcon className={`w-6 h-6 ${getStepColor(step)}`} />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold">{step.title}</h3>
                      <div className="flex items-center space-x-2">
                        {step.urgent && step.status === 'pending' && (
                          <span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded-full">
                            Action Required
                          </span>
                        )}
                        <span className="text-sm text-gray-400">{step.estimatedTime}</span>
                      </div>
                    </div>
                    
                    <p className="text-gray-300 mb-3">{step.description}</p>
                    
                    {step.action && step.status === 'completed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        icon={ExternalLink}
                        iconPosition="right"
                        onClick={() => handleStepAction(step)}
                        className="text-blue-400 border-blue-400 hover:bg-blue-400/10"
                      >
                        {step.action.label}
                      </Button>
                    )}
                  </div>
                  
                  {step.status === 'in_progress' && (
                    <div className="ml-4">
                      <div className="animate-spin w-6 h-6 border-2 border-white/20 border-t-yellow-400 rounded-full"></div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Start Guide */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <BookOpen className="w-6 h-6 text-purple-400 mr-2" />
            Quick Start Resources
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <Play className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <h3 className="font-semibold mb-2">Video Walkthrough</h3>
              <p className="text-sm text-gray-300 mb-3">5-minute tour of co-creator features</p>
              <Button variant="outline" size="sm">Watch Now</Button>
            </div>
            
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <Settings className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <h3 className="font-semibold mb-2">Setup Guide</h3>
              <p className="text-sm text-gray-300 mb-3">Step-by-step integration setup</p>
              <Button variant="outline" size="sm">Read Guide</Button>
            </div>
            
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <Headphones className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
              <h3 className="font-semibold mb-2">Live Support</h3>
              <p className="text-sm text-gray-300 mb-3">Chat with our integration experts</p>
              <Button variant="outline" size="sm">Get Help</Button>
            </div>
          </div>
        </div>

        {/* Completion Actions */}
        <div className="text-center">
          {progressPercentage === 100 ? (
            <div>
              <div className="mb-6">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-2">Activation Complete! 🎉</h2>
                <p className="text-gray-300">Your co-creator experience is now fully activated</p>
              </div>
              
              <Button
                variant="primary"
                size="lg"
                className="bg-gradient-to-r from-green-400 to-blue-400 text-black hover:from-green-300 hover:to-blue-300 font-bold text-lg px-12 py-4"
                icon={Crown}
                iconPosition="left"
                onClick={onComplete}
              >
                Enter Co-Creator Dashboard
              </Button>
            </div>
          ) : (
            <div>
              <p className="text-gray-300 mb-4">
                Activation in progress... Please wait while we set up your exclusive access.
              </p>
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin w-5 h-5 border-2 border-white/20 border-t-white rounded-full"></div>
                <span>Setting up your co-creator benefits...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingActivation;
