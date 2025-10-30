import React, { useState } from 'react';
import { CRMAssessmentQuestion, AssessmentResponse } from '../../types';
import CRMSelector from './CRMSelector';
import ScaleInput from './ScaleInput';
import MultipleChoiceInput from './MultipleChoiceInput';
import TextInput from './TextInput';
import { Info } from 'lucide-react';

interface QuestionStepProps {
  question: CRMAssessmentQuestion;
  response?: AssessmentResponse;
  onResponse: (questionId: string, answer: string | number, selectedCRM?: string) => void;
}

export const QuestionStep: React.FC<QuestionStepProps> = ({
  question,
  response,
  onResponse,
}) => {
  const [showInsight, setShowInsight] = useState(false);

  const handleAnswerChange = (answer: string | number, selectedCRM?: string) => {
    onResponse(question.id, answer, selectedCRM);
  };

  const renderInput = () => {
    switch (question.type) {
      case 'crm_selector':
        return (
          <CRMSelector
            value={response?.selectedCRM || ''}
            onChange={(crm: string) => handleAnswerChange(crm, crm)}
          />
        );
      
      case 'scale':
        return (
          <ScaleInput
            value={typeof response?.answer === 'number' ? response.answer : 0}
            onChange={(value: number) => handleAnswerChange(value)}
            min={1}
            max={10}
          />
        );
      
      case 'multiple_choice':
        return (
          <MultipleChoiceInput
            options={question.options || []}
            value={typeof response?.answer === 'string' ? response.answer : ''}
            onChange={(value: string) => handleAnswerChange(value)}
          />
        );
      
      case 'text':
        return (
          <TextInput
            value={typeof response?.answer === 'string' ? response.answer : ''}
            onChange={(value: string) => handleAnswerChange(value)}
            placeholder="Please describe your current situation..."
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      {/* Category Badge */}
      <div className="mb-4">
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
          question.category === 'current_crm' ? 'bg-blue-100 text-blue-800' :
          question.category === 'data_quality' ? 'bg-green-100 text-green-800' :
          question.category === 'automation_gaps' ? 'bg-yellow-100 text-yellow-800' :
          'bg-purple-100 text-purple-800'
        }`}>
          {question.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </span>
      </div>

      {/* Question */}
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {question.text}
      </h2>

      {/* Input */}
      <div className="mb-6">
        {renderInput()}
      </div>

      {/* Integration Insight */}
      {question.integrationInsight && (
        <div className="border-t pt-6">
          <button
            onClick={() => setShowInsight(!showInsight)}
            className="flex items-center text-primary-600 hover:text-primary-700 font-medium"
          >
            <Info className="w-4 h-4 mr-2" />
            {showInsight ? 'Hide' : 'Show'} Integration Insight
          </button>
          
          {showInsight && (
            <div className="mt-4 p-4 bg-primary-50 rounded-lg border border-primary-200">
              <p className="text-primary-800">{question.integrationInsight}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuestionStep;