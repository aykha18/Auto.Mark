import React, { useEffect, useState, Suspense, lazy } from 'react';
import { Layout } from '../components/layout';
import { 
  HeroSection, 
  PlatformPositioningSection
} from '../components/sections';
import { CRMAssessmentResult } from '../types';
import { trackPageView } from '../utils/analytics';

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
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<CRMAssessmentResult | null>(null);

  useEffect(() => {
    trackPageView('/');
    
    // Listen for custom events to open assessment
    const handleOpenAssessment = () => {
      setIsAssessmentOpen(true);
    };
    
    window.addEventListener('openAssessment', handleOpenAssessment);
    
    return () => {
      window.removeEventListener('openAssessment', handleOpenAssessment);
    };
  }, []);

  const handleAssessmentComplete = (result: CRMAssessmentResult) => {
    setAssessmentResult(result);
    // Track conversion event
    console.log('Assessment completed:', result);
  };

  const openAssessment = () => {
    setIsAssessmentOpen(true);
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
                <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl p-8 md:p-12 relative overflow-hidden">
                  {/* Urgency Badge */}
                  <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse">
                    LIMITED TIME
                  </div>
                  
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    Join 25 Founding Co-Creators
                  </h2>
                  
                  <div className="mb-6">
                    <div className="text-4xl font-bold mb-2">$497</div>
                    <div className="text-lg opacity-90 line-through mb-1">Regular price: $2,000+</div>
                    <p className="text-xl opacity-90">
                      Founder Pricing • Lifetime Access • Direct Product Influence
                    </p>
                  </div>
                  
                  {/* Value Stack */}
                  <div className="bg-white/10 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
                    <div className="text-sm font-semibold mb-2 text-center">What You Get ($1,400+ Value):</div>
                    <div className="space-y-1 text-sm">
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
                      <span className="font-semibold">⚡ Only 12 founding spots remaining</span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <button 
                      onClick={openAssessment}
                      className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors w-full sm:w-auto"
                    >
                      Secure Your Founding Spot
                    </button>
                    <div className="text-sm opacity-75">
                      💡 Take assessment first to qualify for founder pricing
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Assessment Modal */}
            {isAssessmentOpen && (
              <Suspense fallback={<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>}>
                <AssessmentModal
                  isOpen={isAssessmentOpen}
                  onClose={closeAssessment}
                  onComplete={handleAssessmentComplete}
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
