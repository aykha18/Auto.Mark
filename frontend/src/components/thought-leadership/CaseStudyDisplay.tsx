import React, { useState } from 'react';

interface CaseStudyMetric {
  label: string;
  before: string;
  after: string;
  improvement: string;
  icon: string;
}

interface CaseStudy {
  id: string;
  title: string;
  company: string;
  industry: string;
  challenge: string;
  solution: string;
  implementation: string[];
  results: string;
  metrics: CaseStudyMetric[];
  testimonial?: {
    quote: string;
    author: string;
    role: string;
    avatar?: string;
  };
  tags: string[];
  crmUsed: string;
}

interface CaseStudyDisplayProps {
  caseStudies: CaseStudy[];
  className?: string;
}

const CaseStudyDisplay: React.FC<CaseStudyDisplayProps> = ({
  caseStudies,
  className = ''
}) => {
  const [selectedStudy, setSelectedStudy] = useState<CaseStudy>(caseStudies[0]);
  const [activeTab, setActiveTab] = useState<'overview' | 'implementation' | 'results'>('overview');

  const tabs = [
    { key: 'overview', label: 'Overview', icon: '📋' },
    { key: 'implementation', label: 'Implementation', icon: '⚙️' },
    { key: 'results', label: 'Results', icon: '📈' }
  ];

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Success Stories</h3>
        
        {/* Case Study Selector */}
        <div className="flex flex-wrap gap-2">
          {caseStudies.map((study) => (
            <button
              key={study.id}
              onClick={() => setSelectedStudy(study)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedStudy.id === study.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {study.company}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {/* Study Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-xl font-bold text-gray-900">{selectedStudy.title}</h4>
              <p className="text-gray-600">{selectedStudy.company} • {selectedStudy.industry}</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {selectedStudy.crmUsed}
              </span>
            </div>
          </div>
          
          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {selectedStudy.tags.map((tag, index) => (
              <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h5 className="font-semibold text-gray-900 mb-3">The Challenge</h5>
                <p className="text-gray-700 leading-relaxed">{selectedStudy.challenge}</p>
              </div>
              
              <div>
                <h5 className="font-semibold text-gray-900 mb-3">Our Solution</h5>
                <p className="text-gray-700 leading-relaxed">{selectedStudy.solution}</p>
              </div>

              {selectedStudy.testimonial && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-r-lg">
                  <blockquote className="text-lg text-blue-900 mb-4 italic">
                    "{selectedStudy.testimonial.quote}"
                  </blockquote>
                  <div className="flex items-center space-x-3">
                    {selectedStudy.testimonial.avatar && (
                      <img 
                        src={selectedStudy.testimonial.avatar} 
                        alt={selectedStudy.testimonial.author}
                        className="w-10 h-10 rounded-full"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-blue-900">
                        {selectedStudy.testimonial.author}
                      </div>
                      <div className="text-sm text-blue-700">
                        {selectedStudy.testimonial.role}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'implementation' && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-4">Implementation Steps</h5>
              <div className="space-y-4">
                {selectedStudy.implementation.map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-700">{step}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'results' && (
            <div className="space-y-6">
              <div>
                <h5 className="font-semibold text-gray-900 mb-3">Key Results</h5>
                <p className="text-gray-700 leading-relaxed mb-6">{selectedStudy.results}</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {selectedStudy.metrics.map((metric, index) => (
                  <div key={index} className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <span className="text-2xl">{metric.icon}</span>
                      <h6 className="font-semibold text-gray-900">{metric.label}</h6>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Before:</span>
                        <span className="font-medium text-red-600">{metric.before}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">After:</span>
                        <span className="font-medium text-green-600">{metric.after}</span>
                      </div>
                      <div className="pt-2 border-t border-gray-200">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Improvement:</span>
                          <span className="font-bold text-blue-600">{metric.improvement}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseStudyDisplay;
