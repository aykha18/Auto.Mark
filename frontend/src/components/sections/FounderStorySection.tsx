import React, { useState } from 'react';
import { Calendar, TrendingUp, Users, Zap, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card } from '../ui';

interface Milestone {
  id: string;
  date: string;
  title: string;
  description: string;
  metrics: {
    leadsGenerated?: number;
    crmIntegrations?: number;
    automationLevel?: number;
    timesSaved?: number;
  };
  technologies: string[];
  challenge: string;
  solution: string;
}

const FounderStorySection: React.FC = () => {
  const [currentMilestone, setCurrentMilestone] = useState(0);

  const milestones: Milestone[] = [
    {
      id: '1',
      date: 'January 2023',
      title: 'The Disconnected Tools Problem',
      description: 'Started with 5 different tools that didn\'t talk to each other. Lost leads, missed follow-ups, manual data entry consuming 15+ hours per week.',
      metrics: {
        leadsGenerated: 23,
        automationLevel: 5,
        timesSaved: 0,
      },
      technologies: ['Pipedrive', 'Mailchimp', 'Google Sheets', 'Calendly', 'Slack'],
      challenge: 'Manual lead management, no automation, data silos',
      solution: 'Realized the need for unified CRM integration platform',
    },
    {
      id: '2',
      date: 'March 2023',
      title: 'First CRM Integration Breakthrough',
      description: 'Built first automated workflow connecting Pipedrive to email campaigns. Saw immediate 300% increase in lead response rates.',
      metrics: {
        leadsGenerated: 89,
        crmIntegrations: 1,
        automationLevel: 35,
        timesSaved: 8,
      },
      technologies: ['Pipedrive API', 'Python', 'Zapier', 'Custom Scripts'],
      challenge: 'Complex API documentation, authentication issues',
      solution: 'Created reusable integration framework',
    },
    {
      id: '3',
      date: 'June 2023',
      title: 'Multi-CRM Support & AI Integration',
      description: 'Expanded to support HubSpot, Zoho, and Monday.com. Added AI-powered lead scoring and personalized messaging.',
      metrics: {
        leadsGenerated: 247,
        crmIntegrations: 4,
        automationLevel: 70,
        timesSaved: 20,
      },
      technologies: ['OpenAI GPT-4', 'FastAPI', 'PostgreSQL', 'React'],
      challenge: 'Different CRM data structures, scaling automation',
      solution: 'Built universal CRM abstraction layer',
    },
    {
      id: '4',
      date: 'October 2023',
      title: 'Full Marketing Automation Platform',
      description: 'Launched Auto.Mark with NeuraCRM built-in. 24/7 lead nurturing, predictive analytics, and seamless CRM connectivity.',
      metrics: {
        leadsGenerated: 847,
        crmIntegrations: 8,
        automationLevel: 94,
        timesSaved: 35,
      },
      technologies: ['Auto.Mark Platform', 'NeuraCRM', 'AI Agents', 'Real-time Analytics'],
      challenge: 'Scaling to multiple businesses, maintaining reliability',
      solution: 'Co-creator program for collaborative development',
    },
  ];

  const nextMilestone = () => {
    setCurrentMilestone((prev) => (prev + 1) % milestones.length);
  };

  const prevMilestone = () => {
    setCurrentMilestone((prev) => (prev - 1 + milestones.length) % milestones.length);
  };

  const currentData = milestones[currentMilestone];

  return (
    <section id="story" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            From Zero to Automated Lead Generation
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            The journey of building Auto.Mark: How one founder solved the CRM integration nightmare 
            and created a platform that works with any system.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Timeline Navigation */}
          <div className="order-2 lg:order-1">
            <Card className="p-8">
              <div className="flex items-center justify-between mb-6">
                <button
                  onClick={prevMilestone}
                  className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  <span className="font-semibold text-primary-600">{currentData.date}</span>
                </div>
                <button
                  onClick={nextMilestone}
                  className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              <h3 className="text-2xl font-bold text-gray-900 mb-4">{currentData.title}</h3>
              <p className="text-gray-600 mb-6">{currentData.description}</p>

              {/* Challenge & Solution */}
              <div className="space-y-4 mb-6">
                <div className="bg-red-50 border-l-4 border-red-400 p-4">
                  <h4 className="font-semibold text-red-800 mb-1">Challenge</h4>
                  <p className="text-red-700 text-sm">{currentData.challenge}</p>
                </div>
                <div className="bg-green-50 border-l-4 border-green-400 p-4">
                  <h4 className="font-semibold text-green-800 mb-1">Solution</h4>
                  <p className="text-green-700 text-sm">{currentData.solution}</p>
                </div>
              </div>

              {/* Technologies */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-2">Technologies Used</h4>
                <div className="flex flex-wrap gap-2">
                  {currentData.technologies.map((tech) => (
                    <span
                      key={tech}
                      className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              {/* Progress Indicators */}
              <div className="flex space-x-2">
                {milestones.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentMilestone(index)}
                    className={`w-3 h-3 rounded-full transition-colors ${
                      index === currentMilestone ? 'bg-primary-600' : 'bg-gray-300'
                    }`}
                  />
                ))}
              </div>
            </Card>
          </div>

          {/* Metrics Dashboard */}
          <div className="order-1 lg:order-2">
            <div className="grid grid-cols-2 gap-6">
              <Card className="p-6 text-center" hover>
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {currentData.metrics.leadsGenerated || 0}
                </div>
                <div className="text-sm text-gray-600">Leads Generated</div>
              </Card>

              <Card className="p-6 text-center" hover>
                <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-green-600" />
                </div>
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {currentData.metrics.automationLevel || 0}%
                </div>
                <div className="text-sm text-gray-600">Automation Level</div>
              </Card>

              <Card className="p-6 text-center" hover>
                <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {currentData.metrics.crmIntegrations || 0}
                </div>
                <div className="text-sm text-gray-600">CRM Integrations</div>
              </Card>

              <Card className="p-6 text-center" hover>
                <div className="bg-orange-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Calendar className="w-6 h-6 text-orange-600" />
                </div>
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {currentData.metrics.timesSaved || 0}h
                </div>
                <div className="text-sm text-gray-600">Hours Saved/Week</div>
              </Card>
            </div>

            {/* Current Vision */}
            <Card className="mt-6 p-6 bg-gradient-to-r from-primary-50 to-secondary-50">
              <h4 className="font-bold text-gray-900 mb-2">Today's Vision</h4>
              <p className="text-gray-700 text-sm">
                "Every business deserves marketing automation that works with their existing CRM. 
                No more switching systems, no more lost leads, no more manual work. 
                Just intelligent automation that grows with you."
              </p>
              <div className="mt-4 text-right">
                <span className="text-sm text-gray-600 italic">- Founder, Auto.Mark</span>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FounderStorySection;