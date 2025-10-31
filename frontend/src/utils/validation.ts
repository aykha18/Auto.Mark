// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Phone validation (basic)
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
};

// LinkedIn URL validation
export const isValidLinkedInUrl = (url: string): boolean => {
  const linkedinRegex = /^https?:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+\/?$/;
  return linkedinRegex.test(url);
};

// Form validation
export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export const validateLeadCaptureForm = (data: {
  email: string;
  name: string;
  phone?: string;
  linkedinProfile?: string;
}): ValidationResult => {
  const errors: Record<string, string> = {};

  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(data.email)) {
    errors.email = 'Please enter a valid email address';
  }

  if (!data.name || data.name.trim().length < 2) {
    errors.name = 'Name must be at least 2 characters long';
  }

  if (data.phone && !isValidPhone(data.phone)) {
    errors.phone = 'Please enter a valid phone number';
  }

  if (data.linkedinProfile && !isValidLinkedInUrl(data.linkedinProfile)) {
    errors.linkedinProfile = 'Please enter a valid LinkedIn profile URL';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Assessment validation
export const validateAssessmentResponse = (
  questionType: string,
  answer: string | number,
  options?: string[]
): ValidationResult => {
  const errors: Record<string, string> = {};

  switch (questionType) {
    case 'multiple_choice':
      if (!answer || (typeof answer === 'string' && answer.trim() === '')) {
        errors.answer = 'Please select an option';
      } else if (options && !options.includes(answer as string)) {
        errors.answer = 'Invalid option selected';
      }
      break;
    
    case 'scale':
      if (typeof answer !== 'number' || answer < 1 || answer > 10) {
        errors.answer = 'Please select a value between 1 and 10';
      }
      break;
    
    case 'text':
      if (!answer || (typeof answer === 'string' && answer.trim().length < 3)) {
        errors.answer = 'Please provide at least 3 characters';
      }
      break;
    
    case 'crm_selector':
      if (!answer || (typeof answer === 'string' && answer.trim() === '')) {
        errors.answer = 'Please select a CRM system';
      }
      break;
    
    default:
      if (!answer) {
        errors.answer = 'This field is required';
      }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
