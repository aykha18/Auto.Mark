import React from 'react';
import { RefreshCw } from 'lucide-react';

const RefundPolicy: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center mb-6">
            <RefreshCw className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Refund & Cancellation Policy</h1>
          </div>
          
          <p className="text-sm text-gray-600 mb-8">Last Updated: January 2025</p>

          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">30-Day Money-Back Guarantee</h2>
              <p>
                We stand behind the quality of our service. If you're not completely satisfied with the Unitasa
                Co-Creator Program, we offer a full refund within 30 days of your purchase.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Eligibility for Refund</h2>
              <p className="mb-3">You are eligible for a refund if:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>You request a refund within 30 days of purchase</li>
                <li>You have made a genuine attempt to use the platform</li>
                <li>You provide feedback on why the service didn't meet your needs</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">How to Request a Refund</h2>
              <p className="mb-3">To request a refund:</p>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Contact our support team at support@unitasa.com</li>
                <li>Include your order number and reason for refund</li>
                <li>Our team will review your request within 2 business days</li>
                <li>Once approved, refunds are processed within 7-10 business days</li>
              </ol>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Refund Processing</h2>
              <p className="mb-3">
                Refunds will be credited to the original payment method used for purchase:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Credit/Debit Card: 7-10 business days</li>
                <li>UPI/Net Banking: 5-7 business days</li>
                <li>International Cards: 10-14 business days</li>
              </ul>
              <p className="mt-3">
                Please note that processing times may vary depending on your bank or payment provider.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Cancellation Policy</h2>
              <p>
                You may cancel your Co-Creator Program membership at any time. Since this is a one-time payment
                for lifetime access, cancellation means you will no longer have access to the platform and
                associated benefits. Refunds for cancellations are subject to the 30-day money-back guarantee
                period mentioned above.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Non-Refundable Items</h2>
              <p className="mb-3">The following are not eligible for refunds:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Consultation services already delivered</li>
                <li>Custom implementation work completed</li>
                <li>Requests made after the 30-day period</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Us</h2>
              <p className="mb-3">
                For any questions about our refund policy or to request a refund, please contact us:
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p><strong>Email:</strong> support@unitasa.com</p>
                <p><strong>Phone:</strong> +91 976 858 4622 / +91 790 006 6916</p>
                <p><strong>Website:</strong> https://unitasa.in</p>
                <p className="mt-2 text-sm text-gray-600">
                  Support Hours: Monday - Friday, 9:00 AM - 6:00 PM IST
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RefundPolicy;
