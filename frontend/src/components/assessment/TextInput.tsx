import React from 'react';

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  multiline?: boolean;
  maxLength?: number;
}

export const TextInput: React.FC<TextInputProps> = ({
  value,
  onChange,
  placeholder = 'Enter your response...',
  multiline = true,
  maxLength = 500,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      onChange(newValue);
    }
  };

  const commonProps = {
    value,
    onChange: handleChange,
    placeholder,
    className: `w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none`,
  };

  return (
    <div className="space-y-2">
      {multiline ? (
        <textarea
          {...commonProps}
          rows={4}
        />
      ) : (
        <input
          type="text"
          {...commonProps}
        />
      )}
      
      {/* Character Counter */}
      <div className="flex justify-between text-sm text-gray-500">
        <span>Be specific to get better recommendations</span>
        <span>{value.length}/{maxLength}</span>
      </div>
    </div>
  );
};export 
default TextInput;
