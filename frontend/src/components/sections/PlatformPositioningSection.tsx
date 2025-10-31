import React from 'react';
import { Zap, Link, Brain, BarChart3, Shield, Clock } from 'lucide-react';
import { Card } from '../ui';

const PlatformPositioningSection: React.FC = () => {
  const features = [
    {
      icon: Link,
      title: 'Universal CRM Integration',
      description: 'Connect Pipedrive, Zoho, HubSpot, Monday, Salesforce, or use our built-in NeuraCRM. 2-click setup, no coding required.',
      benefits: ['OAuth2 secure authentication', 'Real-time data sync', 'Field mapping automation'],
    },
    {
      icon: Brain,
      title: 'AI-Powered Automation',
      description: '24/7 lead nurturing with intelligent responses, predictive scoring, and personalized campaigns that adapt to each prospect.',
      benefits: ['GPT-4 powered conversations', 'Predictive lead scoring', 'Dynamic content generation'],
    },
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Real-time insights into campaign performance, lead quality, and ROI. Make data-driven decisions with comprehensive reporting.',
      benefits: ['Conversion funnel analysis', 'Lead source attribution', 'Performance optimization'],
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-level encryption, SOC 2 compliance, and secure API integrations. Your data stays protected across all systems.',
      benefits: ['End-to-end encryption', 'GDPR compliant', 'Regular security audits'],
    },
    {
      icon: Clock,
      title: 'Time-Saving Workflows',
      description: 'Automate repetitive tasks, eliminate manual data entry, and focus on high-value activities. Save 20+ hours per week.',
      benefits: ['Automated follow-ups', 'Smart task prioritization', 'Bulk operations'],
    },
    {
      icon: Zap,
      title: 'Instant Deployment',
      description: 'Get started in minutes, not months. Pre-built templates, guided setup, and expert support for rapid implementation.',
      benefits: ['One-click templates', 'Guided onboarding', '24/7 expert support'],
    },
  ];

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Zap className="w-4 h-4 mr-2" />
            Unitasa Platform
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            AI Marketing Automation That Actually Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Stop juggling disconnected tools. Unitasa unifies your marketing stack with intelligent automation 
            that works with any CRM, scales with your business, and delivers measurable results.
          </p>
        </div>

        {/* Value Proposition Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <Card key={index} className="p-6" hover>
                <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                  <IconComponent className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.benefits.map((benefit, benefitIndex) => (
                    <li key={benefitIndex} className="flex items-center text-sm text-gray-500">
                      <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-2"></div>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </Card>
            );
          })}
        </div>

        {/* Platform Comparison */}
        <div className="bg-gray-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Why Choose Unitasa Over Traditional Solutions?
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Feature</th>
                  <th className="text-center py-4 px-4 font-semibold text-primary-600">Unitasa</th>
                  <th className="text-center py-4 px-4 font-semibold text-gray-500">Traditional Tools</th>
                  <th className="text-center py-4 px-4 font-semibold text-gray-500">Custom Development</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="py-4 px-4 font-medium">CRM Integration</td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-green-600 font-semibold">2-click setup</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-500">Complex configuration</td>
                  <td className="py-4 px-4 text-center text-gray-500">Months of development</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 font-medium">AI Automation</td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-green-600 font-semibold">Built-in GPT-4</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-500">Basic rules only</td>
                  <td className="py-4 px-4 text-center text-gray-500">Expensive AI integration</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 font-medium">Setup Time</td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-green-600 font-semibold">Minutes</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-500">Weeks</td>
                  <td className="py-4 px-4 text-center text-gray-500">Months</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 font-medium">Ongoing Maintenance</td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-green-600 font-semibold">Fully managed</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-500">Manual updates</td>
                  <td className="py-4 px-4 text-center text-gray-500">Dedicated dev team</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 font-medium">Total Cost</td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-green-600 font-semibold">$497 lifetime*</span>
                    <div className="text-xs text-gray-500 line-through">Regular: $2,000+</div>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-500">$500+/month</td>
                  <td className="py-4 px-4 text-center text-gray-500">$50,000+</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <p className="text-sm text-gray-500 mt-4 text-center">
            *Co-creator program pricing. Regular pricing will be higher after launch.
          </p>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Transform Your Marketing?
          </h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of businesses that have automated their lead generation and scaled their growth with Unitasa.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition-colors">
              Start Free Assessment
            </button>
            <button className="border-2 border-primary-600 text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-50 transition-colors">
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PlatformPositioningSection;
