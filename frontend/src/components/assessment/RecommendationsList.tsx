import React from 'react';
import { CheckCircle, ArrowRight } from 'lucide-react';

interface RecommendationsListProps {
  title: string;
  items: string[];
  icon: string;
}

const RecommendationsList: React.FC<RecommendationsListProps> = ({
  title,
  items,
  icon,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-3">{icon}</span>
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
      </div>
      
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="flex items-start group hover:bg-gray-50 p-3 rounded-lg transition-colors">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-gray-700 leading-relaxed">{item}</p>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity ml-2 mt-1" />
          </div>
        ))}
      </div>
      
      {items.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No specific recommendations at this time.</p>
          <p className="text-sm mt-1">Your current setup looks good!</p>
        </div>
      )}
    </div>
  );
};

export default RecommendationsList;
