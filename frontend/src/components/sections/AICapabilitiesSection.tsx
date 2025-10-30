import React, { useState } from 'react';
import { Brain, Target, MessageCircle, Zap, Shield, BarChart3 } from 'lucide-react';
import Button from '../ui/Button';
import AIDemoModal from '../ai-demos/AIDemoModal';

interface AICapability {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  metrics: string[];
  demoComponent?: React.ReactNode;
}

const AICapabilitiesSection: React.FC = () => {
  const [activeDemo, setActiveDemo] = useState<string | null>(null);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  const capabilities: AICapability[] = [
    {
      id: 'autonomous-agent',
      title: 'Autonomous Marketing Agent',
      description: 'AI that thinks, learns, and optimizes your campaigns 24/7',
      icon: <Brain className="w-8 h-8" />,
      metrics: [
        'Makes 10,000+ optimization decisions per hour',
        'Improves performance by 15% monthly through AI learning',
        'Executes 500+ marketing actions daily without human intervention'
      ]
    },
    {
      id: 'predictive-intelligence',
      title: 'Predictive Lead Intelligence',
      description: 'Know which leads will convert before they do',
      icon: <Target className="w-8 h-8" />,
      metrics: [
        '94% accuracy in conversion prediction',
        'Predicts customer lifetime value with 89% precision',
        'Identifies high-value prospects 3x faster'
      ]
    },
    {
      id: 'conversational-ai',
      title: 'Conversational AI Assistant',
      description: 'Your AI marketing expert that never sleeps',
      icon: <MessageCircle className="w-8 h-8" />,
      metrics: [
        'Voice-enabled, context-aware consultation',
        'Multi-modal communication (text, voice, visual)',
        'Real-time strategy recommendations'
      ]
    },
    {
      id: 'real-time-optimization',
      title: 'Real-Time Performance Optimization',
      description: 'AI that optimizes your campaigns in real-time',
      icon: <Zap className="w-8 h-8" />,
      metrics: [
        'Automatic budget allocation and bid adjustments',
        'Cross-channel performance monitoring',
        'Instant ROI optimization'
      ]
    },
    {
      id: 'enterprise-security',
      title: 'Enterprise Security & Compliance',
      description: 'Bank-level security with AI-powered threat detection',
      icon: <Shield className="w-8 h-8" />,
      metrics: [
        'OAuth2 security with advanced authentication',
        'AI-powered threat detection and prevention',
        'Automated compliance monitoring'
      ]
    },
    {
      id: 'advanced-analytics',
      title: 'Advanced Analytics & Insights',
      description: 'Deep intelligence that reveals hidden opportunities',
      icon: <BarChart3 className="w-8 h-8" />,
      metrics: [
        'Cross-channel attribution tracking',
        'Predictive analytics for campaign performance',
        'Real-time performance monitoring with circuit breakers'
      ]
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Unified Marketing Intelligence Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need IN one platform. Unified marketing intelligence that replaces 
            fragmented tools with complete marketing unity and autonomous optimization.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {capabilities.map((capability) => (
            <div
              key={capability.id}
              className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
            >
              <div className="flex items-center mb-6">
                <div className="p-3 bg-blue-100 rounded-lg text-blue-600 mr-4">
                  {capability.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {capability.title}
                </h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                {capability.description}
              </p>
              
              <div className="space-y-3 mb-6">
                {capability.metrics.map((metric, index) => (
                  <div key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{metric}</span>
                  </div>
                ))}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setActiveDemo(capability.id);
                  setIsDemoModalOpen(true);
                }}
                className="w-full"
              >
                See Demo
              </Button>
            </div>
          ))}
        </div>

        {/* AI Impact Metrics */}
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            AI Performance Metrics
          </h3>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">340%</div>
              <div className="text-sm text-gray-600">Average ROI Improvement</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">94%</div>
              <div className="text-sm text-gray-600">Prediction Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">10K+</div>
              <div className="text-sm text-gray-600">Decisions Per Hour</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
              <div className="text-sm text-gray-600">Autonomous Operation</div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Get Everything IN One Platform?
          </h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Join 25 founding entrepreneurs who get lifetime access to unified marketing intelligence - 
            everything you need IN one complete platform.
          </p>
          
          {/* Founder Offer Highlight */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6 max-w-lg mx-auto mb-8">
            <div className="flex items-center justify-center mb-3">
              <span className="bg-red-500 text-white text-xs px-3 py-1 rounded-full font-bold animate-pulse">
                LIMITED TIME
              </span>
            </div>
            <div className="text-3xl font-bold text-blue-600 mb-1">$497</div>
            <div className="text-sm text-gray-500 line-through mb-2">Regular: $2,000+</div>
            <div className="text-sm text-gray-700 font-medium">
              🚀 Founding Member Price • ⚡ Only 12 spots left
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="px-8">
              Secure Founding Spot
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="px-8"
              onClick={() => setIsDemoModalOpen(true)}
            >
              Watch AI Demo
            </Button>
          </div>
          
          <div className="text-sm text-gray-500 mt-4">
            💡 Take AI assessment first to qualify for founder pricing
          </div>
        </div>

        {/* AI Demo Modal */}
        <AIDemoModal
          isOpen={isDemoModalOpen}
          onClose={() => setIsDemoModalOpen(false)}
          initialDemo={activeDemo || 'agent'}
        />
      </div>
    </section>
  );
};

export default AICapabilitiesSection;