import React from 'react';
import { Check, X, Crown, Zap, Star } from 'lucide-react';
import Button from '../ui/Button';

interface PricingTier {
  name: string;
  price: string;
  originalPrice?: string;
  period: string;
  description: string;
  features: string[];
  limitations?: string[];
  highlighted?: boolean;
  badge?: string;
  icon?: React.ReactNode;
}

const PricingComparison: React.FC = () => {
  const pricingTiers: PricingTier[] = [
    {
      name: 'Standard Access',
      price: '$99',
      period: '/month',
      description: 'Basic AI marketing automation with standard support',
      features: [
        'Basic AI automation',
        'Standard CRM integrations',
        'Email support',
        'Monthly feature updates',
        'Basic analytics dashboard'
      ],
      limitations: [
        'Limited AI decisions per hour',
        'No priority support',
        'No product influence',
        'Standard feature rollout'
      ],
      icon: <Zap className="w-6 h-6" />
    },
    {
      name: 'Founding Co-Creator',
      price: '$497',
      originalPrice: '$2,000+',
      period: 'one-time',
      description: 'Lifetime access + direct product influence + priority everything',
      features: [
        'Lifetime platform access (all future features)',
        'Unlimited AI decisions per hour',
        'Priority CRM integration support',
        'Direct founder communication channel',
        'Vote on product roadmap',
        'Beta access (3-6 months early)',
        'Personal AI strategy audit ($500 value)',
        'Custom AI agent setup ($300 value)',
        '6-month priority support ($600 value)',
        'Exclusive founder mastermind community',
        'Co-creator badge and recognition',
        'Revenue sharing on referrals'
      ],
      highlighted: true,
      badge: '🔥 75% OFF - LIMITED TIME',
      icon: <Crown className="w-6 h-6 text-yellow-500" />
    },
    {
      name: 'Enterprise',
      price: '$500+',
      period: '/month',
      description: 'Custom AI solutions for large organizations',
      features: [
        'Custom AI model training',
        'Dedicated account manager',
        'White-label options',
        'Advanced security features',
        'Custom integrations'
      ],
      limitations: [
        'Annual contract required',
        'Complex setup process',
        'Higher ongoing costs'
      ],
      icon: <Star className="w-6 h-6" />
    }
  ];

  const calculateAnnualSavings = () => {
    const standardAnnual = 99 * 12; // $1,188
    const founderPrice = 497;
    return standardAnnual - founderPrice; // $691 first year savings
  };

  const calculateLifetimeValue = () => {
    const standardMonthly = 99;
    const yearsOfUse = 5; // Conservative estimate
    const totalStandardCost = standardMonthly * 12 * yearsOfUse; // $5,940
    const founderPrice = 497;
    return totalStandardCost - founderPrice; // $5,443 lifetime savings
  };

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Founder Pricing vs Standard Access
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join as a founding co-creator and save over <strong>${calculateLifetimeValue().toLocaleString()}</strong> 
            while getting lifetime access and exclusive benefits.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {pricingTiers.map((tier, index) => (
            <div
              key={index}
              className={`bg-white rounded-2xl shadow-lg overflow-hidden relative ${
                tier.highlighted 
                  ? 'ring-4 ring-blue-500 transform scale-105' 
                  : 'hover:shadow-xl transition-shadow'
              }`}
            >
              {/* Badge */}
              {tier.badge && (
                <div className="absolute top-4 left-4 right-4 z-10">
                  <div className="bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full text-center animate-pulse">
                    {tier.badge}
                  </div>
                </div>
              )}

              <div className={`p-8 ${tier.highlighted ? 'bg-gradient-to-br from-blue-50 to-purple-50' : ''}`}>
                {/* Header */}
                <div className="text-center mb-8">
                  <div className="flex items-center justify-center mb-4">
                    {tier.icon}
                    <h3 className="text-2xl font-bold text-gray-900 ml-2">{tier.name}</h3>
                  </div>
                  
                  <div className="mb-4">
                    {tier.originalPrice && (
                      <div className="text-lg text-gray-500 line-through mb-1">
                        {tier.originalPrice}
                      </div>
                    )}
                    <div className="flex items-baseline justify-center">
                      <span className={`text-5xl font-bold ${
                        tier.highlighted ? 'text-blue-600' : 'text-gray-900'
                      }`}>
                        {tier.price}
                      </span>
                      <span className="text-xl text-gray-600 ml-1">{tier.period}</span>
                    </div>
                  </div>
                  
                  <p className="text-gray-600">{tier.description}</p>
                </div>

                {/* Features */}
                <div className="space-y-4 mb-8">
                  {tier.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                  
                  {tier.limitations?.map((limitation, limitIndex) => (
                    <div key={limitIndex} className="flex items-start opacity-60">
                      <X className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                      <span className="text-gray-600">{limitation}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <Button
                  className={`w-full ${
                    tier.highlighted 
                      ? 'bg-blue-600 hover:bg-blue-700' 
                      : 'bg-gray-800 hover:bg-gray-900'
                  }`}
                  size="lg"
                >
                  {tier.highlighted ? 'Secure Founding Spot' : 
                   tier.name === 'Standard Access' ? 'Start Free Trial' : 'Contact Sales'}
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Value Comparison */}
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Founding Co-Creator ROI Analysis
          </h3>
          
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="bg-green-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-green-600 mb-2">
                ${calculateAnnualSavings().toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">First Year Savings</div>
              <div className="text-xs text-gray-500 mt-1">vs Standard Monthly Plan</div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                ${calculateLifetimeValue().toLocaleString()}+
              </div>
              <div className="text-sm text-gray-600">Lifetime Value</div>
              <div className="text-xs text-gray-500 mt-1">Conservative 5-year estimate</div>
            </div>
            
            <div className="bg-purple-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                $1,400+
              </div>
              <div className="text-sm text-gray-600">Bonus Value Included</div>
              <div className="text-xs text-gray-500 mt-1">Audit + Setup + Support</div>
            </div>
          </div>
          
          <div className="text-center mt-8">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 max-w-2xl mx-auto">
              <h4 className="font-bold text-gray-900 mb-2">
                🚀 Founding Member Exclusive Benefits
              </h4>
              <p className="text-gray-600 text-sm">
                Beyond the massive cost savings, you get direct influence over product development, 
                priority support, and lifetime access to all future AI features. This is your chance 
                to be part of the founding story of autonomous AI marketing.
              </p>
            </div>
          </div>
        </div>

        {/* Urgency Section */}
        <div className="text-center mt-16">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-lg mx-auto">
            <h4 className="font-bold text-red-800 mb-2">⏰ Founder Pricing Ends Soon</h4>
            <p className="text-red-700 text-sm mb-4">
              Only 12 founding spots remaining. Price increases to $2,000+ after founding phase.
            </p>
            <Button className="bg-red-600 hover:bg-red-700">
              Secure Your Spot Now
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PricingComparison;