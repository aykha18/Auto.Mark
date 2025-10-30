import React, { useState } from 'react';
import { PaymentResult } from '../../types';
import CoCreatorProgramInterface from './CoCreatorProgramInterface';
import PaymentProcessingUI from './PaymentProcessingUI';
import PaymentConfirmation from './PaymentConfirmation';
import OnboardingActivation from './OnboardingActivation';

interface PaymentFlowProps {
  onComplete?: () => void;
  className?: string;
}

type FlowStep = 'program_details' | 'payment_form' | 'confirmation' | 'onboarding' | 'complete';

const PaymentFlow: React.FC<PaymentFlowProps> = ({
  onComplete,
  className = '',
}) => {
  const [currentStep, setCurrentStep] = useState<FlowStep>('program_details');
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null);

  const handleJoinProgram = () => {
    setCurrentStep('payment_form');
  };

  const handlePaymentSuccess = (result: PaymentResult) => {
    setPaymentResult(result);
    setCurrentStep('confirmation');
  };

  const handleConfirmationContinue = () => {
    setCurrentStep('onboarding');
  };

  const handleOnboardingComplete = () => {
    setCurrentStep('complete');
    if (onComplete) {
      onComplete();
    }
  };

  const handleBackToProgram = () => {
    setCurrentStep('program_details');
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'program_details':
        return (
          <CoCreatorProgramInterface
            onJoinProgram={handleJoinProgram}
            className={className}
          />
        );

      case 'payment_form':
        return (
          <PaymentProcessingUI
            onPaymentSuccess={handlePaymentSuccess}
            onBack={handleBackToProgram}
            className={className}
          />
        );

      case 'confirmation':
        return paymentResult ? (
          <PaymentConfirmation
            paymentResult={paymentResult}
            onContinue={handleConfirmationContinue}
            className={className}
          />
        ) : null;

      case 'onboarding':
        return paymentResult?.coCreatorId ? (
          <OnboardingActivation
            coCreatorId={paymentResult.coCreatorId}
            onComplete={handleOnboardingComplete}
            className={className}
          />
        ) : null;

      case 'complete':
        return (
          <div className={`bg-gradient-to-br from-green-900 via-primary-800 to-secondary-900 rounded-2xl p-8 text-white text-center ${className}`}>
            <h1 className="text-4xl font-bold mb-4">Welcome to the Co-Creator Community! 🎉</h1>
            <p className="text-xl mb-6">Your journey as a co-creator has begun. Thank you for being part of this vision!</p>
            <p className="text-gray-300">Redirecting to your dashboard...</p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="w-full">
      {renderCurrentStep()}
    </div>
  );
};

export default PaymentFlow;