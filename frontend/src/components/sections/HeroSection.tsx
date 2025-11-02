import React, { useState } from 'react';
import { ArrowRight, Play, CheckCircle } from 'lucide-react';
import { Button } from '../ui';
import AIDemoModal from '../ai-demos/AIDemoModal';

interface HeroSectionProps {
  onStartAssessment?: () => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({ onStartAssessment }) => {
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  return (
    <section className="bg-gradient-to-br from-unitasa-light via-white to-unitasa-light py-20 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="inline-flex items-center bg-unitasa-electric/10 text-unitasa-blue px-4 py-2 rounded-full text-sm font-medium mb-6 border border-unitasa-electric/20">
              <span className="w-2 h-2 bg-unitasa-electric rounded-full mr-2 animate-pulse"></span>
              Built by a founder who went from zero to automated lead generation
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-unitasa-blue mb-6 leading-tight font-display">
              Unified Marketing
              <span className="bg-gradient-primary bg-clip-text text-transparent block">Intelligence Platform</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-unitasa-gray mb-8 max-w-2xl mx-auto lg:mx-0 font-medium">
              <strong className="text-unitasa-blue">Everything you need IN one platform.</strong> Unified marketing intelligence that replaces
              fragmented tools with <strong className="text-unitasa-electric">complete marketing unity</strong>.
            </p>

            {/* Key Benefits */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8 text-left">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0" />
                <span className="text-gray-700">10,000+ AI decisions per hour</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0" />
                <span className="text-gray-700">94% prediction accuracy</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0" />
                <span className="text-gray-700">Voice-enabled AI assistant</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button 
                variant="primary" 
                size="lg" 
                icon={ArrowRight} 
                iconPosition="right"
                className="text-lg px-8 py-4"
                onClick={onStartAssessment}
              >
                Take AI Readiness Assessment
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                icon={Play} 
                iconPosition="left"
                className="text-lg px-8 py-4"
                onClick={() => setIsDemoModalOpen(true)}
              >
                Watch AI Demo
              </Button>
            </div>

            {/* Social Proof */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-4">Trusted by growing businesses</p>
              <div className="flex items-center justify-center lg:justify-start space-x-8 opacity-60">
                <div className="text-gray-400 font-semibold">TechCorp</div>
                <div className="text-gray-400 font-semibold">GrowthCo</div>
                <div className="text-gray-400 font-semibold">ScaleUp</div>
                <div className="text-gray-400 font-semibold">InnovateLab</div>
              </div>
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            {/* Main Dashboard Mockup */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 transform rotate-3 hover:rotate-0 transition-transform duration-300">
              <div className="bg-gradient-primary h-12 rounded-lg mb-4 flex items-center px-4 shadow-brand">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                </div>
                <div className="ml-4 text-white font-medium">Unitasa Dashboard</div>
              </div>
              
              {/* Dashboard Content */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600">Active Campaigns</div>
                  <div className="text-2xl font-bold text-primary-600">24/7</div>
                </div>
                <div className="bg-gray-100 h-2 rounded-full">
                  <div className="bg-gradient-primary h-2 rounded-full w-3/4"></div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="text-lg font-bold text-green-600">+340%</div>
                    <div className="text-xs text-gray-600">ROI Improvement</div>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">10K+</div>
                    <div className="text-xs text-gray-600">AI Decisions/Hour</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating CRM Icons */}
            <div className="absolute -top-4 -left-4 bg-white rounded-lg shadow-lg p-3 animate-bounce">
              <div className="w-8 h-8 bg-orange-500 rounded flex items-center justify-center text-white text-xs font-bold">
                P
              </div>
            </div>
            <div className="absolute -bottom-4 -right-4 bg-white rounded-lg shadow-lg p-3 animate-pulse">
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                H
              </div>
            </div>
            <div className="absolute top-1/2 -right-8 bg-white rounded-lg shadow-lg p-3 animate-bounce delay-300">
              <div className="w-8 h-8 bg-red-500 rounded flex items-center justify-center text-white text-xs font-bold">
                Z
              </div>
            </div>
          </div>
        </div>

        {/* AI Demo Modal */}
        <AIDemoModal
          isOpen={isDemoModalOpen}
          onClose={() => setIsDemoModalOpen(false)}
          initialDemo="agent"
        />
      </div>
    </section>
  );
};

export default HeroSection;
