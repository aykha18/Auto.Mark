import React, { useState, useEffect } from 'react';
import { Brain, Target, Zap, Shield, BarChart3, MessageCircle, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';
import AIReadinessAssessment from './AIReadinessAssessment';
import { LeadData } from './LeadCaptureForm';
import { paymentService } from '../../services/paymentService';

interface AssessmentStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

interface EnhancedAIAssessmentProps {
  onComplete?: (results: any) => void;
  onClose?: () => void;
  leadData?: LeadData | null;
}

const EnhancedAIAssessment: React.FC<EnhancedAIAssessmentProps> = ({ onComplete, onClose, leadData }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [assessmentData, setAssessmentData] = useState<Record<string, any>>({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const steps: AssessmentStep[] = [
    {
      id: 'welcome',
      title: 'AI Marketing Intelligence Assessment',
      description: 'Discover your AI readiness and unlock autonomous marketing potential',
      icon: <Brain className="w-8 h-8" />,
      component: (
        <div className="text-center py-12">
          <div className="mb-8">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Marketing Intelligence Unity Assessment
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Discover how Unitasa can replace your fragmented marketing tools with one unified platform. 
              Get your personalized marketing unity roadmap in just 3 minutes.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <Target className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">AI Readiness Score</h3>
              <p className="text-sm text-gray-600">Assess your current AI maturity level</p>
            </div>
            <div className="bg-green-50 p-6 rounded-lg">
              <Zap className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">ROI Prediction</h3>
              <p className="text-sm text-gray-600">Forecast your AI implementation impact</p>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg">
              <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Custom Roadmap</h3>
              <p className="text-sm text-gray-600">Get your personalized AI strategy</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">What You'll Discover:</h3>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <div className="flex items-start">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Your AI Marketing IQ Score (0-100)</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Predicted ROI improvement potential</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Priority automation opportunities</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Personalized AI agent recommendations</span>
              </div>
            </div>
          </div>

          <Button 
            size="lg" 
            onClick={() => setCurrentStep(1)}
            className="px-8 py-4 text-lg"
          >
            Start AI Assessment
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )
    },
    {
      id: 'ai-readiness',
      title: 'AI Readiness Assessment',
      description: 'Evaluate your current AI and automation capabilities',
      icon: <Brain className="w-8 h-8" />,
      component: <AIReadinessAssessment leadData={leadData} />
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleStepData = (stepId: string, data: any) => {
    setAssessmentData(prev => ({
      ...prev,
      [stepId]: data
    }));
  };

  if (showResults) {
    return (
      <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Assessment Complete!
          </h2>
          <p className="text-xl text-gray-600">
            Your AI Marketing Intelligence Report is ready
          </p>
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
            Next Steps: Activate Your AI Marketing Team
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <MessageCircle className="w-8 h-8 text-blue-600 mb-3" />
              <h4 className="font-semibold text-gray-900 mb-2">
                Schedule AI Strategy Session
              </h4>
              <p className="text-sm text-gray-600 mb-4">
                Get a personalized 30-minute consultation to discuss your AI implementation roadmap
              </p>
              <Button size="sm" className="w-full">
                Book Free Session
              </Button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-purple-200">
              <div className="flex items-center justify-between mb-3">
                <Zap className="w-8 h-8 text-purple-600" />
                <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-semibold">
                  LIMITED TIME
                </span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Join 25 Founding Co-Creators
              </h4>
              <div className="mb-3">
                <div className="text-2xl font-bold text-purple-600">$497</div>
                <div className="text-xs text-gray-500 line-through">Regular: $2,000+</div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Lifetime access to AI platform + direct product influence + priority support
              </p>
              <Button 
                size="sm" 
                className="w-full bg-purple-600 hover:bg-purple-700"
                onClick={() => {
                  console.log('🎯 Secure Founding Spot clicked - Opening Razorpay Payment!');
                  
                  // Create proper Razorpay payment modal using DOM
                  if (!document.getElementById('razorpay-payment-modal')) {
                    const modal = document.createElement('div');
                    modal.id = 'razorpay-payment-modal';
                    modal.style.cssText = `
                      position: fixed;
                      top: 0;
                      left: 0;
                      width: 100vw;
                      height: 100vh;
                      background: rgba(0, 0, 0, 0.8);
                      z-index: 999999;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      font-family: Arial, sans-serif;
                    `;
                    
                    modal.innerHTML = `
                      <div style="
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        text-align: center;
                        max-width: 500px;
                        width: 90%;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                      ">
                        <h2 style="color: #7c3aed; font-size: 28px; margin-bottom: 20px;">
                          🚀 Co-Creator Program
                        </h2>
                        
                        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                          <div style="font-size: 28px; font-weight: bold; color: #7c3aed;">
                            $497 USD
                          </div>
                          <div style="font-size: 18px; font-weight: bold; color: #7c3aed; margin-top: 5px;">
                            ₹41,500 INR
                          </div>
                          <div style="font-size: 14px; color: #6b7280; text-decoration: line-through; margin-top: 8px;">
                            Regular: $2,000+ / ₹1,67,000+
                          </div>
                          <div style="font-size: 14px; color: #059669; font-weight: 600; margin-top: 5px;">
                            🚀 Founding Member Price • ⚡ Only 12 spots left
                          </div>
                        </div>
                        
                        <p style="font-size: 16px; color: #374151; margin-bottom: 25px;">
                          Lifetime access to AI platform + direct product influence + priority support
                        </p>
                        
                        <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                          <button onclick="processPayment()" 
                                  style="background: #7c3aed; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600;">
                            💳 Pay with Razorpay
                          </button>
                          
                          <button onclick="closePaymentModal()" 
                                  style="background: #6b7280; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">
                            Cancel
                          </button>
                        </div>
                        
                        <div style="margin-top: 20px; font-size: 12px; color: #6b7280;">
                          🔒 Secure payment powered by Razorpay • 256-bit SSL encryption
                        </div>
                      </div>
                    `;
                    
                    document.body.appendChild(modal);
                    console.log('💳 Razorpay payment modal created successfully!');
                    
                    // Add global functions for the modal
                    (window as any).processPayment = function() {
                      console.log('💳 Opening Razorpay checkout...');
                      
                      // Load Razorpay script if not already loaded
                      if (!(window as any).Razorpay) {
                        const script = document.createElement('script');
                        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
                        script.onload = function() {
                          openRazorpayCheckout();
                        };
                        document.head.appendChild(script);
                      } else {
                        openRazorpayCheckout();
                      }
                      
                      function openRazorpayCheckout() {
                        // Currency detection and conversion
                        const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                        const isIndianUser = userTimezone.includes('Asia/Kolkata') || userTimezone.includes('Asia/Calcutta');
                        
                        // Pricing: $497 USD = ₹41,500 INR (approximate conversion rate 1 USD = 83.5 INR)
                        const usdPrice = 497;
                        const inrPrice = Math.round(usdPrice * 83.5); // ₹41,500
                        
                        const currency = isIndianUser ? 'INR' : 'INR'; // Razorpay primarily supports INR
                        const amount = isIndianUser ? inrPrice * 100 : usdPrice * 83.5 * 100; // Convert to paise
                        const displayPrice = isIndianUser ? `₹${inrPrice.toLocaleString('en-IN')}` : `$${usdPrice} (₹${inrPrice.toLocaleString('en-IN')})`;
                        
                        console.log('💰 Pricing Details:', {
                          userTimezone,
                          isIndianUser,
                          currency,
                          amount: amount / 100,
                          displayPrice
                        });
                        
                        const options = {
                          key: 'rzp_test_RcQxnSEfdjl6Nr', // Your actual Razorpay test key
                          amount: amount, // Amount in paise
                          currency: currency,
                          name: 'Unitasa Co-Creator Program',
                          description: `Founding Member Access - ${displayPrice}`,
                          image: '/logo.png', // Your logo URL
                          handler: function(response: any) {
                            console.log('✅ Payment successful:', response);
                            alert('🎉 Payment successful! Welcome to the Co-Creator Program!\\n\\nPayment ID: ' + response.razorpay_payment_id + '\\n\\nYou will receive onboarding instructions via email shortly.');
                            (window as any).closePaymentModal();
                          },
                          prefill: {
                            name: leadData?.name || 'Co-Creator Member',
                            email: leadData?.email || 'member@unitasa.in',
                            contact: '+919999999999'
                          },
                          notes: {
                            program: 'Co-Creator Founding Member',
                            price_usd: '$497',
                            price_inr: `₹${inrPrice.toLocaleString('en-IN')}`,
                            currency: currency,
                            spots_remaining: '12',
                            user_timezone: userTimezone
                          },
                          theme: {
                            color: '#7c3aed'
                          },
                          method: {
                            netbanking: true,
                            card: true,
                            upi: true,
                            wallet: true,
                            emi: false,
                            paylater: false
                          },
                          modal: {
                            ondismiss: function() {
                              console.log('❌ Payment cancelled by user');
                            }
                          }
                        };
                        
                        const rzp = new (window as any).Razorpay(options);
                        rzp.open();
                      }
                    };
                    
                    (window as any).closePaymentModal = function() {
                      const modal = document.getElementById('razorpay-payment-modal');
                      if (modal) {
                        modal.remove();
                        console.log('💳 Payment modal closed');
                      }
                    };
                  }
                }}
              >
                Secure Founding Spot
              </Button>
              
              {/* Emergency Test - Native HTML Button */}
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('🚨 NATIVE BUTTON CLICKED IN ASSESSMENT!');
                  alert('Native button in assessment works!');
                  setShowPaymentModal(true);
                }}
                style={{
                  background: '#ef4444',
                  color: 'white',
                  padding: '8px 16px',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  width: '100%',
                  marginTop: '8px',
                  fontSize: '14px'
                }}
              >
                🚨 EMERGENCY TEST - CLICK ME
              </button>
              
              {/* Debug State Display */}
              <div style={{
                background: '#f3f4f6',
                padding: '10px',
                marginTop: '10px',
                borderRadius: '4px',
                fontSize: '12px',
                fontFamily: 'monospace',
                border: '1px solid #d1d5db'
              }}>
                <strong>🔍 Debug State:</strong><br/>
                showPaymentModal: {showPaymentModal ? 'true' : 'false'}<br/>
                paymentSuccess: {paymentSuccess ? 'true' : 'false'}
              </div>
              
              <div className="text-xs text-center text-gray-500 mt-2">
                ⚡ Only 12 spots remaining
              </div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Button onClick={onClose} variant="outline" className="mr-4">
            Close Assessment
          </Button>
          <Button onClick={() => {
            // For now, just call onComplete - you can add AI Report Modal here too if needed
            onComplete?.(assessmentData);
          }}>
            Get Full AI Report
          </Button>
        </div>
      </div>
    );
  }

  const currentStepData = steps[currentStep];

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 max-w-4xl mx-auto">
      {/* Progress Header */}
      {currentStep > 0 && (
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {currentStepData.title}
            </h2>
            <span className="text-sm text-gray-500">
              Step {currentStep} of {steps.length - 1}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Step Content */}
      <div className="p-6">
        {currentStepData.component}
      </div>

      {/* Navigation */}
      {currentStep > 0 && (
        <div className="p-6 border-t border-gray-200 flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          <Button onClick={handleNext}>
            {currentStep === steps.length - 1 ? 'Complete Assessment' : 'Continue'}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      )}

      {/* ULTRA AGGRESSIVE MODAL - WILL DEFINITELY SHOW */}
      {showPaymentModal && (
        <div style={{
          position: 'fixed',
          top: '0px',
          left: '0px',
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(255, 0, 0, 0.9)',
          zIndex: '999999',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Arial, sans-serif'
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            padding: '40px',
            borderRadius: '10px',
            textAlign: 'center',
            maxWidth: '500px',
            width: '90%',
            border: '5px solid #ff0000',
            boxShadow: '0 0 50px rgba(0,0,0,0.8)'
          }}>
            <h1 style={{ 
              color: '#ff0000', 
              fontSize: '32px', 
              marginBottom: '20px',
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
            }}>
              🚨 MODAL IS WORKING! 🚨
            </h1>
            
            <p style={{ fontSize: '18px', marginBottom: '20px', color: '#333' }}>
              <strong>SUCCESS!</strong> The button clicks are working and the modal is rendering!
            </p>
            
            <div style={{ 
              backgroundColor: '#f0f0f0', 
              padding: '15px', 
              borderRadius: '5px',
              marginBottom: '20px',
              fontFamily: 'monospace'
            }}>
              <strong>Debug Info:</strong><br/>
              showPaymentModal: {showPaymentModal ? 'TRUE' : 'FALSE'}<br/>
              paymentSuccess: {paymentSuccess ? 'TRUE' : 'FALSE'}
            </div>
            
            <p style={{ fontSize: '16px', marginBottom: '30px', color: '#666' }}>
              This proves the React state management and modal rendering is working correctly!
            </p>
            
            <button
              onClick={() => {
                console.log('🎉 Modal close button clicked');
                setShowPaymentModal(false);
                alert('Modal closed successfully! The button functionality is working perfectly.');
              }}
              style={{
                backgroundColor: '#22c55e',
                color: 'white',
                padding: '15px 30px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              ✅ CLOSE MODAL - IT WORKS!
            </button>
          </div>
        </div>
      )}

      {/* Success State */}
      {paymentSuccess && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-auto text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to the Co-Creator Program!</h3>
            <p className="text-gray-600 mb-6">
              Your payment was successful. You'll receive onboarding instructions via email shortly.
            </p>
            <Button
              onClick={() => {
                setPaymentSuccess(false);
                setShowPaymentModal(false);
              }}
              className="w-full"
            >
              Continue
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAIAssessment;
