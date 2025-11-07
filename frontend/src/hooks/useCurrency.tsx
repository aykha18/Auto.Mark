import { useState, useEffect } from 'react';

interface CurrencyDisplay {
  currency: 'USD' | 'INR';
  symbol: string;
  amount: number;
  displayText: string;
  isIndian: boolean;
}

export const useCurrency = (baseAmountUSD: number = 497): CurrencyDisplay => {
  const [currencyDisplay, setCurrencyDisplay] = useState<CurrencyDisplay>({
    currency: 'USD',
    symbol: '$',
    amount: baseAmountUSD,
    displayText: `$${baseAmountUSD}`,
    isIndian: false
  });

  useEffect(() => {
    const detectCurrency = () => {
      try {
        // Detect from timezone
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const isIndian = timezone.includes('Asia/Kolkata') || 
                        timezone.includes('Asia/Calcutta') ||
                        timezone.includes('Asia/Kolkata');
        
        if (isIndian) {
          // Indian user - show INR
          const inrAmount = Math.round(baseAmountUSD * 83); // 1 USD = 83 INR
          setCurrencyDisplay({
            currency: 'INR',
            symbol: '₹',
            amount: inrAmount,
            displayText: `₹${inrAmount.toLocaleString('en-IN')}`,
            isIndian: true
          });
        } else {
          // International user - show USD
          setCurrencyDisplay({
            currency: 'USD',
            symbol: '$',
            amount: baseAmountUSD,
            displayText: `$${baseAmountUSD}`,
            isIndian: false
          });
        }
      } catch (error) {
        // Default to USD if detection fails
        console.log('Currency detection failed, defaulting to USD');
      }
    };

    detectCurrency();
  }, [baseAmountUSD]);

  return currencyDisplay;
};

export default useCurrency;
