import React from 'react';
import { CheckCircle } from 'lucide-react';

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  progress: number;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  totalSteps,
  progress,
}) => {
  return (
    <div className="w-full">
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div
          className="bg-gradient-to-r from-primary-600 to-secondary-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step Indicators */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-600">
            Step {currentStep} of {totalSteps}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            {Math.round(progress)}% Complete
          </span>
          {progress === 100 && (
            <CheckCircle className="w-5 h-5 text-green-500" />
          )}
        </div>
      </div>

      {/* Step Dots */}
      <div className="flex justify-center space-x-2 mb-8">
        {Array.from({ length: totalSteps }, (_, index) => (
          <div
            key={index}
            className={`w-3 h-3 rounded-full transition-all duration-200 ${
              index < currentStep
                ? 'bg-primary-600'
                : index === currentStep - 1
                ? 'bg-primary-400 ring-2 ring-primary-200'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

export default ProgressIndicator;
