import React, { useState } from 'react';
import Button from '../ui/Button';
import RazorpayCheckout from '../payment/RazorpayCheckout';

const PaymentTest: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [testAmount, setTestAmount] = useState<number>(1); // Default to ₹1 for testing
  const [showPayment, setShowPayment] = useState(false);

  const getApiUrl = () => {
    // In production (not localhost), always use relative URLs
    if (window.location.hostname !== 'localhost' &&
        window.location.hostname !== '127.0.0.1') {
      console.log('Production detected, using relative URLs');
      return ''; // Relative URLs will use the same domain
    }

    // If REACT_APP_API_URL is set and it's not the placeholder, use it
    if (process.env.REACT_APP_API_URL &&
        !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app') &&
        !process.env.REACT_APP_API_URL.includes('railway.app')) {
      console.log('Using REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
      return process.env.REACT_APP_API_URL;
    }

    // Development default
    console.log('Using localhost default');
    return 'http://localhost:8000';
  };

  const testHealth = async () => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/api/v1/health`);
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(`Error: ${error}`);
    }
  };

  const testPaymentOrder = async () => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/api/v1/payments/razorpay/test-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ amount: testAmount })
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(`Error: ${error}`);
    }
  };

  const handlePaymentSuccess = (data: any) => {
    setResult(`✅ Payment Success: ${JSON.stringify(data, null, 2)}`);
    setShowPayment(false);
  };

  const handlePaymentError = (error: string) => {
    setResult(`❌ Payment Error: ${error}`);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">💳 Production Payment Testing</h2>

      {/* Test Amount Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Test Amount (USD):
        </label>
        <input
          type="number"
          value={testAmount}
          onChange={(e) => setTestAmount(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="0.01"
          step="0.01"
        />
        <p className="text-sm text-gray-500 mt-1">
          Will show as ₹{Math.round(testAmount * 83).toLocaleString()} for INR or ${testAmount} for USD
        </p>
      </div>

      {/* Test Buttons */}
      <div className="flex gap-4 mb-6 flex-wrap">
        <Button onClick={testHealth}>
          Test Health
        </Button>
        <Button onClick={testPaymentOrder} variant="outline">
          Test Order API
        </Button>
        <Button onClick={() => setShowPayment(true)} className="bg-green-600 hover:bg-green-700">
          🧪 Test Full Payment Flow
        </Button>
      </div>

      {/* Important Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-yellow-800 mb-2">⚠️ Important Testing Notes:</h3>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Use test card: <code>4000 0000 0000 0002</code></li>
          <li>• Any expiry date in future</li>
          <li>• CVV: <code>123</code></li>
          <li>• This will charge ₹{Math.round(testAmount * 83)} to your Razorpay balance</li>
          <li>• You can refund test payments in Razorpay dashboard</li>
        </ul>
      </div>

      {/* Results */}
      <pre className="p-4 bg-gray-100 rounded text-sm overflow-auto max-h-96">
        {result || 'Click a button to test...'}
      </pre>

      {/* Payment Modal */}
      {showPayment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="max-w-2xl w-full mx-4">
            <RazorpayCheckout
              amount={testAmount}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
              onCancel={() => setShowPayment(false)}
              customerEmail="test@unitasa.in"
              customerName="Test User"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PaymentTest;