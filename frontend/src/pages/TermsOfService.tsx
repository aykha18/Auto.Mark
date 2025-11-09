import React from 'react';
import { FileText, ArrowLeft } from 'lucide-react';

const TermsOfService: React.FC = () => {
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
            <FileText className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Terms of Service</h1>
          </div>
          
          <p className="text-sm text-gray-600 mb-8">Last Updated: January 2025</p>

          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
              <p>
                By accessing and using Unitasa's services, you accept and agree to be bound by these Terms of Service.
                If you do not agree to these terms, please do not use our services.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Description of Service</h2>
              <p className="mb-3">
                Unitasa provides an AI-powered marketing intelligence platform that includes:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>AI marketing assessment and analysis</li>
                <li>CRM integration recommendations</li>
                <li>Marketing automation tools</li>
                <li>Co-Creator Program access</li>
                <li>Consultation and implementation services</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Co-Creator Program</h2>
              <p className="mb-3">
                The Co-Creator Program offers founding members:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Lifetime access to the Unitasa platform</li>
                <li>Priority support and direct product influence</li>
                <li>Special pricing at ₹41,251 INR (one-time payment)</li>
                <li>Early access to new features</li>
              </ul>
              <p className="mt-3">
                Limited to 25 founding members. Program terms and benefits are subject to the specific agreement
                provided at the time of enrollment.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Payment Terms</h2>
              <p className="mb-3">
                Payment processing is handled securely through Razorpay. By making a payment, you agree to:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Provide accurate billing information</li>
                <li>Pay all fees associated with your purchase</li>
                <li>Authorize us to charge your payment method</li>
              </ul>
              <p className="mt-3">
                All prices are listed in INR and USD. Currency conversion rates are approximate and may vary.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Refund Policy</h2>
              <p>
                We offer a 30-day money-back guarantee for the Co-Creator Program. If you're not satisfied with
                the service, contact us within 30 days of purchase for a full refund. Refunds are processed within
                7-10 business days.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">6. User Responsibilities</h2>
              <p className="mb-3">You agree to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Provide accurate information</li>
                <li>Maintain the security of your account</li>
                <li>Use the service in compliance with applicable laws</li>
                <li>Not misuse or attempt to disrupt the service</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Intellectual Property</h2>
              <p>
                All content, features, and functionality of Unitasa are owned by us and are protected by
                international copyright, trademark, and other intellectual property laws.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Limitation of Liability</h2>
              <p>
                Unitasa shall not be liable for any indirect, incidental, special, consequential, or punitive
                damages resulting from your use of or inability to use the service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Changes to Terms</h2>
              <p>
                We reserve the right to modify these terms at any time. We will notify users of any material
                changes via email or through the platform.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Contact Information</h2>
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

export default TermsOfService;
