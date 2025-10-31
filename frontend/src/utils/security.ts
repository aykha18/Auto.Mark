/**
 * Frontend Security Utilities
 * Implements XSS protection, input sanitization, and security best practices
 */

// Content Security Policy nonce management
export const getCSPNonce = (): string | null => {
  const metaTag = document.querySelector('meta[name="csp-nonce"]');
  return metaTag ? metaTag.getAttribute('content') : null;
};

// XSS Protection utilities
export const sanitizeHTML = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};

export const sanitizeURL = (url: string): string => {
  try {
    const parsedURL = new URL(url);
    
    // Only allow HTTP and HTTPS protocols
    if (!['http:', 'https:'].includes(parsedURL.protocol)) {
      throw new Error('Invalid protocol');
    }
    
    // Block javascript: and data: URLs
    if (parsedURL.protocol === 'javascript:' || parsedURL.protocol === 'data:') {
      throw new Error('Blocked protocol');
    }
    
    return parsedURL.toString();
  } catch {
    // Return empty string for invalid URLs
    return '';
  }
};

// Input validation and sanitization
export const sanitizeInput = (input: string, type: 'text' | 'email' | 'phone' | 'url' = 'text'): string => {
  if (!input || typeof input !== 'string') {
    return '';
  }
  
  // Remove null bytes and control characters
  let sanitized = input.replace(/[\x00-\x1F\x7F]/g, '');
  
  // Trim whitespace
  sanitized = sanitized.trim();
  
  // Type-specific sanitization
  switch (type) {
    case 'email':
      // Remove dangerous characters for email
      sanitized = sanitized.replace(/[<>'"]/g, '');
      break;
    case 'phone':
      // Keep only digits, spaces, hyphens, parentheses, and plus
      sanitized = sanitized.replace(/[^0-9\s\-\(\)\+]/g, '');
      break;
    case 'url':
      sanitized = sanitizeURL(sanitized);
      break;
    default:
      // Basic text sanitization - remove HTML tags
      sanitized = sanitized.replace(/<[^>]*>/g, '');
  }
  
  return sanitized;
};

// Secure form data handling
export const sanitizeFormData = (formData: Record<string, any>): Record<string, any> => {
  const sanitized: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(formData)) {
    if (typeof value === 'string') {
      // Determine sanitization type based on field name
      let type: 'text' | 'email' | 'phone' | 'url' = 'text';
      
      if (key.toLowerCase().includes('email')) {
        type = 'email';
      } else if (key.toLowerCase().includes('phone')) {
        type = 'phone';
      } else if (key.toLowerCase().includes('url') || key.toLowerCase().includes('website')) {
        type = 'url';
      }
      
      sanitized[key] = sanitizeInput(value, type);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
};

// CSRF Protection
export const generateCSRFToken = (): string => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

export const setCSRFToken = (token: string): void => {
  sessionStorage.setItem('csrf_token', token);
};

export const getCSRFToken = (): string | null => {
  return sessionStorage.getItem('csrf_token');
};

// Secure API request headers
export const getSecureHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  };
  
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  
  return headers;
};

// Secure local storage wrapper
export const secureStorage = {
  setItem: (key: string, value: string): void => {
    try {
      // In production, consider encrypting sensitive data
      sessionStorage.setItem(key, value);
    } catch (error) {
      console.warn('Failed to store data securely:', error);
    }
  },
  
  getItem: (key: string): string | null => {
    try {
      return sessionStorage.getItem(key);
    } catch (error) {
      console.warn('Failed to retrieve data securely:', error);
      return null;
    }
  },
  
  removeItem: (key: string): void => {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.warn('Failed to remove data securely:', error);
    }
  },
  
  clear: (): void => {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.warn('Failed to clear secure storage:', error);
    }
  }
};

// Password strength validation
export const validatePasswordStrength = (password: string): {
  isStrong: boolean;
  score: number;
  feedback: string[];
} => {
  const feedback: string[] = [];
  let score = 0;
  
  if (password.length >= 8) {
    score += 20;
  } else {
    feedback.push('Password should be at least 8 characters long');
  }
  
  if (/[a-z]/.test(password)) {
    score += 20;
  } else {
    feedback.push('Include lowercase letters');
  }
  
  if (/[A-Z]/.test(password)) {
    score += 20;
  } else {
    feedback.push('Include uppercase letters');
  }
  
  if (/\d/.test(password)) {
    score += 20;
  } else {
    feedback.push('Include numbers');
  }
  
  if (/[^a-zA-Z0-9]/.test(password)) {
    score += 20;
  } else {
    feedback.push('Include special characters');
  }
  
  return {
    isStrong: score >= 80,
    score,
    feedback
  };
};

// Rate limiting for client-side requests
class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  
  isAllowed(key: string, maxRequests: number = 10, windowMs: number = 60000): boolean {
    const now = Date.now();
    const windowStart = now - windowMs;
    
    if (!this.requests.has(key)) {
      this.requests.set(key, []);
    }
    
    const keyRequests = this.requests.get(key)!;
    
    // Remove old requests outside the window
    const validRequests = keyRequests.filter(timestamp => timestamp > windowStart);
    
    if (validRequests.length >= maxRequests) {
      return false;
    }
    
    // Add current request
    validRequests.push(now);
    this.requests.set(key, validRequests);
    
    return true;
  }
  
  reset(key: string): void {
    this.requests.delete(key);
  }
}

export const rateLimiter = new RateLimiter();

// Security event logging
export const logSecurityEvent = (event: string, details: Record<string, any> = {}): void => {
  // In production, send to security monitoring service
  console.warn('Security Event:', {
    event,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
    ...details
  });
};

// Detect and prevent clickjacking
export const preventClickjacking = (): void => {
  if (window.top !== window.self) {
    // Page is in an iframe
    logSecurityEvent('clickjacking_attempt', {
      referrer: document.referrer,
      parentOrigin: window.parent.location.origin
    });
    
    // Break out of iframe
    window.top!.location.href = window.self.location.href;
  }
};

// Initialize security measures
export const initializeSecurity = (): void => {
  // Prevent clickjacking
  preventClickjacking();
  
  // Generate and set CSRF token
  const csrfToken = generateCSRFToken();
  setCSRFToken(csrfToken);
  
  // Add security event listeners
  window.addEventListener('error', (event) => {
    if (event.error && event.error.name === 'SecurityError') {
      logSecurityEvent('security_error', {
        message: event.error.message,
        filename: event.filename,
        lineno: event.lineno
      });
    }
  });
  
  // Monitor for suspicious activity
  let rapidClicks = 0;
  document.addEventListener('click', () => {
    rapidClicks++;
    setTimeout(() => rapidClicks--, 1000);
    
    if (rapidClicks > 20) {
      logSecurityEvent('suspicious_clicking', { clickCount: rapidClicks });
    }
  });
};
