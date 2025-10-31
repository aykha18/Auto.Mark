import React from 'react';
import { Check } from 'lucide-react';

interface MultipleChoiceInputProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
}

export const MultipleChoiceInput: React.FC<MultipleChoiceInputProps> = ({
  options,
  value,
  onChange,
}) => {
  return (
    <div className="space-y-3">
      {options.map((option, index) => {
        const isSelected = value === option;
        
        return (
          <button
            key={index}
            type="button"
            onClick={() => onChange(option)}
            className={`w-full flex items-center justify-between p-4 border-2 rounded-lg transition-all duration-200 text-left ${
              isSelected
                ? 'border-primary-500 bg-primary-50 text-primary-900'
                : 'border-gray-300 bg-white text-gray-700 hover:border-primary-300 hover:bg-primary-25'
            }`}
          >
            <span className="font-medium">{option}</span>
            {isSelected && (
              <Check className="w-5 h-5 text-primary-600" />
            )}
          </button>
        );
      })}
    </div>
  );
};

export default MultipleChoiceInput;
