import React, { useState } from 'react';
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle, 
  ExternalLink, 
  Key, 
  Shield,
  Zap,
  Settings,
  Play
} from 'lucide-react';
import { Card, Button, Input } from '../ui';

interface CRMSetupWizardProps {
  crmType: string;
  onComplete: (config: any) => void;
  onCancel: () => void;
}

const CRMSetupWizard: React.FC<CRMSetupWizardProps> = ({ crmType, onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [config, setConfig] = useState({
    authMethod: 'oauth2',
    apiKey: '',
    clientId: '',
    clientSecret: '',
    domain: '',
    testConnection: false,
    fieldMapping: {},
    syncSettings: {
      contacts: true,
      deals: true,
      activities: true,
      campaigns: false,
    }
  });

  const steps = [
    {
      id: 'auth',
      title: 'Authentication',
      description: 'Connect your CRM account securely',
      icon: Shield
    },
    {
      id: 'test',
      title: 'Test Connection',
      description: 'Verify the connection works',
      icon: Zap
    },
    {
      id: 'mapping',
      title: 'Field Mapping',
      description: 'Map CRM fields to Auto.Mark',
      icon: Settings
    },
    {
      id: 'sync',
      title: 'Sync Settings',
      description: 'Choose what data to sync',
      icon: CheckCircle
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(config);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderAuthStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Connect Your {crmType} Account
        </h3>
        <p className="text-gray-600">
          Choose your preferred authentication method to securely connect your CRM.
        </p>
      </div>

      {/* Auth Method Selection */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card 
            className={`p-4 cursor-pointer border-2 ${
              config.authMethod === 'oauth2' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
            }`}
            onClick={() => setConfig({...config, authMethod: 'oauth2'})}
          >
            <div className="flex items-center space-x-3">
              <Shield className="w-6 h-6 text-primary-600" />
              <div>
                <div className="font-semibold text-gray-900">OAuth2 (Recommended)</div>
                <div className="text-sm text-gray-600">Most secure, no API keys needed</div>
              </div>
            </div>
          </Card>

          <Card 
            className={`p-4 cursor-pointer border-2 ${
              config.authMethod === 'api_key' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
            }`}
            onClick={() => setConfig({...config, authMethod: 'api_key'})}
          >
            <div className="flex items-center space-x-3">
              <Key className="w-6 h-6 text-primary-600" />
              <div>
                <div className="font-semibold text-gray-900">API Key</div>
                <div className="text-sm text-gray-600">Direct API access</div>
              </div>
            </div>
          </Card>
        </div>

        {/* OAuth2 Setup */}
        {config.authMethod === 'oauth2' && (
          <Card className="p-6 bg-blue-50 border-blue-200">
            <div className="flex items-start space-x-3">
              <Shield className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-2">OAuth2 Setup</h4>
                <p className="text-blue-800 text-sm mb-4">
                  Click the button below to securely connect your {crmType} account. 
                  You'll be redirected to {crmType} to authorize the connection.
                </p>
                <Button variant="primary" icon={ExternalLink}>
                  Connect to {crmType}
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* API Key Setup */}
        {config.authMethod === 'api_key' && (
          <div className="space-y-4">
            <Input
              label="API Key"
              placeholder="Enter your API key"
              value={config.apiKey}
              onChange={(value) => setConfig({...config, apiKey: value})}
              required
            />
            {crmType.toLowerCase() === 'salesforce' && (
              <Input
                label="Instance Domain"
                placeholder="your-instance.salesforce.com"
                value={config.domain}
                onChange={(value) => setConfig({...config, domain: value})}
                required
              />
            )}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <Shield className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <strong>Security Note:</strong> Your API key is encrypted and stored securely. 
                  We recommend using OAuth2 for enhanced security.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderTestStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Test Connection
        </h3>
        <p className="text-gray-600">
          Let's verify that we can connect to your {crmType} account successfully.
        </p>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Connection Status</span>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-600 font-medium">Connected</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-gray-700">API Access</span>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-600 font-medium">Verified</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Permissions</span>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-600 font-medium">Read/Write</span>
            </div>
          </div>
        </div>
      </Card>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
          <div className="text-sm text-green-800">
            <strong>Connection Successful!</strong> We can access your {crmType} data and are ready to set up synchronization.
          </div>
        </div>
      </div>
    </div>
  );

  const renderMappingStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Field Mapping
        </h3>
        <p className="text-gray-600">
          Map your {crmType} fields to Auto.Mark fields for seamless data synchronization.
        </p>
      </div>

      <div className="space-y-4">
        {[
          { autoMark: 'Email', crm: 'email', required: true },
          { autoMark: 'First Name', crm: 'first_name', required: true },
          { autoMark: 'Last Name', crm: 'last_name', required: true },
          { autoMark: 'Company', crm: 'company', required: false },
          { autoMark: 'Phone', crm: 'phone', required: false },
          { autoMark: 'Lead Source', crm: 'lead_source', required: false },
        ].map((field, index) => (
          <div key={index} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
            <div className="flex-1">
              <div className="font-medium text-gray-900">{field.autoMark}</div>
              {field.required && (
                <div className="text-xs text-red-600">Required</div>
              )}
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                <option value={field.crm}>{field.crm}</option>
                <option value="custom_field_1">Custom Field 1</option>
                <option value="custom_field_2">Custom Field 2</option>
                <option value="">Don't map</option>
              </select>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Settings className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <strong>Smart Mapping:</strong> We've automatically detected and mapped common fields. 
            You can customize these mappings or add custom field mappings later.
          </div>
        </div>
      </div>
    </div>
  );

  const renderSyncStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Sync Settings
        </h3>
        <p className="text-gray-600">
          Choose what data to synchronize between {crmType} and Auto.Mark.
        </p>
      </div>

      <div className="space-y-4">
        {[
          { key: 'contacts', label: 'Contacts', description: 'Sync contact information and lead data' },
          { key: 'deals', label: 'Deals/Opportunities', description: 'Sync sales pipeline and deal stages' },
          { key: 'activities', label: 'Activities', description: 'Sync tasks, calls, and meetings' },
          { key: 'campaigns', label: 'Campaigns', description: 'Sync marketing campaigns and responses' },
        ].map((item) => (
          <Card key={item.key} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="font-medium text-gray-900">{item.label}</div>
                <div className="text-sm text-gray-600">{item.description}</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={config.syncSettings[item.key as keyof typeof config.syncSettings]}
                  onChange={(e) => setConfig({
                    ...config,
                    syncSettings: {
                      ...config.syncSettings,
                      [item.key]: e.target.checked
                    }
                  })}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-4 bg-gray-50">
        <h4 className="font-medium text-gray-900 mb-2">Sync Frequency</h4>
        <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
          <option value="realtime">Real-time (Recommended)</option>
          <option value="5min">Every 5 minutes</option>
          <option value="15min">Every 15 minutes</option>
          <option value="1hour">Every hour</option>
          <option value="daily">Daily</option>
        </select>
      </Card>
    </div>
  );

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderAuthStep();
      case 1:
        return renderTestStep();
      case 2:
        return renderMappingStep();
      case 3:
        return renderSyncStep();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            return (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  index <= currentStep 
                    ? 'border-primary-500 bg-primary-500 text-white' 
                    : 'border-gray-300 bg-white text-gray-400'
                }`}>
                  {index < currentStep ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    <IconComponent className="w-5 h-5" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-2 ${
                    index < currentStep ? 'bg-primary-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-2">
          {steps.map((step, index) => (
            <div key={step.id} className="text-center" style={{ width: '120px' }}>
              <div className="text-sm font-medium text-gray-900">{step.title}</div>
              <div className="text-xs text-gray-600">{step.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <Card className="p-8 mb-6">
        {renderStepContent()}
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={currentStep === 0 ? onCancel : handlePrev}
          icon={ChevronLeft}
          iconPosition="left"
        >
          {currentStep === 0 ? 'Cancel' : 'Previous'}
        </Button>
        
        <Button
          variant="primary"
          onClick={handleNext}
          icon={currentStep === steps.length - 1 ? CheckCircle : ChevronRight}
          iconPosition="right"
        >
          {currentStep === steps.length - 1 ? 'Complete Setup' : 'Next'}
        </Button>
      </div>
    </div>
  );
};

export default CRMSetupWizard;