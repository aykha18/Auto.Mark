import React, { useState } from 'react';
import { 
  BookOpen, 
  Code, 
  ExternalLink, 
  Copy, 
  CheckCircle,
  Play,
  Download,
  Github
} from 'lucide-react';
import { Layout } from '../components/layout';
import { Card, Button } from '../components/ui';

const CRMDocumentation: React.FC = () => {
  const [selectedCRM, setSelectedCRM] = useState('pipedrive');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const crmDocs = {
    pipedrive: {
      name: 'Pipedrive',
      logo: '🔶',
      setupTime: '5 minutes',
      difficulty: 'Easy',
      authMethod: 'OAuth2',
      endpoints: [
        { name: 'Persons', endpoint: '/persons', description: 'Manage contacts and leads' },
        { name: 'Deals', endpoint: '/deals', description: 'Access sales pipeline data' },
        { name: 'Activities', endpoint: '/activities', description: 'Track tasks and meetings' },
        { name: 'Pipelines', endpoint: '/pipelines', description: 'Manage sales stages' }
      ],
      codeExample: `// Initialize Pipedrive connection
const pipedrive = new PipedriveConnector({
  apiToken: 'your-api-token',
  companyDomain: 'your-company'
});

// Sync contacts
const contacts = await pipedrive.getPersons({
  limit: 100,
  start: 0
});

// Create new deal
const deal = await pipedrive.createDeal({
  title: 'New Opportunity',
  person_id: 123,
  value: 5000,
  currency: 'USD'
});`,
      webhooks: [
        'person.added',
        'person.updated',
        'deal.added',
        'deal.updated',
        'activity.added'
      ]
    },
    hubspot: {
      name: 'HubSpot',
      logo: '🟠',
      setupTime: '3 minutes',
      difficulty: 'Easy',
      authMethod: 'OAuth2',
      endpoints: [
        { name: 'Contacts', endpoint: '/contacts/v1/contact', description: 'Manage contact records' },
        { name: 'Companies', endpoint: '/companies/v2/companies', description: 'Company information' },
        { name: 'Deals', endpoint: '/deals/v1/deal', description: 'Sales opportunities' },
        { name: 'Engagements', endpoint: '/engagements/v1/engagements', description: 'Track interactions' }
      ],
      codeExample: `// Initialize HubSpot connection
const hubspot = new HubSpotConnector({
  accessToken: 'your-access-token',
  portalId: 'your-portal-id'
});

// Get contacts
const contacts = await hubspot.getContacts({
  limit: 100,
  properties: ['email', 'firstname', 'lastname', 'company']
});

// Create contact
const contact = await hubspot.createContact({
  properties: {
    email: 'contact@example.com',
    firstname: 'John',
    lastname: 'Doe'
  }
});`,
      webhooks: [
        'contact.creation',
        'contact.propertyChange',
        'deal.creation',
        'deal.propertyChange',
        'company.creation'
      ]
    },
    zoho: {
      name: 'Zoho CRM',
      logo: '🔵',
      setupTime: '8 minutes',
      difficulty: 'Medium',
      authMethod: 'OAuth2',
      endpoints: [
        { name: 'Contacts', endpoint: '/Contacts', description: 'Contact management' },
        { name: 'Accounts', endpoint: '/Accounts', description: 'Company accounts' },
        { name: 'Deals', endpoint: '/Deals', description: 'Sales opportunities' },
        { name: 'Leads', endpoint: '/Leads', description: 'Lead management' }
      ],
      codeExample: `// Initialize Zoho CRM connection
const zoho = new ZohoCRMConnector({
  accessToken: 'your-access-token',
  refreshToken: 'your-refresh-token',
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
  domain: 'zohoapis.com'
});

// Get contacts
const contacts = await zoho.getRecords('Contacts', {
  page: 1,
  per_page: 200
});

// Create lead
const lead = await zoho.createRecord('Leads', {
  Last_Name: 'Smith',
  Email: 'lead@example.com',
  Company: 'Example Corp'
});`,
      webhooks: [
        'Contacts.create',
        'Contacts.edit',
        'Deals.create',
        'Deals.edit',
        'Leads.create'
      ]
    }
  };

  const currentDoc = crmDocs[selectedCRM as keyof typeof crmDocs];

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <Layout>
      <div className="bg-white min-h-screen">
        {/* Header */}
        <div className="bg-gray-50 border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center space-x-3 mb-4">
              <BookOpen className="w-8 h-8 text-primary-600" />
              <h1 className="text-3xl font-bold text-gray-900">CRM Integration Documentation</h1>
            </div>
            <p className="text-xl text-gray-600 max-w-3xl">
              Complete guides, code examples, and API references for integrating your CRM with Unitasa.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <Card className="p-4 sticky top-4">
                <h3 className="font-semibold text-gray-900 mb-4">CRM Platforms</h3>
                <nav className="space-y-2">
                  {Object.entries(crmDocs).map(([key, crm]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedCRM(key)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        selectedCRM === key
                          ? 'bg-primary-100 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <span className="text-lg">{crm.logo}</span>
                      <span className="font-medium">{crm.name}</span>
                    </button>
                  ))}
                </nav>

                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-3">Quick Links</h4>
                  <div className="space-y-2">
                    <a href="#setup" className="block text-sm text-primary-600 hover:text-primary-700">
                      Setup Guide
                    </a>
                    <a href="#endpoints" className="block text-sm text-primary-600 hover:text-primary-700">
                      API Endpoints
                    </a>
                    <a href="#examples" className="block text-sm text-primary-600 hover:text-primary-700">
                      Code Examples
                    </a>
                    <a href="#webhooks" className="block text-sm text-primary-600 hover:text-primary-700">
                      Webhooks
                    </a>
                  </div>
                </div>
              </Card>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-3 space-y-8">
              {/* Overview */}
              <Card className="p-8">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="text-4xl">{currentDoc.logo}</div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{currentDoc.name} Integration</h2>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                        {currentDoc.difficulty} Setup
                      </span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                        {currentDoc.setupTime}
                      </span>
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
                        {currentDoc.authMethod}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="primary" icon={Play} className="w-full">
                    Start Integration
                  </Button>
                  <Button variant="outline" icon={Download} className="w-full">
                    Download SDK
                  </Button>
                  <Button variant="outline" icon={Github} className="w-full">
                    View on GitHub
                  </Button>
                </div>
              </Card>

              {/* Setup Guide */}
              <Card className="p-8" id="setup">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Setup Guide</h3>
                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="bg-primary-100 text-primary-600 w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm">
                      1
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Create API Credentials</h4>
                      <p className="text-gray-600 mb-3">
                        Log into your {currentDoc.name} account and navigate to the API settings to create new credentials.
                      </p>
                      <Button variant="outline" size="sm" icon={ExternalLink}>
                        Open {currentDoc.name} API Settings
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="bg-primary-100 text-primary-600 w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm">
                      2
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Configure Unitasa</h4>
                      <p className="text-gray-600 mb-3">
                        Add your {currentDoc.name} credentials to Unitasa and test the connection.
                      </p>
                      <Button variant="outline" size="sm" icon={Play}>
                        Test Connection
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="bg-primary-100 text-primary-600 w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm">
                      3
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Start Syncing</h4>
                      <p className="text-gray-600">
                        Configure field mappings and sync settings to begin automated data synchronization.
                      </p>
                    </div>
                  </div>
                </div>
              </Card>

              {/* API Endpoints */}
              <Card className="p-8" id="endpoints">
                <h3 className="text-xl font-bold text-gray-900 mb-6">API Endpoints</h3>
                <div className="space-y-4">
                  {currentDoc.endpoints.map((endpoint, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{endpoint.name}</h4>
                        <code className="bg-gray-100 px-2 py-1 rounded text-sm text-gray-700">
                          {endpoint.endpoint}
                        </code>
                      </div>
                      <p className="text-gray-600 text-sm">{endpoint.description}</p>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Code Examples */}
              <Card className="p-8" id="examples">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Code Examples</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    icon={copiedCode === 'main' ? CheckCircle : Copy}
                    onClick={() => copyToClipboard(currentDoc.codeExample, 'main')}
                  >
                    {copiedCode === 'main' ? 'Copied!' : 'Copy Code'}
                  </Button>
                </div>
                <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
                  <pre className="text-green-400 text-sm">
                    <code>{currentDoc.codeExample}</code>
                  </pre>
                </div>
              </Card>

              {/* Webhooks */}
              <Card className="p-8" id="webhooks">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Supported Webhooks</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentDoc.webhooks.map((webhook, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <code className="text-sm text-gray-700">{webhook}</code>
                    </div>
                  ))}
                </div>
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">Real-time Updates</h4>
                  <p className="text-blue-800 text-sm">
                    Configure webhooks to receive real-time notifications when data changes in your {currentDoc.name} account.
                    This enables instant synchronization and automated workflows.
                  </p>
                </div>
              </Card>

              {/* SDK and Tools */}
              <Card className="p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Developer Tools & SDKs</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Code className="w-6 h-6 text-blue-600" />
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Python SDK</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Full-featured Python library for {currentDoc.name} integration
                    </p>
                    <Button variant="outline" size="sm" icon={Download}>
                      Download SDK
                    </Button>
                  </div>
                  
                  <div className="text-center">
                    <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Code className="w-6 h-6 text-green-600" />
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Node.js SDK</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      JavaScript/TypeScript library with full type support
                    </p>
                    <Button variant="outline" size="sm" icon={Download}>
                      Download SDK
                    </Button>
                  </div>
                  
                  <div className="text-center">
                    <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                      <BookOpen className="w-6 h-6 text-purple-600" />
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Postman Collection</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Ready-to-use API collection for testing and development
                    </p>
                    <Button variant="outline" size="sm" icon={ExternalLink}>
                      Import Collection
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Support */}
              <Card className="p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Developer Support</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Integration Support</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Get personalized help setting up your {currentDoc.name} integration.
                    </p>
                    <Button variant="primary" size="sm">
                      Contact Support
                    </Button>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Developer Community</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Join our developer community for tips, examples, and best practices.
                    </p>
                    <Button variant="outline" size="sm" icon={ExternalLink}>
                      Join Community
                    </Button>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Live Chat Support</h4>
                    <p className="text-gray-600 text-sm mb-4">
                      Get instant help from our integration specialists.
                    </p>
                    <Button variant="outline" size="sm">
                      Start Chat
                    </Button>
                  </div>
                </div>
                
                {/* Support Stats */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-primary-600">&lt; 2h</div>
                      <div className="text-sm text-gray-600">Avg Response Time</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-primary-600">98%</div>
                      <div className="text-sm text-gray-600">Success Rate</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-primary-600">24/7</div>
                      <div className="text-sm text-gray-600">Support Available</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-primary-600">500+</div>
                      <div className="text-sm text-gray-600">Integrations Completed</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CRMDocumentation;
