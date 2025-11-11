import React from 'react';
import { Star, Quote, TrendingUp, Users, Award, CheckCircle } from 'lucide-react';
import { Card } from '../ui';

const SocialProofSection: React.FC = () => {
  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Marketing Director',
      company: 'TechFlow Solutions',
      avatar: 'SC',
      rating: 5,
      quote: 'Unitasa connected our HubSpot to AI automation in literally 2 clicks. We\'ve seen 340% increase in qualified leads and saved 25 hours per week on manual tasks.',
      metrics: {
        leadIncrease: '340%',
        timeSaved: '25h/week',
        roi: '450%'
      }
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Founder & CEO',
      company: 'GrowthLab',
      avatar: 'MR',
      rating: 5,
      quote: 'The Pipedrive integration was seamless. Our lead response time went from hours to seconds, and the AI actually understands our business context. Game changer.',
      metrics: {
        responseTime: '< 30 sec',
        conversionRate: '67%',
        leadQuality: '89%'
      }
    },
    {
      name: 'Emily Watson',
      role: 'Sales Operations',
      company: 'ScaleUp Ventures',
      avatar: 'EW',
      rating: 5,
      quote: 'We tried 5 different automation tools before Unitasa. This is the first one that actually works with our Zoho CRM without breaking our existing workflows.',
      metrics: {
        toolsReplaced: '5',
        setupTime: '15 min',
        satisfaction: '98%'
      }
    }
  ];

  const stats = [
    {
      icon: Users,
      value: '2,500+',
      label: 'Businesses Automated',
      description: 'Growing companies trust Unitasa'
    },
    {
      icon: TrendingUp,
      value: '340%',
      label: 'Average Lead Increase',
      description: 'Typical results within 30 days'
    },
    {
      icon: CheckCircle,
      value: '99.9%',
      label: 'Uptime Guarantee',
      description: 'Enterprise-grade reliability'
    },
    {
      icon: Award,
      value: '4.9/5',
      label: 'Customer Rating',
      description: 'Based on 500+ reviews'
    }
  ];

  const certifications = [
    { name: 'SOC 2 Type II', description: 'Security & Compliance' },
    { name: 'GDPR Compliant', description: 'Data Protection' },
    { name: 'ISO 27001', description: 'Information Security' },
    { name: 'PCI DSS', description: 'Payment Security' }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        {/* <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Trusted by Growing Businesses Worldwide
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join thousands of companies that have transformed their marketing automation 
            and achieved measurable growth with Unitasa.
          </p>
        </div> */}

        {/* Key Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {stats.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <Card key={index} className="p-6 text-center" hover>
                <div className="bg-primary-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <IconComponent className="w-6 h-6 text-primary-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="font-semibold text-gray-700 mb-1">{stat.label}</div>
                <div className="text-sm text-gray-500">{stat.description}</div>
              </Card>
            );
          })}
        </div>



        {/* Trust Indicators */}
        <div className="bg-white rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Enterprise-Grade Security & Compliance
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {certifications.map((cert, index) => (
              <div key={index} className="text-center p-4 border border-gray-200 rounded-lg">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div className="font-semibold text-gray-900 mb-1">{cert.name}</div>
                <div className="text-sm text-gray-600">{cert.description}</div>
              </div>
            ))}
          </div>

          {/* Additional Trust Elements */}
          <div className="border-t border-gray-200 pt-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">99.9%</div>
                <div className="text-gray-600">Uptime SLA</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">24/7</div>
                <div className="text-gray-600">Expert Support</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">30-Day</div>
                <div className="text-gray-600">Money-Back Guarantee</div>
              </div>
            </div>
          </div>
        </div>

        {/* Social Proof CTA */}
        <div className="text-center mt-16">
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Don't take our word for it. See how Unitasa can transform your marketing automation 
            with a personalized assessment of your current setup.
          </p>
          <button className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition-colors">
            Get Your Free Assessment
          </button>
        </div>
      </div>
    </section>
  );
};

export default SocialProofSection;
