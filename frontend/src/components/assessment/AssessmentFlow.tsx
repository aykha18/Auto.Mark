import React, { useState, useEffect } from 'react';
import { CRMAssessmentQuestion, AssessmentResponse, CRMAssessmentResult } from '../../types';
import LandingPageAPI from '../../services/landingPageApi';
import QuestionStep from './QuestionStep';
import ProgressIndicator from './ProgressIndicator';
import AssessmentResults from './AssessmentResults';
import Button from '../ui/Button';
import { ArrowLeft, ArrowRight } from 'lucide-react';

interface AssessmentFlowProps {
  onComplete?: (result: CRMAssessmentResult) => void;
  onClose?: () => void;
}

export const AssessmentFlow: React.FC<AssessmentFlowProps> = ({ onComplete, onClose }) => {
  const [questions, setQuestions] = useState<CRMAssessmentQuestion[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState<AssessmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<CRMAssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);

  useEffect(() => {
    initializeAssessment();
  }, []);

  const initializeAssessment = async () => {
    try {
      setLoading(true);
      
      // For testing, just load questions directly
      const questionsData = await LandingPageAPI.getAssessmentQuestions();
      setQuestions(questionsData);
      setAssessmentId(1); // Mock assessment ID for testing
    } catch (err) {
      setError('Failed to load assessment questions. Please try again.');
      console.error('Error loading questions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = (questionId: string, answer: string | number, selectedCRM?: string) => {
    const newResponse: AssessmentResponse = {
      questionId,
      answer,
      selectedCRM,
      timestamp: new Date(),
      integrationInsightViewed: false,
    };

    setResponses(prev => {
      const existing = prev.findIndex(r => r.questionId === questionId);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = newResponse;
        return updated;
      }
      return [...prev, newResponse];
    });
  };

  const canProceed = () => {
    const currentQuestion = questions[currentStep];
    if (!currentQuestion) return false;
    
    const response = responses.find(r => r.questionId === currentQuestion.id);
    return response && (response.answer !== '' && response.answer !== null && response.answer !== undefined);
  }; 
 const nextStep = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      submitAssessment();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const submitAssessment = async () => {
    if (!assessmentId) {
      setError('Assessment not properly initialized. Please try again.');
      return;
    }

    try {
      setSubmitting(true);
      const assessmentResult = await LandingPageAPI.submitAssessmentResponse({
        assessment_id: assessmentId,
        responses: responses
      });
      setResult(assessmentResult);
      onComplete?.(assessmentResult);
    } catch (err) {
      setError('Failed to submit assessment. Please try again.');
      console.error('Error submitting assessment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <Button onClick={initializeAssessment} variant="primary">
          Try Again
        </Button>
      </div>
    );
  }

  if (result) {
    return <AssessmentResults result={result} onClose={onClose} />;
  }

  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;

  return (
    <div className="max-w-4xl mx-auto">
      <ProgressIndicator 
        currentStep={currentStep + 1} 
        totalSteps={questions.length} 
        progress={progress}
      />
      
      <div className="mt-8">
        <QuestionStep
          question={currentQuestion}
          response={responses.find(r => r.questionId === currentQuestion.id)}
          onResponse={handleResponse}
        />
      </div>

      <div className="flex justify-between mt-8">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
          icon={ArrowLeft}
          iconPosition="left"
        >
          Previous
        </Button>

        <Button
          variant="primary"
          onClick={nextStep}
          disabled={!canProceed() || submitting}
          loading={submitting}
          icon={currentStep === questions.length - 1 ? undefined : ArrowRight}
          iconPosition="right"
        >
          {currentStep === questions.length - 1 ? 'Get Results' : 'Next'}
        </Button>
      </div>
    </div>
  );
};

export default AssessmentFlow;