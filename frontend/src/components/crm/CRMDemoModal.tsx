import React, { useState } from 'react';
import { X, Play, CheckCircle, ArrowRight, ExternalLink } from 'lucide-react';
import { Card, Button } from '../ui';

interface CRMDemoModalProps {
  crmName: string;
  crmLogo: string;
  isOpen: boolean;
  onClose: () => void;
  onStartSetup: () => void;
}

const CRMDemoModal: React.FC<CRMDemoModalProps> = ({
  crmName,
  crmLogo,
  isOpen,
  onClose,
  onStartSetup
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const demoSteps = [
    {
      title: 'Connect Your Account',
      description: `Securely connect your ${crmName} account using OAuth2 authentication`,
      duration: '30 seconds',
      preview: 'OAuth2 connection flow with secure token exchange'
    },
    {
      title: 'Map Your Data',
      description: 'Automatically map your CRM fields to Unitasa for seamless synchronization',
      duration: '1 minute',
      preview: 'Smart field mapping with AI-powered suggestions'
    },
    {
      title: 'Configure Automation',
      description: 'Set up automated workflows and lead nurturing sequences',
      duration: '2 minutes',
      preview: 'Drag-and-drop workflow builder with CRM triggers'
    },
    {
      title: 'Start Syncing',
      description: 'Begin real-time data synchronization and automation',
      duration: 'Instant',
      preview: 'Live dashboard showing sync status and metrics'
    }
  ];

  const handlePlayDemo = () => {
    setIsPlaying(true);
    // Simulate demo progression
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= demoSteps.length - 1) {
          clearInterval(interval);
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 2000);
  };

  const resetDemo = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{crmLogo}</div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {crmName} Integration Demo
              </h2>
              <p className="text-gray-600">
                See how easy it is to connect {crmName} with Unitasa
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Demo Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Demo Steps */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Integration Process
              </h3>
              
              {demoSteps.map((step, index) => (
                <Card
                  key={index}
                  className={`p-4 border-2 transition-all ${
                    index === currentStep
                      ? 'border-primary-500 bg-primary-50'
                      : index < currentStep
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                      index < currentStep
                        ? 'bg-green-500 text-white'
                        : index === currentStep
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {index < currentStep ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{step.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">{step.duration}</span>
                        {index === currentStep && isPlaying && (
                          <div className="flex items-center text-xs text-primary-600">
                            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary-600 mr-1" />
                            Processing...
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Demo Preview */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Live Preview
              </h3>
              
              <Card className="p-6 bg-gray-50 min-h-[300px] flex items-center justify-center">
                {!isPlaying && currentStep === 0 ? (
                  <div className="text-center">
                    <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Play className="w-8 h-8 text-primary-600" />
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Ready to Start Demo
                    </h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Click play to see the {crmName} integration process in action
                    </p>
                    <Button variant="primary" onClick={handlePlayDemo} icon={Play}>
                      Start Demo
                    </Button>
                  </div>
                ) : (
                  <div className="w-full">
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="text-lg">{crmLogo}</div>
                        <div>
                          <h4 className="font-semibold text-gray-900">
                            {demoSteps[currentStep]?.title}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {demoSteps[currentStep]?.preview}
                          </p>
                        </div>
                      </div>
                      
                      {/* Mock UI based on current step */}
                      {currentStep === 0 && (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                            <span className="text-sm text-blue-800">OAuth2 Authentication</span>
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          </div>
                          <div className="text-xs text-gray-500">
                            Secure connection established with {crmName}
                          </div>
                        </div>
                      )}
                      
                      {currentStep === 1 && (
                        <div className="space-y-2">
                          {['Email', 'Name', 'Company', 'Phone'].map((field, i) => (
                            <div key={i} className="flex items-center justify-between p-2 bg-green-50 rounded">
                              <span className="text-sm text-green-800">{field}</span>
                              <ArrowRight className="w-4 h-4 text-green-600" />
                              <span className="text-sm text-green-800">{field.toLowerCase()}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {currentStep === 2 && (
                        <div className="space-y-3">
                          <div className="p-3 bg-purple-50 rounded-lg">
                            <div className="text-sm font-medium text-purple-800">Workflow Created</div>
                            <div className="text-xs text-purple-600">New lead → Welcome email → Follow-up sequence</div>
                          </div>
                        </div>
                      )}
                      
                      {currentStep === 3 && (
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 gap-3">
                            <div className="p-3 bg-green-50 rounded-lg text-center">
                              <div className="text-lg font-bold text-green-600">1,247</div>
                              <div className="text-xs text-green-800">Records Synced</div>
                            </div>
                            <div className="p-3 bg-blue-50 rounded-lg text-center">
                              <div className="text-lg font-bold text-blue-600">98%</div>
                              <div className="text-xs text-blue-800">Health Score</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {currentStep === demoSteps.length - 1 && !isPlaying && (
                      <div className="text-center mt-4">
                        <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                        <p className="text-sm text-green-600 font-medium">
                          Demo Complete! Ready to set up your integration?
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </Card>
              
              {currentStep > 0 && (
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={resetDemo}>
                    Restart Demo
                  </Button>
                  <Button variant="outline" size="sm" icon={ExternalLink}>
                    View Documentation
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600">
            Integration typically takes {demoSteps.reduce((total, step) => {
              const minutes = step.duration.includes('minute') ? parseInt(step.duration) : 0;
              return total + minutes;
            }, 0)} minutes to complete
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={onClose}>
              Close Demo
            </Button>
            <Button variant="primary" onClick={onStartSetup} icon={ArrowRight}>
              Start Real Setup
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CRMDemoModal;
