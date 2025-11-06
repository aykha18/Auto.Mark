import React, { useState } from 'react';
import Button from '../ui/Button';
import { consultationService } from '../../services/consultationService';

const ConsultationTest: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const testConsultationBooking = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing consultation booking...');
      
      const testData = {
        name: 'Test User',
        email: 'test@example.com',
        company: 'Test Company',
        phone: '+1234567890',
        preferredTime: 'morning',
        timezone: 'UTC',
        challenges: 'Need help with AI marketing automation',
        currentCRM: 'hubspot',
        source: 'frontend_test',
        consultationType: 'ai_strategy_session'
      };

      console.log('📤 Sending booking request:', testData);
      
      const response = await consultationService.bookConsultation(testData);
      
      console.log('📥 Received response:', response);
      setResult(response);
      
    } catch (err) {
      console.error('❌ Consultation booking test failed:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-2xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Consultation Booking Test</h2>
      
      <div className="space-y-4">
        <Button
          onClick={testConsultationBooking}
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Testing...' : 'Test Consultation Booking'}
        </Button>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">Error:</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {result && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-800 mb-2">Success:</h3>
            <pre className="text-sm text-green-700 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}

        <div className="text-sm text-gray-600">
          <p><strong>Test Data:</strong></p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Name: Test User</li>
            <li>Email: test@example.com</li>
            <li>Company: Test Company</li>
            <li>Phone: +1234567890</li>
            <li>CRM: HubSpot</li>
            <li>Challenges: Need help with AI marketing automation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ConsultationTest;