import React, { useState } from 'react';

interface DemoStep {
  id: string;
  title: string;
  description: string;
  code?: string;
  visual?: string;
  metrics?: {
    label: string;
    value: string;
    improvement?: string;
  }[];
}

interface TechnicalDemoProps {
  title: string;
  description: string;
  steps: DemoStep[];
  className?: string;
}

const TechnicalDemo: React.FC<TechnicalDemoProps> = ({
  title,
  description,
  steps,
  className = ''
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const playDemo = () => {
    setIsPlaying(true);
    setActiveStep(0);
    
    const interval = setInterval(() => {
      setActiveStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(interval);
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 3000);
  };

  const currentStep = steps[activeStep];

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
          </div>
          <button
            onClick={playDemo}
            disabled={isPlaying}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
            <span>{isPlaying ? 'Playing...' : 'Play Demo'}</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Step Navigation */}
        <div className="flex items-center space-x-2 mb-6">
          {steps.map((step, index) => (
            <button
              key={step.id}
              onClick={() => !isPlaying && setActiveStep(index)}
              disabled={isPlaying}
              className={`flex-1 p-3 rounded-lg text-sm font-medium transition-all ${
                index === activeStep
                  ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
                  : index < activeStep
                  ? 'bg-green-100 text-green-800 border-2 border-green-300'
                  : 'bg-gray-100 text-gray-600 border-2 border-gray-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  index === activeStep
                    ? 'bg-blue-600 text-white'
                    : index < activeStep
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-400 text-white'
                }`}>
                  {index < activeStep ? '✓' : index + 1}
                </span>
                <span className="truncate">{step.title}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Current Step Content */}
        <div className="space-y-6">
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              {currentStep.title}
            </h4>
            <p className="text-gray-600">{currentStep.description}</p>
          </div>

          {/* Code Example */}
          {currentStep.code && (
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-green-400 text-sm">
                <code>{currentStep.code}</code>
              </pre>
            </div>
          )}

          {/* Visual Representation */}
          {currentStep.visual && (
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <div className="text-4xl mb-2">{currentStep.visual}</div>
              <p className="text-sm text-gray-600">Visual representation</p>
            </div>
          )}

          {/* Metrics */}
          {currentStep.metrics && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {currentStep.metrics.map((metric, index) => (
                <div key={index} className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600 mb-1">
                    {metric.value}
                  </div>
                  <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
                  {metric.improvement && (
                    <div className="text-xs text-green-600 font-medium">
                      {metric.improvement}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{activeStep + 1} of {steps.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${((activeStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalDemo;