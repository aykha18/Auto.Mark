import React from 'react';
import { Mail, Phone, MapPin, Clock, MessageCircle, ArrowLeft } from 'lucide-react';

const Contact: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
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
        
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Contact Us</h1>
          <p className="text-xl text-gray-600">
            We're here to help! Reach out to us through any of the channels below.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Get in Touch</h2>
            
            <div className="space-y-6">
              <div className="flex items-start">
                <Mail className="w-6 h-6 text-blue-600 mr-4 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Email</h3>
                  <a href="mailto:support@unitasa.com" className="text-blue-600 hover:underline">
                    support@unitasa.com
                  </a>
                  <p className="text-sm text-gray-600 mt-1">
                    We typically respond within 24 hours
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <Phone className="w-6 h-6 text-blue-600 mr-4 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Phone</h3>
                  <p>
                    <a href="tel:+919768584622" className="text-blue-600 hover:underline">
                      +91 976 858 4622
                    </a>
                  </p>
                  <p>
                    <a href="tel:+917900066916" className="text-blue-600 hover:underline">
                      +91 790 006 6916
                    </a>
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Monday - Friday, 9:00 AM - 6:00 PM IST
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <Clock className="w-6 h-6 text-blue-600 mr-4 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Business Hours</h3>
                  <p className="text-gray-700">Monday - Friday: 9:00 AM - 6:00 PM IST</p>
                  <p className="text-gray-700">Saturday: 10:00 AM - 2:00 PM IST</p>
                  <p className="text-gray-700">Sunday: Closed</p>
                </div>
              </div>

              <div className="flex items-start">
                <MapPin className="w-6 h-6 text-blue-600 mr-4 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Location</h3>
                  <p className="text-gray-700">India</p>
                  <p className="text-sm text-gray-600 mt-1">
                    Serving clients globally
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
              
              <div className="space-y-4">
                <a
                  href="https://calendly.com/khanayubchand/ai-strategy-session"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-4 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  <div className="flex items-center">
                    <MessageCircle className="w-6 h-6 text-blue-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Book a Consultation</h3>
                      <p className="text-sm text-gray-600">Schedule a free 30-minute strategy session</p>
                    </div>
                  </div>
                </a>

                <button
                  onClick={() => window.dispatchEvent(new CustomEvent('openLeadCapture'))}
                  className="block w-full p-4 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-center">
                    <MessageCircle className="w-6 h-6 text-gray-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Take AI Assessment</h3>
                      <p className="text-sm text-gray-600">Get personalized recommendations</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Need Immediate Help?</h3>
              <p className="text-gray-700 mb-4">
                For urgent inquiries, please call us directly or send an email with "URGENT" in the subject line.
              </p>
              <p className="text-sm text-gray-600">
                We prioritize urgent requests and aim to respond within 2 hours during business hours.
              </p>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">What is the Co-Creator Program?</h3>
              <p className="text-gray-700">
                The Co-Creator Program offers founding members lifetime access to Unitasa's AI marketing platform
                at a special price of ₹41,500 INR / $497 USD, with priority support and direct product influence.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">How do refunds work?</h3>
              <p className="text-gray-700">
                We offer a 30-day money-back guarantee. If you're not satisfied, contact us within 30 days for
                a full refund, processed within 7-10 business days.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Which payment methods do you accept?</h3>
              <p className="text-gray-700">
                We accept all major payment methods through Razorpay: UPI, Credit/Debit Cards, Net Banking,
                and International Cards (Visa, Mastercard, Amex).
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Do you offer implementation support?</h3>
              <p className="text-gray-700">
                Yes! Co-Creator Program members receive personalized implementation support, including strategy
                sessions, CRM integration guidance, and ongoing technical assistance.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
