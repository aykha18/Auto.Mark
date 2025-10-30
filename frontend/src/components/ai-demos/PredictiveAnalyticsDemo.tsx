import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, Users, DollarSign } from 'lucide-react';

interface Lead {
  id: string;
  name: string;
  email: string;
  score: number;
  conversionProbability: number;
  predictedValue: number;
  source: string;
  status: 'hot' | 'warm' | 'cold';
}

const PredictiveAnalyticsDemo: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analytics, setAnalytics] = useState({
    totalLeads: 0,
    hotLeads: 0,
    predictedRevenue: 0,
    conversionRate: 0
  });

  const sampleLeads: Lead[] = [
    {
      id: '1',
      name: 'Sarah Johnson',
      email: 'sarah.j@techcorp.com',
      score: 94,
      conversionProbability: 87,
      predictedValue: 15400,
      source: 'LinkedIn',
      status: 'hot'
    },
    {
      id: '2',
      name: 'Mike Chen',
      email: 'mchen@startup.io',
      score: 78,
      conversionProbability: 65,
      predictedValue: 8900,
      source: 'Google Ads',
      status: 'warm'
    },
    {
      id: '3',
      name: 'Emily Rodriguez',
      email: 'emily.r@enterprise.com',
      score: 91,
      conversionProbability: 82,
      predictedValue: 22100,
      source: 'Referral',
      status: 'hot'
    },
    {
      id: '4',
      name: 'David Kim',
      email: 'dkim@agency.net',
      score: 56,
      conversionProbability: 34,
      predictedValue: 4200,
      source: 'Facebook',
      status: 'cold'
    },
    {
      id: '5',
      name: 'Lisa Thompson',
      email: 'lisa.t@consulting.biz',
      score: 85,
      conversionProbability: 73,
      predictedValue: 12800,
      source: 'Email Campaign',
      status: 'warm'
    }
  ];

  const runAnalysis = () => {
    setIsAnalyzing(true);
    setLeads([]);
    
    setTimeout(() => {
      setLeads(sampleLeads);
      setAnalytics({
        totalLeads: sampleLeads.length,
        hotLeads: sampleLeads.filter(lead => lead.status === 'hot').length,
        predictedRevenue: sampleLeads.reduce((sum, lead) => sum + (lead.predictedValue * lead.conversionProbability / 100), 0),
        conversionRate: sampleLeads.reduce((sum, lead) => sum + lead.conversionProbability, 0) / sampleLeads.length
      });
      setIsAnalyzing(false);
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'hot': return 'text-red-600 bg-red-100';
      case 'warm': return 'text-orange-600 bg-orange-100';
      case 'cold': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Target className="w-6 h-6 text-purple-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">
            Predictive Lead Intelligence
          </h3>
        </div>
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          {isAnalyzing ? 'Analyzing...' : 'Run AI Analysis'}
        </button>
      </div>

      {/* Analytics Overview */}
      {leads.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <Users className="w-5 h-5 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-600">{analytics.totalLeads}</div>
            <div className="text-xs text-gray-600">Total Leads</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <TrendingUp className="w-5 h-5 text-red-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-red-600">{analytics.hotLeads}</div>
            <div className="text-xs text-gray-600">Hot Leads</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <DollarSign className="w-5 h-5 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-600">
              ${analytics.predictedRevenue.toLocaleString()}
            </div>
            <div className="text-xs text-gray-600">Predicted Revenue</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <Target className="w-5 h-5 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-600">
              {analytics.conversionRate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600">Avg. Conversion Rate</div>
          </div>
        </div>
      )}

      {/* Lead Analysis Results */}
      {isAnalyzing && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI is analyzing lead behavior patterns...</p>
        </div>
      )}

      {leads.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900 mb-3">AI Lead Scoring Results</h4>
          {leads.map((lead) => (
            <div
              key={lead.id}
              className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h5 className="font-medium text-gray-900">{lead.name}</h5>
                  <p className="text-sm text-gray-600">{lead.email}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
                  {lead.status.toUpperCase()}
                </span>
              </div>
              
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">AI Score:</span>
                  <div className="font-semibold text-gray-900">{lead.score}/100</div>
                </div>
                <div>
                  <span className="text-gray-500">Conversion Prob:</span>
                  <div className="font-semibold text-gray-900">{lead.conversionProbability}%</div>
                </div>
                <div>
                  <span className="text-gray-500">Predicted Value:</span>
                  <div className="font-semibold text-gray-900">${lead.predictedValue.toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-gray-500">Source:</span>
                  <div className="font-semibold text-gray-900">{lead.source}</div>
                </div>
              </div>
              
              {/* Conversion Probability Bar */}
              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Conversion Probability</span>
                  <span>{lead.conversionProbability}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      lead.conversionProbability >= 80 ? 'bg-red-500' :
                      lead.conversionProbability >= 60 ? 'bg-orange-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${lead.conversionProbability}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {leads.length === 0 && !isAnalyzing && (
        <div className="text-center py-8 text-gray-500">
          Click "Run AI Analysis" to see predictive lead intelligence in action
        </div>
      )}
    </div>
  );
};

export default PredictiveAnalyticsDemo;