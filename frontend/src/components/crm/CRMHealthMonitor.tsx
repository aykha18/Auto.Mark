import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  RefreshCw,
  Settings,
  BarChart3
} from 'lucide-react';
import { Card, Button } from '../ui';

interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'healthy' | 'warning' | 'critical';
  description: string;
}

interface IntegrationHealth {
  crmId: string;
  crmName: string;
  overallScore: number;
  metrics: HealthMetric[];
  lastUpdated: Date;
  alerts: string[];
}

const CRMHealthMonitor: React.FC = () => {
  const [healthData, setHealthData] = useState<IntegrationHealth[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock health data
  useEffect(() => {
    setHealthData([
      {
        crmId: 'pipedrive',
        crmName: 'Pipedrive',
        overallScore: 98,
        lastUpdated: new Date(),
        alerts: [],
        metrics: [
          {
            id: 'sync_latency',
            name: 'Sync Latency',
            value: 1.2,
            unit: 'seconds',
            trend: 'stable',
            status: 'healthy',
            description: 'Average time for data synchronization'
          },
          {
            id: 'api_success_rate',
            name: 'API Success Rate',
            value: 99.8,
            unit: '%',
            trend: 'up',
            status: 'healthy',
            description: 'Percentage of successful API calls'
          },
          {
            id: 'data_accuracy',
            name: 'Data Accuracy',
            value: 97.5,
            unit: '%',
            trend: 'stable',
            status: 'healthy',
            description: 'Accuracy of synchronized data'
          },
          {
            id: 'webhook_delivery',
            name: 'Webhook Delivery',
            value: 98.9,
            unit: '%',
            trend: 'up',
            status: 'healthy',
            description: 'Successful webhook deliveries'
          }
        ]
      },
      {
        crmId: 'hubspot',
        crmName: 'HubSpot',
        overallScore: 95,
        lastUpdated: new Date(Date.now() - 2 * 60 * 1000),
        alerts: ['Rate limit approaching'],
        metrics: [
          {
            id: 'sync_latency',
            name: 'Sync Latency',
            value: 2.1,
            unit: 'seconds',
            trend: 'up',
            status: 'warning',
            description: 'Average time for data synchronization'
          },
          {
            id: 'api_success_rate',
            name: 'API Success Rate',
            value: 98.2,
            unit: '%',
            trend: 'down',
            status: 'warning',
            description: 'Percentage of successful API calls'
          },
          {
            id: 'data_accuracy',
            name: 'Data Accuracy',
            value: 96.8,
            unit: '%',
            trend: 'stable',
            status: 'healthy',
            description: 'Accuracy of synchronized data'
          },
          {
            id: 'webhook_delivery',
            name: 'Webhook Delivery',
            value: 94.2,
            unit: '%',
            trend: 'down',
            status: 'warning',
            description: 'Successful webhook deliveries'
          }
        ]
      },
      {
        crmId: 'zoho',
        crmName: 'Zoho CRM',
        overallScore: 85,
        lastUpdated: new Date(Date.now() - 15 * 60 * 1000),
        alerts: ['Authentication token expired', 'Sync errors detected'],
        metrics: [
          {
            id: 'sync_latency',
            name: 'Sync Latency',
            value: 5.8,
            unit: 'seconds',
            trend: 'up',
            status: 'critical',
            description: 'Average time for data synchronization'
          },
          {
            id: 'api_success_rate',
            name: 'API Success Rate',
            value: 89.1,
            unit: '%',
            trend: 'down',
            status: 'critical',
            description: 'Percentage of successful API calls'
          },
          {
            id: 'data_accuracy',
            name: 'Data Accuracy',
            value: 92.3,
            unit: '%',
            trend: 'down',
            status: 'warning',
            description: 'Accuracy of synchronized data'
          },
          {
            id: 'webhook_delivery',
            name: 'Webhook Delivery',
            value: 78.5,
            unit: '%',
            trend: 'down',
            status: 'critical',
            description: 'Successful webhook deliveries'
          }
        ]
      }
    ]);
  }, [selectedTimeframe]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'critical':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />;
      case 'critical':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  const overallHealth = Math.round(
    healthData.reduce((sum, integration) => sum + integration.overallScore, 0) / healthData.length
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Integration Health Monitor</h2>
          <p className="text-gray-600">Real-time monitoring of CRM integration performance</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Timeframe Selector */}
          <div className="bg-gray-100 rounded-lg p-1">
            {(['1h', '24h', '7d', '30d'] as const).map((timeframe) => (
              <button
                key={timeframe}
                onClick={() => setSelectedTimeframe(timeframe)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  selectedTimeframe === timeframe
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {timeframe}
              </button>
            ))}
          </div>
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={handleRefresh}
            loading={isRefreshing}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Overall Health Score */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Overall Integration Health</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            overallHealth >= 90 ? 'bg-green-100 text-green-800' :
            overallHealth >= 70 ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {overallHealth >= 90 ? 'Excellent' :
             overallHealth >= 70 ? 'Good' : 'Needs Attention'}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-4xl font-bold text-gray-900">{overallHealth}%</div>
          <div className="flex-1">
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full ${
                  overallHealth >= 90 ? 'bg-green-500' :
                  overallHealth >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${overallHealth}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Integration Health Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {healthData.map((integration) => (
          <Card key={integration.crmId} className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{integration.crmName}</h4>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                integration.overallScore >= 90 ? 'bg-green-100 text-green-800' :
                integration.overallScore >= 70 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {integration.overallScore}%
              </div>
            </div>

            {/* Alerts */}
            {integration.alerts.length > 0 && (
              <div className="mb-4 space-y-2">
                {integration.alerts.map((alert, index) => (
                  <div key={index} className="flex items-center space-x-2 p-2 bg-red-50 rounded-lg">
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                    <span className="text-sm text-red-700">{alert}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Metrics */}
            <div className="space-y-3">
              {integration.metrics.map((metric) => (
                <div key={metric.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`p-1 rounded ${getStatusColor(metric.status)}`}>
                      {getStatusIcon(metric.status)}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{metric.name}</div>
                      <div className="text-xs text-gray-500">{metric.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-gray-900">
                      {metric.value}{metric.unit}
                    </span>
                    {getTrendIcon(metric.trend)}
                  </div>
                </div>
              ))}
            </div>

            {/* Last Updated */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Last updated: {integration.lastUpdated.toLocaleTimeString()}</span>
                <Button variant="ghost" size="sm" icon={Settings}>
                  Configure
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Performance Trends */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Performance Trends</h3>
          <Button variant="outline" size="sm" icon={BarChart3}>
            View Detailed Analytics
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">99.2%</div>
            <div className="text-sm text-gray-600">Avg Uptime</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">+0.3%</span>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">2.1s</div>
            <div className="text-sm text-gray-600">Avg Latency</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">-0.2s</span>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">15.2K</div>
            <div className="text-sm text-gray-600">Records/Hour</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">+12%</span>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">3</div>
            <div className="text-sm text-gray-600">Active Alerts</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">-2</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default CRMHealthMonitor;
