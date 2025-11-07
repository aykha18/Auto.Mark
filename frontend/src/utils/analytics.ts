import { PageViewEvent } from '../types';
import LandingPageAPI from '../services/landingPageApi';

// Generate session ID
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Get or create session ID
export const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

// Track page view
export const trackPageView = async (page: string, referrer?: string): Promise<void> => {
  try {
    const pageViewEvent: PageViewEvent = {
      page,
      referrer: referrer || document.referrer,
      timestamp: new Date(),
      sessionId: getSessionId(),
    };

    // Only track if backend is available
    await LandingPageAPI.trackPageView(pageViewEvent);
  } catch (error) {
    // Silently fail for analytics - don't show errors to users
    console.log('Analytics tracking skipped (backend not available)');
  }
};

// Track conversion event
export const trackConversion = async (eventType: string, eventData?: any): Promise<void> => {
  try {
    // Track to Google Analytics
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', eventType, eventData);
    }
    console.log('Conversion tracked:', eventType, eventData);
  } catch (error) {
    console.error('Failed to track conversion:', error);
  }
};

// Track specific events
export const trackEvent = (eventName: string, params?: Record<string, any>): void => {
  try {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', eventName, params);
    }
  } catch (error) {
    console.error('Failed to track event:', error);
  }
};

// Pre-defined event trackers
export const analytics = {
  // Assessment events
  assessmentStarted: () => trackEvent('assessment_started'),
  assessmentCompleted: (score: number) => trackEvent('assessment_completed', { score }),
  
  // Lead events
  leadCaptured: (source: string) => trackEvent('lead_captured', { source }),
  
  // Consultation events
  consultationBooked: () => trackEvent('consultation_booked'),
  
  // Payment events
  paymentInitiated: (amount: number, currency: string) => 
    trackEvent('payment_initiated', { value: amount, currency }),
  paymentCompleted: (amount: number, currency: string) => 
    trackEvent('purchase', { value: amount, currency, transaction_id: Date.now().toString() }),
  
  // Engagement events
  demoScheduled: () => trackEvent('demo_scheduled'),
  aiReportGenerated: () => trackEvent('ai_report_generated'),
  
  // CTA clicks
  ctaClicked: (ctaName: string, location: string) => 
    trackEvent('cta_click', { cta_name: ctaName, location }),
};
