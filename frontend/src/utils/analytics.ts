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
    // This would be implemented when we have conversion tracking endpoint
    console.log('Conversion tracked:', eventType, eventData);
  } catch (error) {
    console.error('Failed to track conversion:', error);
  }
};
