import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Clock, RefreshCw, Settings, ExternalLink } from 'lucide-react';
import { Card, Button } from '../ui';

interface ConnectionStatus {
  id: string;
  crmName: string;
  status: 'connected' | 'disconnected' | 'error' | 'syncing';
  lastSync: Date;
  recordsSynced: number;
  errors: string[];
  healthScore: number;
}

interface CRMConnectionStatusProps {
  connections?: ConnectionStatus[];
}

const CRMConnectionStatus: React.FC<CRMConnectionStatusProps> = ({ connections = [] }) => {
  const [connectionStatuses, setConnectionStatuses] = useState<ConnectionStatus[]>(connections);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    if (connections.length === 0) {
      setConnectionStatuses([
        {
          id: 'pipedrive-1',
          crmName: 'Pipedrive',
          status: 'connected',
          lastSync: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
          recordsSynced: 1247,
          errors: [],
          healthScore: 98
        },
        {
          id: 'hubspot-1',
          crmName: 'HubSpot',
          status: 'syncing',
          lastSync: new Date(Date.now() - 2 * 60 * 1000), // 2 minutes ago
          recordsSynced: 892,
          errors: [],
          healthScore: 95
        },
        {
          id: 'zoho-1',
          crmName: 'Zoho CRM',
          status: 'error',
          lastSync: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
          recordsSynced: 0,
          errors: ['API rate limit exceeded', 'Authentication token expired'],
          healthScore: 45
        }
      ]);
    }
  }, [connections]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'syncing':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'disconnected':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'syncing':
        return 'Syncing...';
      case 'error':
        return 'Error';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-600 bg-green-50';
      case 'syncing':
        return 'text-blue-600 bg-blue-50';
      case 'error':
        return 'text-red-600 bg-red-50';
      case 'disconnected':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatLastSync = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  const handleReconnect = (connectionId: string) => {
    // Handle reconnection logic
    console.log('Reconnecting:', connectionId);
  };

  const handleConfigure = (connectionId: string) => {
    // Handle configuration logic
    console.log('Configuring:', connectionId);
  };

  if (connectionStatuses.length === 0) {
    return (
      <Card className="p-8 text-center">
        <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <Settings className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No CRM Connections</h3>
        <p className="text-gray-600 mb-6">
          Connect your first CRM to start automating your marketing workflows.
        </p>
        <Button variant="primary" icon={ExternalLink}>
          Browse CRM Integrations
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">CRM Connection Status</h3>
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

      {/* Connection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {connectionStatuses.map((connection) => (
          <Card key={connection.id} className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{connection.crmName}</h4>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(connection.status)}`}>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(connection.status)}
                  <span>{getStatusText(connection.status)}</span>
                </div>
              </div>
            </div>

            {/* Health Score */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Health Score</span>
                <span className={`font-semibold ${getHealthScoreColor(connection.healthScore)}`}>
                  {connection.healthScore}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    connection.healthScore >= 90
                      ? 'bg-green-500'
                      : connection.healthScore >= 70
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${connection.healthScore}%` }}
                />
              </div>
            </div>

            {/* Sync Info */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Last Sync</span>
                <span className="text-gray-900">{formatLastSync(connection.lastSync)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Records Synced</span>
                <span className="text-gray-900">{connection.recordsSynced.toLocaleString()}</span>
              </div>
            </div>

            {/* Errors */}
            {connection.errors.length > 0 && (
              <div className="mb-4">
                <div className="text-sm text-red-600 font-medium mb-2">Issues:</div>
                <ul className="space-y-1">
                  {connection.errors.map((error, index) => (
                    <li key={index} className="text-xs text-red-600 flex items-start">
                      <AlertCircle className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
                      {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-2">
              {connection.status === 'error' || connection.status === 'disconnected' ? (
                <Button
                  variant="primary"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleReconnect(connection.id)}
                >
                  Reconnect
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  icon={Settings}
                  onClick={() => handleConfigure(connection.id)}
                >
                  Configure
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <Card className="p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Integration Summary</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {connectionStatuses.filter(c => c.status === 'connected').length}
            </div>
            <div className="text-sm text-gray-600">Connected</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {connectionStatuses.filter(c => c.status === 'syncing').length}
            </div>
            <div className="text-sm text-gray-600">Syncing</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {connectionStatuses.filter(c => c.status === 'error').length}
            </div>
            <div className="text-sm text-gray-600">Errors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {connectionStatuses.reduce((sum, c) => sum + c.recordsSynced, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Records</div>
          </div>
        </div>

        {/* Overall Health Score */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium text-gray-900">Overall Integration Health</span>
            <span className="text-lg font-bold text-green-600">
              {Math.round(connectionStatuses.reduce((sum, c) => sum + c.healthScore, 0) / connectionStatuses.length)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="h-3 rounded-full bg-gradient-to-r from-green-500 to-blue-500"
              style={{ 
                width: `${Math.round(connectionStatuses.reduce((sum, c) => sum + c.healthScore, 0) / connectionStatuses.length)}%` 
              }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Poor</span>
            <span>Good</span>
            <span>Excellent</span>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Quick Actions</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button variant="primary" icon={ExternalLink} className="w-full">
            Add New Integration
          </Button>
          <Button variant="outline" icon={Settings} className="w-full">
            Bulk Configuration
          </Button>
          <Button variant="outline" icon={RefreshCw} className="w-full">
            Sync All Connections
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default CRMConnectionStatus;
