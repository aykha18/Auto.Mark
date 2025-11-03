// Landing Page Types
export interface FounderStoryContent {
  heroNarrative: string;
  milestones: FounderMilestone[];
  currentMetrics: {
    totalLeadsAutomated: number;
    crmsIntegrated: number;
    businessesEnabled: number;
    integrationHours: number;
  };
  vision: string;
}

export interface FounderMilestone {
  id: string;
  date: Date;
  title: string;
  description: string;
  metrics: {
    leadsGenerated?: number;
    crmIntegrations?: number;
    automationLevel?: number;
    timesSaved?: number;
  };
  technologies: string[];
  integrationChallenges: string[];
  lessonLearned: string;
}

export interface CoCreatorProgramStatus {
  seatsRemaining: number;
  totalSeats: number;
  urgencyLevel: 'high' | 'medium' | 'low';
}

export interface CRMIntegration {
  name: string;
  logo: string;
  status: 'available' | 'coming_soon' | 'beta';
  setupComplexity: 'easy' | 'medium' | 'advanced';
  setupTimeMinutes: number;
  features: string[];
}

// Assessment Types
export interface CRMAssessmentQuestion {
  id: string;
  text: string;
  integrationInsight: string;
  type: 'multiple_choice' | 'scale' | 'text' | 'crm_selector';
  options?: string[];
  weight: number;
  category: 'current_crm' | 'data_quality' | 'automation_gaps' | 'technical_readiness';
}

export interface AssessmentResponse {
  questionId: string;
  answer: string | number;
  selectedCRM?: string;
  timestamp: Date;
  integrationInsightViewed: boolean;
}

export interface CRMAssessmentResult {
  leadId: string;
  currentCRM: string;
  integrationScore: number;
  readinessLevel: 'nurture_with_guides' | 'co_creator_qualified' | 'priority_integration';
  integrationRecommendations: string[];
  automationOpportunities: string[];
  technicalRequirements: string[];
  nextSteps: string[];
}

// Lead Types
export interface LeadCaptureForm {
  email: string;
  name: string;
  businessDescription?: string;
  phone?: string;
  linkedinProfile?: string;
}

export interface LeadResponse {
  id: string;
  message: string;
  success: boolean;
}

// CRM Integration Types
export interface CRMConnector {
  id: string;
  name: string;
  logo: string;
  apiType: 'REST' | 'GraphQL' | 'SOAP';
  authMethod: 'OAuth2' | 'API_Key' | 'JWT';
  setupComplexity: 'easy' | 'medium' | 'advanced';
  setupTimeMinutes: number;
  features: CRMFeature[];
  status: 'available' | 'beta' | 'coming_soon';
  documentation: string;
  sdkAvailable: boolean;
}

export interface CRMFeature {
  name: string;
  supported: boolean;
  description: string;
  apiEndpoint?: string;
}

// Chat Types
export interface ChatSession {
  id: string;
  active: boolean;
  messages: ChatMessage[];
  context?: ChatContext;
  voiceEnabled?: boolean;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date | string | undefined;
  type?: 'text' | 'voice' | 'system';
  metadata?: {
    crmRecommendation?: string;
    assessmentReference?: string;
    integrationTip?: string;
  };
}

export interface ChatContext {
  currentPage: string;
  userProgress: {
    assessmentCompleted: boolean;
    crmSelected?: string;
    readinessScore?: number;
  };
  previousMessages: string[];
}

export interface VoiceRecognitionState {
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  confidence: number;
}

export interface ChatWidget {
  isOpen: boolean;
  isMinimized: boolean;
  unreadCount: number;
  position: 'bottom-right' | 'bottom-left';
}

// Analytics Types
export interface PageViewEvent {
  page: string;
  referrer?: string;
  timestamp: Date;
  sessionId: string;
}

// Payment Types
export interface PaymentIntent {
  id: string;
  clientSecret: string;
  amount: number;
  currency: string;
  status: 'requires_payment_method' | 'requires_confirmation' | 'requires_action' | 'processing' | 'succeeded' | 'canceled';
}

export interface PaymentForm {
  email: string;
  name: string;
  businessName?: string;
  phone?: string;
}

export interface PaymentResult {
  success: boolean;
  paymentIntentId?: string;
  error?: string;
  coCreatorId?: string;
}

export interface CoCreatorProfile {
  id: string;
  userId: string;
  joinedAt: Date;
  lifetimeAccess: boolean;
  supporterBadge: boolean;
  featuresInfluenced: string[];
  testimonialOptIn: boolean;
}
