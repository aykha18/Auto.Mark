import React, { useState } from 'react';
import { X, ArrowRight, ArrowLeft } from 'lucide-react';
import Button from '../ui/Button';

interface CRMSelectorStepProps {
  isOpen: boolean;
  onClose: () => void;
  onNext: (selectedCRM: string) => void;
  onBack: () => void;
}

interface CRMOption {
  id: string;
  name: string;
  icon: string; // We'll use text/emoji for now, can be replaced with actual icons
  color: string;
}

const CRMSelectorStep: React.FC<CRMSelectorStepProps> = ({
  isOpen,
  onClose,
  onNext,
  onBack
}) => {
  const [selectedCRM, setSelectedCRM] = useState<string>('');
  const [customCrmName, setCustomCrmName] = useState<string>('');

  const crmOptions: CRMOption[] = [
    { id: 'pipedrive', name: 'Pipedrive', icon: '🔧', color: 'bg-green-500' },
    { id: 'zoho', name: 'Zoho CRM', icon: '🎯', color: 'bg-orange-500' },
    { id: 'hubspot', name: 'HubSpot', icon: '🚀', color: 'bg-orange-600' },
    { id: 'monday', name: 'Monday.com', icon: '📊', color: 'bg-blue-500' },
    { id: 'freshworks', name: 'Freshworks', icon: '🌱', color: 'bg-green-600' },
    { id: 'salesforce', name: 'Salesforce', icon: '☁️', color: 'bg-blue-600' },
    { id: 'agilecrm', name: 'AgileCRM', icon: '⚡', color: 'bg-purple-500' },
    { id: 'copper', name: 'Copper CRM', icon: '🔶', color: 'bg-orange-700' },
    { id: 'jetpack', name: 'Jetpack CRM', icon: '✈️', color: 'bg-gray-600' },
    { id: 'other', name: 'Other CRM', icon: '❓', color: 'bg-gray-500' },
    { id: 'none', name: 'No CRM Yet', icon: '❌', color: 'bg-red-500' }
  ];

  const handleCRMSelect = (crmId: string) => {
    setSelectedCRM(crmId);
  };

  const handleNext = () => {
    console.log('CRM selector next clicked, selected:', selectedCRM);
    console.log('Custom CRM name:', customCrmName);
    
    if (selectedCRM) {
      // If "other" is selected, pass the custom name, otherwise pass the selected CRM
      const crmValue = selectedCRM === 'other' ? `other:${customCrmName}` : selectedCRM;
      onNext(crmValue);
    }
  };

  const isNextDisabled = !selectedCRM || (selectedCRM === 'other' && !customCrmName.trim());

  if (!isOpen) return null;

  console.log('CRM Selector Step is open');

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Which CRM do you use?
            </h2>
            <p className="text-gray-600 mt-1">
              Select your current CRM system for personalized recommendations
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* CRM Grid */}
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {crmOptions.map((crm) => (
              <button
                key={crm.id}
                onClick={() => handleCRMSelect(crm.id)}
                className={`
                  relative p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md
                  ${selectedCRM === crm.id 
                    ? 'border-primary-500 bg-primary-50 shadow-md' 
                    : 'border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                {/* Selection indicator */}
                {selectedCRM === crm.id && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                )}
                
                {/* CRM Icon */}
                <div className={`w-12 h-12 ${crm.color} rounded-lg flex items-center justify-center text-white text-xl mb-3 mx-auto`}>
                  {crm.icon}
                </div>
                
                {/* CRM Name */}
                <div className="text-sm font-medium text-gray-900 text-center">
                  {crm.name}
                </div>
              </button>
            ))}
          </div>

          {/* Custom CRM Name Input - Show when "other" is selected */}
          {selectedCRM === 'other' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Please specify your CRM system:
              </label>
              <input
                type="text"
                value={customCrmName}
                onChange={(e) => setCustomCrmName(e.target.value)}
                placeholder="Enter your CRM system name (e.g., Custom CRM, In-house system, etc.)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                autoFocus
              />
            </div>
          )}

          {/* Help Text */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>Don't see your CRM?</strong> Select "Other CRM" and specify your system name. We'll provide general integration guidance that works with most systems.
            </p>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={onBack}
              icon={ArrowLeft}
              iconPosition="left"
            >
              Back
            </Button>
            
            <Button
              variant="primary"
              onClick={handleNext}
              disabled={isNextDisabled}
              icon={ArrowRight}
              iconPosition="right"
            >
              Continue to Assessment
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CRMSelectorStep;