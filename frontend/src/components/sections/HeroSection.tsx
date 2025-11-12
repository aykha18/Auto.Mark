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
            {/* Transparent Beta Badge */}
            <div className="inline-flex items-center bg-red-500 text-white px-4 py-2 rounded-full text-sm font-bold mb-6 animate-pulse">
              <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
              BETA - INVITING 25 FOUNDING MEMBERS
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-unitasa-blue mb-6 leading-tight font-display">
              Marketing Intelligence
              <span className="bg-gradient-primary bg-clip-text text-transparent block">That Thinks & Optimizes</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-unitasa-gray mb-8 max-w-2xl mx-auto lg:mx-0 font-medium">
              <strong className="text-unitasa-blue">Beyond traditional marketing automation.</strong> AI that makes 10,000+ intelligent decisions per hour,
              replacing human oversight with <strong className="text-unitasa-electric">autonomous marketing excellence</strong>.
            </p>

            <p className="text-lg text-unitasa-gray mb-8 max-w-2xl mx-auto lg:mx-0">
              🚀 NOW IN BETA - Join 25 Founding Members Built by a founder frustrated with disconnected marketing tools. Help shape the future of AI marketing automation.
            </p>

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
              
              {/* Problem Statement */}
              <div className="space-y-4 p-4">
                <h3 className="text-lg font-bold text-unitasa-blue mb-3">The Problem Every B2B Founder Faces:</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">⏰</span>
                    <span>15+ hours/week managing disconnected marketing tools</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">💔</span>
                    <span>CRM integrations that break constantly</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">🤖</span>
                    <span>"AI marketing" that's just basic if/then rules</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">💸</span>
                    <span>$500+/month on tools that don't talk to each other</span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-unitasa-light/50 rounded-lg">
                  <p className="text-sm text-unitasa-blue font-medium">
                    I built Unitasa because I had this exact problem. Now inviting 25 founders to build it together.
                  </p>
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
