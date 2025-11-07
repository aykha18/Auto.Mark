import React, { useEffect, useState, Suspense, lazy } from 'react';
import { Layout } from '../components/layout';
import { 
  HeroSection, 
  PlatformPositioningSection
} from '../components/sections';
import { CRMAssessmentResult } from '../types';
import { trackPageView } from '../utils/analytics';
import LeadCaptureForm, { LeadData } from '../components/assessment/LeadCaptureForm';
import CRMSelectorStep from '../components/assessment/CRMSelectorStep';
import ConsultationTest from '../components/test/ConsultationTest';
import { useCurrency } from '../hooks/useCurrency';

// Lazy load heavy components
const AICapabilitiesSection = lazy(() => import('../components/sections/AICapabilitiesSection'));
const FounderStorySection = lazy(() => import('../components/sections/FounderStorySection'));
const SocialProofSection = lazy(() => import('../components/sections/SocialProofSection'));
const CRMMarketplaceSection = lazy(() => import('../components/sections/CRMMarketplaceSection'));
const ThoughtLeadershipSection = lazy(() => import('../components/sections/ThoughtLeadershipSection'));
const AssessmentModal = lazy(() => import('../components/assessment/AssessmentModal'));
const ChatWidget = lazy(() => import('../components/chat/ChatWidget'));
const ChatProvider = lazy(() => import('../components/chat/ChatProvider'));

// Chat Widget Container Component
const ChatWidgetContainer: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  return (
    <ChatWidget
      isOpen={isChatOpen}
      onToggle={() => setIsChatOpen(!isChatOpen)}
      onMinimize={() => setIsChatMinimized(!isChatMinimized)}
      isMinimized={isChatMinimized}
      unreadCount={unreadCount}
    />
  );
};

const LandingPage: React.FC = () => {
  const [isLeadCaptureOpen, setIsLeadCaptureOpen] = useState(false);
  const [isCRMSelectorOpen, setIsCRMSelectorOpen] = useState(false);
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<CRMAssessmentResult | null>(null);
  const [leadData, setLeadData] = useState<LeadData | null>(null);
  
  // Currency detection for pricing display
  const currency = useCurrency(497);

  useEffect(() => {
    trackPageView('/');

    // Listen for custom events to open assessment
    const handleOpenAssessment = () => {
      setIsAssessmentOpen(true);
    };

    // Listen for custom events to open lead capture
    const handleOpenLeadCapture = () => {
      setIsLeadCaptureOpen(true);
    };

    window.addEventListener('openAssessment', handleOpenAssessment);
    window.addEventListener('openLeadCapture', handleOpenLeadCapture);

    return () => {
      window.removeEventListener('openAssessment', handleOpenAssessment);
      window.removeEventListener('openLeadCapture', handleOpenLeadCapture);
    };
  }, []);

  const handleAssessmentComplete = (result: CRMAssessmentResult) => {
    setAssessmentResult(result);
    // Track conversion event
    console.log('Assessment completed:', result);
  };

  const openAssessment = () => {
    // First show lead capture form
    setIsLeadCaptureOpen(true);
  };

  const handleLeadCapture = (data: LeadData) => {
    console.log('Lead captured, opening CRM selector:', data);
    setLeadData(data);
    setIsLeadCaptureOpen(false);
    setIsCRMSelectorOpen(true);
  };

  const handleCRMSelection = (selectedCRM: string) => {
    console.log('CRM selected:', selectedCRM);
    if (leadData) {
      setLeadData({ ...leadData, preferredCRM: selectedCRM });
    }
    setIsCRMSelectorOpen(false);
    setIsAssessmentOpen(true);
  };

  const closeLeadCapture = () => {
    setIsLeadCaptureOpen(false);
  };

  const closeCRMSelector = () => {
    setIsCRMSelectorOpen(false);
  };

  const backToCRMSelector = () => {
    setIsAssessmentOpen(false);
    setIsCRMSelectorOpen(true);
  };

  const backToLeadCapture = () => {
    setIsCRMSelectorOpen(false);
    setIsLeadCaptureOpen(true);
  };

  const closeAssessment = () => {
    setIsAssessmentOpen(false);
  };

  return (
    <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>}>
      <ChatProvider>
        <Layout>
          <div className="bg-white">
            <HeroSection onStartAssessment={openAssessment} />
            
            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <AICapabilitiesSection />
            </Suspense>
            
            <PlatformPositioningSection />
            
            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <CRMMarketplaceSection />
            </Suspense>
            
            <Suspense fallback={<div className="h-64 bg-gray-50 animate-pulse"></div>}>
              <SocialProofSection />
            </Suspense>
            
            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <FounderStorySection />
            </Suspense>
            
            <Suspense fallback={<div className="h-64 bg-gray-50 animate-pulse"></div>}>
              <ThoughtLeadershipSection isCoCreator={assessmentResult?.readinessLevel === 'priority_integration'} />
            </Suspense>
            
            {/* Co-Creator Program Preview */}
            <section id="co-creator" className="py-20">
              <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <div className="bg-gradient-to-r from-unitasa-electric to-unitasa-purple text-white rounded-2xl p-8 md:p-12 relative overflow-hidden shadow-brand">
                  {/* Urgency Badge */}
                  <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse">
                    LIMITED TIME
                  </div>

                  <h2 className="text-3xl md:text-4xl font-bold mb-4 font-display">
                    Join 25 Visionaries of AI Marketing
                  </h2>

                  <div className="mb-6">
                    <div className="text-4xl font-bold mb-2 text-white">{currency.displayText}</div>
                    <div className="text-sm text-white/80 mt-1">
                      {currency.isIndian ? '(~$497 USD)' : '(~₹41,500 INR)'}
                    </div>
                    <div className="text-lg opacity-90 line-through mb-1 text-white mt-2">
                      Regular price: {currency.isIndian ? '₹1,67,000+' : '$2,000+'}
                    </div>
                    <p className="text-xl opacity-90 text-white">
                      Assessment-Qualified • Lifetime Access • Shape AI Marketing's Future
                    </p>
                  </div>
                  
                  {/* Value Stack */}
                  <div className="bg-white/10 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
                    <div className="text-sm font-semibold mb-2 text-center text-white">What You Get ($1,400+ Value):</div>
                    <div className="space-y-1 text-sm text-white">
                      <div className="flex justify-between">
                        <span>• Lifetime AI Platform Access</span>
                        <span>$500+/month</span>
                      </div>
                      <div className="flex justify-between">
                        <span>• Personal AI Strategy Audit</span>
                        <span>$500</span>
                      </div>
                      <div className="flex justify-between">
                        <span>• Custom AI Agent Setup</span>
                        <span>$300</span>
                      </div>
                      <div className="flex justify-between">
                        <span>• 6-Month Priority Support</span>
                        <span>$600</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-center mb-6">
                    <div className="bg-white/20 rounded-full px-4 py-2">
                      <span className="font-semibold text-white">⚡ Only 12 visionary spots remaining</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <button
                      onClick={openAssessment}
                      className="bg-white text-unitasa-blue px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors w-full sm:w-auto shadow-lg"
                    >
                      Qualify for AI Intelligence Access
                    </button>
                    <div className="text-sm opacity-75 text-white">
                      🎯 Assessment determines if you're ready for enterprise AI marketing
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Lead Capture Form */}
            <LeadCaptureForm
              isOpen={isLeadCaptureOpen}
              onClose={closeLeadCapture}
              onSubmit={handleLeadCapture}
            />

            {/* CRM Selector Step */}
            <CRMSelectorStep
              isOpen={isCRMSelectorOpen}
              onClose={closeCRMSelector}
              onNext={handleCRMSelection}
              onBack={backToLeadCapture}
            />

            {/* Assessment Modal */}
            {isAssessmentOpen && (
              <Suspense fallback={<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>}>
                <AssessmentModal
                  isOpen={isAssessmentOpen}
                  onClose={closeAssessment}
                  onComplete={handleAssessmentComplete}
                  leadData={leadData}
                />
              </Suspense>
            )}

            {/* Chat Widget */}
            <Suspense fallback={null}>
              <ChatWidgetContainer />
            </Suspense>
          </div>
        </Layout>
      </ChatProvider>
    </Suspense>
  );
};

export default LandingPage;
