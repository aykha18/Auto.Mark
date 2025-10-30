import React from 'react';
import Button from '../ui/Button';
import {
  AlertTriangle,
  RefreshCw,
  Mail,
  CreditCard,
  Shield,
  ExternalLink,
  ArrowLeft,
  Phone,
  Clock,
  Lock
} from 'lucide-react';

// Utility function to categorize Stripe errors
export const categorizeStripeError = (stripeError: any): PaymentError => {
  const { code, message, type } = stripeError;
  
  switch (code) {
    case 'card_declined':
      return {
        type: 'card_declined',
        message: message || 'Your card was declined. Please try a different payment method.',
        code,
        retryable: true,
        suggestedAction: 'Try a different card or contact your bank'
      };
    case 'insufficient_funds':
      return {
        type: 'insufficient_funds',
        message: message || 'Your card has insufficient funds.',
        code,
        retryable: true,
        suggestedAction: 'Check your balance or use a different card'
      };
    case 'expired_card':
      return {
        type: 'expired_card',
        message: message || 'Your card has expired.',
        code,
        retryable: true,
        suggestedAction: 'Use a card that hasn\'t expired'
      };
    case 'authentication_required':
    case 'card_authentication_required':
      return {
        type: 'authentication_required',
        message: message || 'Your card requires authentication. Please complete 3D Secure verification.',
        code,
        retryable: true,
        suggestedAction: 'Complete authentication with your bank'
      };
    case 'processing_error':
      return {
        type: 'processing_error',
        message: message || 'An error occurred while processing your card.',
        code,
        retryable: true,
        suggestedAction: 'Try again or use a different payment method'
      };
    case 'rate_limit_error':
      return {
        type: 'rate_limit',
        message: message || 'Too many requests. Please wait before trying again.',
        code,
        retryable: true,
        suggestedAction: 'Wait 15 minutes before retrying'
      };
    case 'invalid_request_error':
      return {
        type: 'invalid_request',
        message: message || 'Invalid payment request. Please refresh and try again.',
        code,
        retryable: true,
        suggestedAction: 'Refresh the page and try again'
      };
    default:
      if (type === 'validation_error') {
        return {
          type: 'invalid_request',
          message: message || 'Please check your payment information and try again.',
          code,
          retryable: true,
          suggestedAction: 'Verify your payment details'
        };
      }
      
      return {
        type: 'unknown',
        message: message || 'An unexpected error occurred. Please try again.',
        code,
        retryable: true,
        suggestedAction: 'Try again or contact support'
      };
  }
};

interface PaymentError {
  type: 'card_declined' | 'insufficient_funds' | 'expired_card' | 'network_error' | 'processing_error' | 'authentication_required' | 'invalid_request' | 'rate_limit' | 'unknown';
  message: string;
  code?: string;
  retryable: boolean;
  suggestedAction?: string;
}

interface PaymentErrorHandlerProps {
  error: PaymentError;
  onRetry: () => void;
  onBack: () => void;
  onContactSupport: () => void;
  retryCount: number;
  maxRetries: number;
  className?: string;
}

const PaymentErrorHandler: React.FC<PaymentErrorHandlerProps> = ({
  error,
  onRetry,
  onBack,
  onContactSupport,
  retryCount,
  maxRetries,
  className = '',
}) => {
  const getErrorIcon = () => {
    switch (error.type) {
      case 'card_declined':
      case 'insufficient_funds':
      case 'expired_card':
        return CreditCard;
      case 'network_error':
        return RefreshCw;
      case 'authentication_required':
        return Lock;
      case 'rate_limit':
        return Clock;
      case 'processing_error':
        return RefreshCw;
      default:
        return AlertTriangle;
    }
  };

  const getErrorTitle = () => {
    switch (error.type) {
      case 'card_declined':
        return 'Card Declined';
      case 'insufficient_funds':
        return 'Insufficient Funds';
      case 'expired_card':
        return 'Card Expired';
      case 'network_error':
        return 'Connection Issue';
      case 'processing_error':
        return 'Processing Error';
      case 'authentication_required':
        return 'Authentication Required';
      case 'rate_limit':
        return 'Too Many Attempts';
      case 'invalid_request':
        return 'Invalid Request';
      default:
        return 'Payment Failed';
    }
  };

  const getErrorSuggestions = () => {
    switch (error.type) {
      case 'card_declined':
        return [
          'Contact your bank to authorize the transaction',
          'Try a different payment method',
          'Verify your card details are correct',
          'Check if your card supports international transactions',
          'Ensure your billing address matches your card'
        ];
      case 'insufficient_funds':
        return [
          'Check your account balance',
          'Try a different card or payment method',
          'Contact your bank for assistance',
          'Consider using a debit card or bank transfer'
        ];
      case 'expired_card':
        return [
          'Use a card that hasn\'t expired',
          'Update your card information',
          'Try a different payment method',
          'Contact your bank for a replacement card'
        ];
      case 'network_error':
        return [
          'Check your internet connection',
          'Try again in a few moments',
          'Refresh the page and retry',
          'Try using a different browser or device'
        ];
      case 'authentication_required':
        return [
          'Complete 3D Secure authentication with your bank',
          'Check for SMS or app notifications from your bank',
          'Try using a different card',
          'Contact your bank if authentication fails'
        ];
      case 'processing_error':
        return [
          'Wait a few minutes and try again',
          'Check if the payment went through before retrying',
          'Try a different payment method',
          'Contact support if the error persists'
        ];
      case 'rate_limit':
        return [
          'Wait 15 minutes before trying again',
          'Too many attempts were made recently',
          'Contact support for immediate assistance',
          'Try using a different payment method'
        ];
      case 'invalid_request':
        return [
          'Refresh the page and try again',
          'Check that all required fields are filled',
          'Try using a different browser',
          'Contact support if the issue continues'
        ];
      default:
        return [
          'Try again in a few moments',
          'Use a different payment method',
          'Contact support if the issue persists',
          'Check your internet connection'
        ];
    }
  };

  const canRetry = error.retryable && retryCount < maxRetries;
  const ErrorIcon = getErrorIcon();

  return (
    <div className={`bg-gradient-to-br from-red-900/20 via-primary-800 to-secondary-900 rounded-2xl p-8 text-white ${className}`}>
      <div className="max-w-2xl mx-auto text-center">
        {/* Error Icon and Title */}
        <div className="mb-6">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <ErrorIcon className="w-8 h-8 text-red-400" />
          </div>
          
          <h1 className="text-3xl font-bold mb-2">{getErrorTitle()}</h1>
          <p className="text-xl text-gray-300">{error.message}</p>
          
          {error.code && (
            <p className="text-sm text-gray-400 mt-2">Error Code: {error.code}</p>
          )}
        </div>

        {/* Error Details and Suggestions */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center justify-center">
            <Shield className="w-5 h-5 mr-2" />
            What You Can Do
          </h2>
          
          <div className="text-left space-y-3">
            {getErrorSuggestions().map((suggestion, index) => (
              <div key={index} className="flex items-start">
                <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                  <span className="text-blue-400 text-sm font-semibold">{index + 1}</span>
                </div>
                <span className="text-gray-300">{suggestion}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Retry Information */}
        {retryCount > 0 && (
          <div className="bg-yellow-500/10 border border-yellow-400/30 rounded-lg p-4 mb-6">
            <p className="text-yellow-200">
              Attempt {retryCount} of {maxRetries}
              {!canRetry && ' - Maximum retry attempts reached'}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="outline"
            onClick={onBack}
            icon={ArrowLeft}
            iconPosition="left"
            className="flex-1 max-w-xs"
          >
            Back to Payment
          </Button>

          {canRetry && (
            <Button
              variant="primary"
              onClick={onRetry}
              icon={RefreshCw}
              iconPosition="left"
              className="flex-1 max-w-xs bg-blue-600 hover:bg-blue-700"
            >
              Try Again
            </Button>
          )}

          <Button
            variant="secondary"
            onClick={onContactSupport}
            icon={Mail}
            iconPosition="left"
            className="flex-1 max-w-xs"
          >
            Contact Support
          </Button>
        </div>

        {/* Alternative Payment Methods */}
        <div className="mt-8 pt-6 border-t border-white/20">
          <h3 className="text-lg font-semibold mb-4">Alternative Options</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white/5 rounded-lg p-4">
              <Phone className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <h4 className="font-semibold mb-2">Phone Payment</h4>
              <p className="text-sm text-gray-300 mb-3">
                Call us to complete your payment over the phone
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open('tel:+1-555-AUTOMARK', '_self')}
              >
                Call Now
              </Button>
            </div>
            
            <div className="bg-white/5 rounded-lg p-4">
              <ExternalLink className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <h4 className="font-semibold mb-2">Bank Transfer</h4>
              <p className="text-sm text-gray-300 mb-3">
                Complete payment via secure bank transfer
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open('mailto:payments@automark.ai?subject=Bank Transfer Request', '_blank')}
              >
                Request Details
              </Button>
            </div>
          </div>
        </div>

        {/* Security Assurance */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <Shield className="w-4 h-4 mr-1" />
              SSL Encrypted
            </div>
            <div className="flex items-center">
              <CreditCard className="w-4 h-4 mr-1" />
              PCI Compliant
            </div>
          </div>
          <p className="mt-2">Your payment information is secure and protected</p>
        </div>
      </div>
    </div>
  );
};

export default PaymentErrorHandler;