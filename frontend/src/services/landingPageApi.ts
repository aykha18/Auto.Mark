import apiClient from './api';
import {
  FounderStoryContent,
  CoCreatorProgramStatus,
  CRMIntegration,
  LeadCaptureForm,
  LeadResponse,
  PageViewEvent,
  ChatSession,
  CRMAssessmentQuestion,
  AssessmentResponse,
  CRMAssessmentResult
} from '../types';

export class LandingPageAPI {
  // Founder Story
  static async getFounderStory(): Promise<FounderStoryContent> {
    const response = await apiClient.get('/api/v1/landing/founder-story');
    return response.data;
  }

  // Co-Creator Program
  static async getCoCreatorStatus(): Promise<CoCreatorProgramStatus> {
    const response = await apiClient.get('/api/v1/landing/co-creator-status');
    return response.data;
  }

  // CRM Integrations
  static async getSupportedCRMs(): Promise<CRMIntegration[]> {
    const response = await apiClient.get('/api/v1/landing/supported-crms');
    return response.data;
  }

  // Lead Capture
  static async submitLeadCapture(leadData: LeadCaptureForm): Promise<LeadResponse> {
    const response = await apiClient.post('/api/v1/landing/lead-capture', leadData);
    return response.data;
  }

  // Analytics
  static async trackPageView(pageData: PageViewEvent): Promise<void> {
    // TODO: Implement backend endpoint for page view tracking
    // For now, just log locally to avoid 405 errors
    if (process.env.NODE_ENV === 'development') {
      console.log('Page view tracked (local only):', pageData.page);
    }
    return Promise.resolve();
  }

  // Chat
  static async initializeChat(): Promise<ChatSession> {
    const response = await apiClient.post('/api/v1/chat/initialize');
    return response.data;
  }

  // Assessment
  static async getAssessmentQuestions(): Promise<CRMAssessmentQuestion[]> {
    const response = await apiClient.get('/api/v1/landing/assessment/questions');
    return response.data.questions;
  }

  static async startAssessment(data: { email: string; name: string; company?: string }): Promise<any> {
    const response = await apiClient.post('/api/v1/landing/assessment/start', data);
    return response.data;
  }

  static async submitAssessmentResponse(data: { assessment_id: number; responses: AssessmentResponse[] }): Promise<CRMAssessmentResult> {
    const response = await apiClient.post('/api/v1/landing/assessment/submit', data);
    return response.data;
  }

  // Payment Processing
  static async createPaymentIntent(amount: number, currency: string = 'usd'): Promise<any> {
    const response = await apiClient.post('/api/v1/landing/create-payment-intent', {
      amount,
      currency,
      metadata: {
        program: 'co-creator',
        seats: 25
      }
    });
    return response.data;
  }

  static async registerCoCreator(paymentIntentId: string, customerInfo: any): Promise<any> {
    const response = await apiClient.post('/api/v1/landing/co-creator-registration', {
      paymentIntentId,
      customerInfo
    });
    return response.data;
  }

  static async getCoCreatorProfile(coCreatorId: string): Promise<any> {
    const response = await apiClient.get(`/api/v1/landing/co-creator-profile/${coCreatorId}`);
    return response.data;
  }

  static async activateCoCreator(coCreatorId: string, activationData: any): Promise<any> {
    const response = await apiClient.post(`/api/v1/landing/co-creator-activate/${coCreatorId}`, activationData);
    return response.data;
  }

  static async getPaymentReceipt(paymentIntentId: string): Promise<Blob> {
    const response = await apiClient.get(`/api/v1/landing/payment-receipt/${paymentIntentId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Founding Members Stats
  static async getFoundingMembersStats(): Promise<{
    total_spots: number;
    spots_taken: number;
    spots_remaining: number;
    progress_percentage: number;
    last_updated: string;
    is_live: boolean;
    status: string;
  }> {
    const response = await apiClient.get('/api/v1/landing/founding-members/stats');
    return response.data;
  }

  // Agent Activity Stats
  static async getAgentActivityStats(): Promise<{
    ai_generated_posts: number;
    ai_engagements: number;
    ai_followups: number;
    ai_booked_demos: number;
    last_post_time: string;
    last_activity: string;
    is_live: boolean;
    status: string;
    response_time_avg: string;
    live_activities: Array<{
      time: string;
      action: string;
      type: string;
    }>;
  }> {
    const response = await apiClient.get('/api/v1/landing/agent-activity/stats');
    return response.data;
  }

  // Health Check
  static async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get('/api/v1/landing/health');
    return response.data;
  }
}

export default LandingPageAPI;
