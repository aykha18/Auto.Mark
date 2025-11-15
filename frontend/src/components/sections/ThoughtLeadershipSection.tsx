import React, { useState } from 'react';
import {
  TechnicalDemo,
  RoadmapPresentation,
  CaseStudyDisplay,
  DevelopmentStatusTracker,
  SupporterCommunicationSystem,
  InteractiveFounderTimeline
} from '../thought-leadership';
import ConsultationBooking from '../booking/ConsultationBooking';

// Mock data - in a real app, this would come from props or API
const mockTechnicalDemoSteps = [
  {
    id: '1',
    title: 'CRM Connection',
    description: 'Establish secure connection to your existing CRM system',
    code: `// Unitasa CRM Integration
const crmConnection = await unitasa.connect({
  provider: 'salesforce',
  credentials: { apiKey, instanceUrl },
  syncInterval: '5min'
});`,
    metrics: [
      { label: 'Setup Time', value: '< 5 min', improvement: '90% faster' },
      { label: 'Data Sync', value: 'Real-time', improvement: 'vs 24hr delay' }
    ]
  },
  {
    id: '2',
    title: 'AI Analysis',
    description: 'AI analyzes your lead data and identifies automation opportunities',
    visual: '🤖',
    metrics: [
      { label: 'Leads Analyzed', value: '10,000+', improvement: 'in seconds' },
      { label: 'Patterns Found', value: '47', improvement: 'actionable insights' }
    ]
  },
  {
    id: '3',
    title: 'Automation Setup',
    description: 'Automated workflows are created and deployed',
    code: `// Automated lead nurturing workflow
const workflow = autoMark.createWorkflow({
  trigger: 'new_lead',
  conditions: ['score > 70', 'industry = "tech"'],
  actions: ['send_welcome_email', 'schedule_demo', 'notify_sales']
});`,
    metrics: [
      { label: 'Workflows Created', value: '12', improvement: 'automatically' },
      { label: 'Response Time', value: '< 1 min', improvement: 'vs 2-3 days' }
    ]
  }
];

const mockRoadmapItems = [
  {
    id: '1',
    title: 'Advanced CRM Integrations',
    description: 'Deep integration with Salesforce, HubSpot, and Pipedrive',
    status: 'completed' as const,
    quarter: 'Q1 2025',
    features: ['OAuth2 authentication', 'Real-time sync', 'Custom field mapping', 'Webhook support'],
    impact: 'Seamless data flow',
    foundingUserInfluence: true
  },
  {
    id: '2',
    title: 'AI-Powered Lead Scoring',
    description: 'Machine learning algorithms for intelligent lead qualification',
    status: 'in_progress' as const,
    quarter: 'Q2 2025',
    features: ['Predictive scoring', 'Behavioral analysis', 'Custom scoring models', 'A/B testing'],
    impact: '40% improvement in conversion rates',
    foundingUserInfluence: true
  },
  {
    id: '3',
    title: 'Multi-Channel Automation',
    description: 'Unified automation across email, SMS, social media, and phone',
    status: 'planned' as const,
    quarter: 'Q3 2025',
    features: ['Email sequences', 'SMS campaigns', 'Social media posting', 'Voice calls'],
    impact: '3x increase in touchpoints',
    foundingUserInfluence: false
  }
];

const mockCaseStudies = [
  {
    id: '1',
    title: 'SaaS Startup Scales Lead Generation 10x',
    company: 'TechFlow Solutions',
    industry: 'SaaS',
    challenge: 'Manual lead qualification was taking 40+ hours per week, causing delays in follow-up and lost opportunities.',
    solution: 'Implemented Unitasa with Salesforce integration for automated lead scoring and nurturing workflows.',
    implementation: [
      'Connected Salesforce CRM with OAuth2 authentication',
      'Set up AI-powered lead scoring based on company size, industry, and behavior',
      'Created automated email sequences for different lead segments',
      'Implemented real-time notifications for high-value prospects'
    ],
    results: 'Reduced manual work by 85%, increased qualified leads by 300%, and improved response time from 2 days to 5 minutes.',
    metrics: [
      { label: 'Lead Volume', before: '50/month', after: '500/month', improvement: '10x increase', icon: '📈' },
      { label: 'Response Time', before: '2 days', after: '5 minutes', improvement: '99% faster', icon: '⚡' },
      { label: 'Conversion Rate', before: '2%', after: '8%', improvement: '4x better', icon: '🎯' },
      { label: 'Time Saved', before: '40 hrs/week', after: '6 hrs/week', improvement: '85% reduction', icon: '⏰' }
    ],
    testimonial: {
      quote: 'Unitasa transformed our entire sales process. We went from drowning in leads to having a systematic, automated approach that actually works.',
      author: 'Sarah Chen',
      role: 'VP of Sales'
    },
    tags: ['SaaS', 'Salesforce', 'Lead Scoring', 'Email Automation'],
    crmUsed: 'Salesforce'
  }
];

const mockMilestones = [
  {
    id: '1',
    date: new Date('2025-04-15'),
    title: 'The Problem Discovery',
    description: 'Realized the pain of disconnected marketing tools while managing multiple client campaigns',
    metrics: {
      leadsGenerated: 100,
      crmIntegrations: 0,
      automationLevel: 10,
      timesSaved: 1
    },
    technologies: ['Manual processes', 'Spreadsheets', 'Basic email tools'],
    integrationChallenges: ['Data scattered across 5 different tools', 'Manual data entry taking 20+ hours/week'],
    lessonLearned: 'The biggest bottleneck in marketing automation is data integration, not the automation itself.'
  },
  {
    id: '2',
    date: new Date('2025-07-01'),
    title: 'First Integration Success',
    description: 'Built the first working CRM integration with Pipedrive using their REST API',
    metrics: {
      leadsGenerated: 500,
      crmIntegrations: 1,
      automationLevel: 40,
      timesSaved: 3
    },
    technologies: ['Python', 'Pipedrive API', 'PostgreSQL', 'FastAPI'],
    integrationChallenges: ['OAuth2 implementation complexity', 'Rate limiting and pagination'],
    lessonLearned: 'Start with one CRM and perfect the integration before expanding to others.'
  },
  {
    id: '3',
    date: new Date('2025-10-01'),
    title: 'Multi-CRM Platform',
    description: 'Successfully integrated with 5 major CRM systems and launched beta version',
    metrics: {
      leadsGenerated: 2500,
      crmIntegrations: 5,
      automationLevel: 80,
      timesSaved: 10
    },
    technologies: ['React', 'TypeScript', 'Docker', 'Railway', 'OpenAI GPT-4'],
    integrationChallenges: ['Different API patterns across CRMs', 'Field mapping complexity', 'Error handling'],
    lessonLearned: 'Standardizing the integration layer is crucial for scaling across multiple CRM platforms.'
  }
];

const mockDevelopmentMilestones = [
  {
    id: '1',
    title: 'Core CRM Integration Framework',
    description: 'Build the foundational integration system supporting major CRMs',
    status: 'completed' as const,
    completedDate: new Date('2025-04-15'),
    progress: 100,
    category: 'backend' as const,
    dependencies: ['API research', 'Authentication system']
  },
  {
    id: '2',
    title: 'AI Lead Scoring Engine',
    description: 'Implement machine learning algorithms for intelligent lead qualification',
    status: 'in_progress' as const,
    progress: 75,
    category: 'backend' as const,
    blockers: ['Training data collection'],
    dependencies: ['CRM data sync']
  },
  {
    id: '3',
    title: 'React Frontend Dashboard',
    description: 'Build responsive dashboard for managing integrations and viewing analytics',
    status: 'in_progress' as const,
    progress: 60,
    category: 'frontend' as const,
    estimatedDate: new Date('2025-04-01')
  }
];

const mockRecentUpdates = [
  {
    id: '1',
    date: new Date('2025-04-20'),
    title: 'Salesforce Integration Enhanced',
    description: 'Added support for custom objects and improved field mapping capabilities',
    type: 'feature' as const,
    impact: 'high' as const
  },
  {
    id: '2',
    date: new Date('2025-04-18'),
    title: 'Performance Optimization',
    description: 'Reduced API response times by 40% through caching improvements',
    type: 'improvement' as const,
    impact: 'medium' as const
  }
];

const mockSupporterMessages = [
  {
    id: '1',
    title: 'New Feature: Advanced Lead Scoring',
    content: 'We\'ve just released the advanced lead scoring feature that many of you requested. This uses machine learning to analyze lead behavior and assign more accurate scores.',
    date: new Date('2025-04-15'),
    type: 'update' as const,
    priority: 'high' as const,
    readStatus: false
  }
];

const mockFeedbackRequests = [
  {
    id: '1',
    title: 'CRM Integration Priority Vote',
    description: 'Help us decide which CRM integration to prioritize next',
    type: 'feature_vote' as const,
    deadline: new Date('2025-05-01'),
    responses: 12,
    maxResponses: 25,
    status: 'open' as const
  }
];

interface ThoughtLeadershipSectionProps {
  isCoCreator?: boolean;
}

const ThoughtLeadershipSection: React.FC<ThoughtLeadershipSectionProps> = ({
  isCoCreator = false
}) => {
  const [activeDemo, setActiveDemo] = useState<'technical' | 'roadmap' | 'cases' | 'status' | 'communication' | 'timeline'>('technical');
  const [showConsultation, setShowConsultation] = useState(false);

  const demos = [
    { key: 'technical', label: 'Technical Demo', icon: '⚙️' },
    { key: 'roadmap', label: 'Product Roadmap', icon: '🗺️' },
    { key: 'cases', label: 'Success Stories', icon: '📈' },
    { key: 'status', label: 'Development Status', icon: '🚧' },
    { key: 'communication', label: 'Co-Creator Hub', icon: '👥' },
    { key: 'timeline', label: 'Founder Journey', icon: '🚀' }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Transparent Development & Thought Leadership
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See exactly how we're building the future of AI marketing automation. 
            From technical demos to real success stories, we believe in complete transparency.
          </p>
        </div>

        {/* Demo Navigation */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {demos.map((demo) => (
            <button
              key={demo.key}
              onClick={() => setActiveDemo(demo.key as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeDemo === demo.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border'
              }`}
            >
              <span>{demo.icon}</span>
              <span>{demo.label}</span>
            </button>
          ))}
        </div>

        {/* Demo Content */}
        <div className="max-w-6xl mx-auto">
          {activeDemo === 'technical' && (
            <TechnicalDemo
              title="Unitasa Integration Demo"
              description="See how Unitasa connects to your CRM and automates your marketing in under 5 minutes"
              steps={mockTechnicalDemoSteps}
            />
          )}

          {activeDemo === 'roadmap' && (
            <RoadmapPresentation
              title="Product Roadmap"
              subtitle="Our transparent development plan with co-creator influence opportunities"
              roadmapItems={mockRoadmapItems}
            />
          )}

          {activeDemo === 'cases' && (
            <CaseStudyDisplay caseStudies={mockCaseStudies} />
          )}

          {activeDemo === 'status' && (
            <DevelopmentStatusTracker
              milestones={mockDevelopmentMilestones}
              recentUpdates={mockRecentUpdates}
            />
          )}

          {activeDemo === 'communication' && (
            <SupporterCommunicationSystem
              messages={mockSupporterMessages}
              feedbackRequests={mockFeedbackRequests}
              isCoCreator={isCoCreator}
              onJoinProgram={() => window.dispatchEvent(new CustomEvent('openLeadCapture'))}
            />
          )}

          {activeDemo === 'timeline' && (
            <InteractiveFounderTimeline milestones={mockMilestones} />
          )}
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <div className="bg-white rounded-xl shadow-lg border p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Join the Journey
            </h3>
            <p className="text-gray-600 mb-6">
              Become a co-creator and directly influence the development of Unitasa. 
              Your feedback shapes our roadmap and helps build the future of marketing automation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => window.dispatchEvent(new CustomEvent('openLeadCapture'))}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Take Assessment
              </button>
              <button 
                onClick={() => setShowConsultation(true)}
                className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                Schedule Demo
              </button>
            </div>
          </div>
        </div>

        {/* Consultation Booking Modal */}
        <ConsultationBooking 
          isOpen={showConsultation}
          onClose={() => setShowConsultation(false)} 
        />
      </div>
    </section>
  );
};

export default ThoughtLeadershipSection;
