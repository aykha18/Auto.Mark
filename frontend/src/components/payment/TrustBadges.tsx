import React from 'react';
import {
  Shield,
  Lock,
  CreditCard,
  CheckCircle,
  Star,
  Award,
  Zap,
  Globe
} from 'lucide-react';

interface TrustBadgesProps {
  variant?: 'horizontal' | 'vertical' | 'grid';
  size?: 'sm' | 'md' | 'lg';
  showLabels?: boolean;
  className?: string;
}

const TrustBadges: React.FC<TrustBadgesProps> = ({
  variant = 'horizontal',
  size = 'md',
  showLabels = true,
  className = '',
}) => {
  const badges = [
    {
      icon: Shield,
      label: 'SSL Encrypted',
      description: '256-bit encryption',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10'
    },
    {
      icon: Lock,
      label: 'PCI Compliant',
      description: 'Level 1 certified',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'
    },
    {
      icon: Zap,
      label: 'Stripe Secure',
      description: 'Trusted by millions',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    {
      icon: CheckCircle,
      label: '30-Day Guarantee',
      description: 'Money back promise',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10'
    },
    {
      icon: Globe,
      label: 'Global Payments',
      description: 'Worldwide accepted',
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10'
    },
    {
      icon: Award,
      label: 'Trusted Platform',
      description: '99.9% uptime',
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10'
    }
  ];

  const sizeClasses = {
    sm: {
      icon: 'w-4 h-4',
      container: 'p-2',
      text: 'text-xs',
      badge: 'w-16 h-16'
    },
    md: {
      icon: 'w-5 h-5',
      container: 'p-3',
      text: 'text-sm',
      badge: 'w-20 h-20'
    },
    lg: {
      icon: 'w-6 h-6',
      container: 'p-4',
      text: 'text-base',
      badge: 'w-24 h-24'
    }
  };

  const currentSize = sizeClasses[size];

  const renderBadge = (badge: typeof badges[0], index: number) => (
    <div
      key={index}
      className={`${badge.bgColor} rounded-lg ${currentSize.container} flex items-center justify-center transition-all duration-300 hover:scale-105 ${
        variant === 'vertical' ? 'flex-col text-center' : 'flex-row'
      }`}
    >
      <badge.icon className={`${badge.color} ${currentSize.icon} ${
        variant === 'vertical' ? 'mb-2' : showLabels ? 'mr-2' : ''
      }`} />
      
      {showLabels && (
        <div className={variant === 'vertical' ? 'text-center' : ''}>
          <div className={`font-semibold text-white ${currentSize.text}`}>
            {badge.label}
          </div>
          {size !== 'sm' && (
            <div className={`text-gray-400 ${currentSize.text === 'text-base' ? 'text-sm' : 'text-xs'}`}>
              {badge.description}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const getContainerClasses = () => {
    switch (variant) {
      case 'horizontal':
        return 'flex flex-wrap items-center justify-center gap-3';
      case 'vertical':
        return 'flex flex-col space-y-3';
      case 'grid':
        return 'grid grid-cols-2 md:grid-cols-3 gap-3';
      default:
        return 'flex flex-wrap items-center justify-center gap-3';
    }
  };

  return (
    <div className={`${getContainerClasses()} ${className}`}>
      {badges.map((badge, index) => renderBadge(badge, index))}
    </div>
  );
};

// Simplified version for inline use
export const InlineTrustBadges: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`flex items-center justify-center space-x-6 text-sm text-gray-300 ${className}`}>
    <div className="flex items-center">
      <Shield className="w-4 h-4 mr-1 text-green-400" />
      SSL Encrypted
    </div>
    <div className="flex items-center">
      <Lock className="w-4 h-4 mr-1 text-blue-400" />
      PCI Compliant
    </div>
    <div className="flex items-center">
      <Zap className="w-4 h-4 mr-1 text-purple-400" />
      Stripe Secure
    </div>
  </div>
);

// Payment method badges
export const PaymentMethodBadges: React.FC<{ className?: string }> = ({ className = '' }) => {
  const paymentMethods = [
    { name: 'Visa', logo: '💳' },
    { name: 'Mastercard', logo: '💳' },
    { name: 'American Express', logo: '💳' },
    { name: 'Discover', logo: '💳' },
    { name: 'PayPal', logo: '🅿️' },
    { name: 'Apple Pay', logo: '🍎' },
    { name: 'Google Pay', logo: '🔵' }
  ];

  return (
    <div className={`flex flex-wrap items-center justify-center gap-2 ${className}`}>
      {paymentMethods.map((method, index) => (
        <div
          key={index}
          className="bg-white/10 rounded-lg px-3 py-2 flex items-center space-x-2 text-sm text-gray-300"
        >
          <span>{method.logo}</span>
          <span>{method.name}</span>
        </div>
      ))}
    </div>
  );
};

export default TrustBadges;
