import React from 'react';
import { Shield, ArrowLeft } from 'lucide-react';

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => {
            window.history.pushState({}, '', '/');
            window.dispatchEvent(new PopStateEvent('popstate'));
          }}
          className="flex items-center text-blue-600 hover:text-blue-700 mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Home
        </button>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center mb-6">
            <Shield className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
          </div>
          
          <p className="text-sm text-gray-600 mb-8">Last Updated: January 2025</p>

          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Information We Collect</h2>
              <p className="mb-3">
                At Unitasa, we collect information that you provide directly to us, including:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Name, email address, and contact information</li>
                <li>Company name and business details</li>
                <li>CRM system information and preferences</li>
                <li>Assessment responses and marketing data</li>
                <li>Payment and billing information</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">2. How We Use Your Information</h2>
              <p className="mb-3">We use the information we collect to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Provide, maintain, and improve our services</li>
                <li>Process your transactions and send related information</li>
                <li>Send you technical notices and support messages</li>
                <li>Respond to your comments and questions</li>
                <li>Provide personalized AI marketing recommendations</li>
                <li>Analyze usage patterns and optimize our platform</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Information Sharing</h2>
              <p className="mb-3">
                We do not sell your personal information. We may share your information only in the following circumstances:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>With your consent or at your direction</li>
                <li>With service providers who perform services on our behalf</li>
                <li>To comply with legal obligations</li>
                <li>To protect our rights and prevent fraud</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Security</h2>
              <p>
                We implement appropriate technical and organizational measures to protect your personal information
                against unauthorized access, alteration, disclosure, or destruction. All payment transactions are
                processed through secure payment gateways (Razorpay) with industry-standard encryption.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Your Rights</h2>
              <p className="mb-3">You have the right to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Access your personal information</li>
                <li>Correct inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Object to processing of your data</li>
                <li>Export your data</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Cookies and Tracking</h2>
              <p>
                We use cookies and similar tracking technologies to collect information about your browsing activities
                and to provide personalized experiences. You can control cookies through your browser settings.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Contact Us</h2>
              <p className="mb-3">
                If you have any questions about this Privacy Policy, please contact us:
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p><strong>Email:</strong> support@unitasa.com</p>
                <p><strong>Phone:</strong> +91 976 858 4622 / +91 790 006 6916</p>
                <p><strong>Website:</strong> https://unitasa.in</p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
