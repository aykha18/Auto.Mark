import React from 'react';
import EnhancedAIAssessment from './EnhancedAIAssessment';
import { CRMAssessmentResult } from '../../types';
import { LeadData } from './LeadCaptureForm';
import { X } from 'lucide-react';

interface AssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: (result: CRMAssessmentResult) => void;
  leadData?: LeadData | null;
}

export const AssessmentModal: React.FC<AssessmentModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  leadData,
}) => {
  if (!isOpen) return null;

  const handleComplete = (result: CRMAssessmentResult) => {
    onComplete?.(result);
    // Keep modal open to show results
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
          
          {/* Content */}
          <div className="p-8">
            <EnhancedAIAssessment 
              onComplete={handleComplete}
              onClose={onClose}
              leadData={leadData}
            />
          </div>
        </div>
      </div>
    </div>
  );
};export
 default AssessmentModal;
