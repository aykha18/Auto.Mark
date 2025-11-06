import React, { useState, useEffect } from 'react';

interface CurrencyInfo {
  currency: string;
  amount: number;
  symbol: string;
  country: string;
  displayAmount: string;
}

interface CurrencyDetectorProps {
  baseAmountUSD: number;
  onCurrencyChange: (currencyInfo: CurrencyInfo) => void;
}

const CurrencyDetector: React.FC<CurrencyDetectorProps> = ({
  baseAmountUSD,
  onCurrencyChange
}) => {
  const [detectedCountry, setDetectedCountry] = useState<string>('US');
  const [selectedCurrency, setSelectedCurrency] = useState<string>('USD');
  const [currencyInfo, setCurrencyInfo] = useState<CurrencyInfo>({
    currency: 'USD',
    amount: baseAmountUSD,
    symbol: '$',
    country: 'US',
    displayAmount: `$${baseAmountUSD}`
  });

  // Exchange rates (in production, fetch from API)
  const exchangeRates = {
    USD: 1,
    INR: 83,
    EUR: 0.85,
    GBP: 0.73,
    CAD: 1.25,
    AUD: 1.45
  };

  // Currency symbols
  const currencySymbols = {
    USD: '$',
    INR: '₹',
    EUR: '€',
    GBP: '£',
    CAD: 'C$',
    AUD: 'A$'
  };

  // Detect user's country (simplified - in production use a geolocation service)
  useEffect(() => {
    const detectCountry = async () => {
      try {
        // Try to detect from timezone
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        
        if (timezone.includes('Asia/Kolkata') || timezone.includes('Asia/Calcutta')) {
          setDetectedCountry('IN');
          setSelectedCurrency('INR');
        } else if (timezone.includes('Europe/')) {
          setDetectedCountry('EU');
          setSelectedCurrency('EUR');
        } else if (timezone.includes('America/')) {
          setDetectedCountry('US');
          setSelectedCurrency('USD');
        } else {
          // Default to USD for unknown regions
          setDetectedCountry('US');
          setSelectedCurrency('USD');
        }
      } catch (error) {
        console.log('Could not detect timezone, defaulting to USD');
        setDetectedCountry('US');
        setSelectedCurrency('USD');
      }
    };

    detectCountry();
  }, []);

  // Update currency info when currency changes
  useEffect(() => {
    const rate = exchangeRates[selectedCurrency as keyof typeof exchangeRates] || 1;
    const amount = baseAmountUSD * rate;
    const symbol = currencySymbols[selectedCurrency as keyof typeof currencySymbols] || '$';
    
    const newCurrencyInfo: CurrencyInfo = {
      currency: selectedCurrency,
      amount: Math.round(amount * 100) / 100, // Round to 2 decimal places
      symbol,
      country: detectedCountry,
      displayAmount: `${symbol}${amount.toLocaleString()}`
    };

    setCurrencyInfo(newCurrencyInfo);
    onCurrencyChange(newCurrencyInfo);
  }, [selectedCurrency, baseAmountUSD, detectedCountry, onCurrencyChange]);

  const handleCurrencyChange = (currency: string) => {
    setSelectedCurrency(currency);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">Payment Currency</h3>
        <span className="text-xs text-gray-500">
          Detected: {detectedCountry === 'IN' ? '🇮🇳 India' : detectedCountry === 'EU' ? '🇪🇺 Europe' : '🌍 International'}
        </span>
      </div>

      <div className="space-y-3">
        {/* Currency Selection */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleCurrencyChange('INR')}
            className={`p-3 rounded-lg border text-left transition-colors ${
              selectedCurrency === 'INR'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium">🇮🇳 Indian Rupees</div>
            <div className="text-sm text-gray-600">
              ₹{(baseAmountUSD * exchangeRates.INR).toLocaleString()}
            </div>
          </button>

          <button
            onClick={() => handleCurrencyChange('USD')}
            className={`p-3 rounded-lg border text-left transition-colors ${
              selectedCurrency === 'USD'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium">🌍 US Dollars</div>
            <div className="text-sm text-gray-600">
              ${baseAmountUSD}
            </div>
          </button>
        </div>

        {/* Selected Amount Display */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {currencyInfo.displayAmount}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Co-Creator Program Access
            </div>
            {selectedCurrency !== 'USD' && (
              <div className="text-xs text-gray-500 mt-1">
                Equivalent to ${baseAmountUSD} USD
              </div>
            )}
          </div>
        </div>

        {/* Payment Methods Preview */}
        <div className="text-xs text-gray-600">
          <div className="font-medium mb-1">Available payment methods:</div>
          {selectedCurrency === 'INR' ? (
            <div>UPI, Cards, Net Banking, Wallets</div>
          ) : (
            <div>International Cards (Visa, Mastercard, Amex)</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CurrencyDetector;