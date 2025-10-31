import React from 'react';

interface ScaleInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  labels?: { min: string; max: string };
}

export const ScaleInput: React.FC<ScaleInputProps> = ({
  value,
  onChange,
  min = 1,
  max = 10,
  labels = { min: 'Not at all', max: 'Extremely well' },
}) => {
  const handleClick = (selectedValue: number) => {
    onChange(selectedValue);
  };

  return (
    <div className="space-y-4">
      {/* Scale Buttons */}
      <div className="flex justify-between items-center space-x-2">
        {Array.from({ length: max - min + 1 }, (_, index) => {
          const scaleValue = min + index;
          const isSelected = value === scaleValue;
          
          return (
            <button
              key={scaleValue}
              type="button"
              onClick={() => handleClick(scaleValue)}
              className={`w-12 h-12 rounded-full border-2 font-semibold transition-all duration-200 ${
                isSelected
                  ? 'bg-primary-600 border-primary-600 text-white shadow-lg scale-110'
                  : 'bg-white border-gray-300 text-gray-700 hover:border-primary-400 hover:bg-primary-50'
              }`}
            >
              {scaleValue}
            </button>
          );
        })}
      </div>

      {/* Labels */}
      <div className="flex justify-between text-sm text-gray-600">
        <span>{labels.min}</span>
        <span>{labels.max}</span>
      </div>

      {/* Selected Value Display */}
      {value > 0 && (
        <div className="text-center">
          <span className="inline-block px-4 py-2 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
            Selected: {value}
          </span>
        </div>
      )}
    </div>
  );
};export 
default ScaleInput;
