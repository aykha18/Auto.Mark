import React, { useState } from 'react';
import { Search, ChevronDown } from 'lucide-react';

interface CRMSelectorProps {
  value: string;
  onChange: (crm: string) => void;
}

const CRM_OPTIONS = [
  { id: 'pipedrive', name: 'Pipedrive', logo: '🔵' },
  { id: 'hubspot', name: 'HubSpot', logo: '🟠' },
  { id: 'salesforce', name: 'Salesforce', logo: '🔷' },
  { id: 'zoho', name: 'Zoho CRM', logo: '🟡' },
  { id: 'monday', name: 'Monday.com', logo: '🟣' },
  { id: 'airtable', name: 'Airtable', logo: '🟢' },
  { id: 'notion', name: 'Notion', logo: '⚫' },
  { id: 'excel', name: 'Excel/Google Sheets', logo: '📊' },
  { id: 'other', name: 'Other CRM', logo: '❓' },
  { id: 'none', name: 'No CRM Currently', logo: '❌' },
];

export const CRMSelector: React.FC<CRMSelectorProps> = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredOptions = CRM_OPTIONS.filter(option =>
    option.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedOption = CRM_OPTIONS.find(option => option.id === value);

  const handleSelect = (crmId: string) => {
    onChange(crmId);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative">
      {/* Selected Value Display */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 border border-gray-300 rounded-lg bg-white hover:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      >
        <div className="flex items-center">
          {selectedOption ? (
            <>
              <span className="text-2xl mr-3">{selectedOption.logo}</span>
              <span className="text-gray-900">{selectedOption.name}</span>
            </>
          ) : (
            <span className="text-gray-500">Select your current CRM system</span>
          )}
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-gray-300 rounded-lg shadow-lg">
          {/* Search */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search CRM systems..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Options */}
          <div className="max-h-64 overflow-y-auto">
            {filteredOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => handleSelect(option.id)}
                className={`w-full flex items-center px-4 py-3 hover:bg-gray-50 transition-colors ${
                  value === option.id ? 'bg-primary-50 text-primary-700' : 'text-gray-900'
                }`}
              >
                <span className="text-2xl mr-3">{option.logo}</span>
                <span>{option.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};export 
default CRMSelector;