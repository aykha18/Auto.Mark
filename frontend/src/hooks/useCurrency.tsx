import { useState, useEffect } from 'react';

interface CurrencyDisplay {
  currency: 'USD' | 'INR';
  symbol: string;
  amount: number;
  displayText: string;
  isIndian: boolean;
}

// TEMPORARY: Force INR for Razorpay KYC approval
// Set to false to re-enable currency detection after approval
const FORCE_INR_ONLY = true;

export const useCurrency = (baseAmountUSD: number = 497): CurrencyDisplay => {
  const [currencyDisplay, setCurrencyDisplay] = useState<CurrencyDisplay>({
    currency: 'INR',
    symbol: '₹',
    amount: Math.round(baseAmountUSD * 83),
    displayText: `₹${Math.round(baseAmountUSD * 83).toLocaleString('en-IN')}`,
    isIndian: true
  });

  useEffect(() => {
    const detectCurrency = () => {
      try {
        // TEMPORARY: Force INR for all users for Razorpay KYC approval
        if (FORCE_INR_ONLY) {
          const inrAmount = Math.round(baseAmountUSD * 83); // 1 USD = 83 INR
          setCurrencyDisplay({
            currency: 'INR',
            symbol: '₹',
            amount: inrAmount,
            displayText: `₹${inrAmount.toLocaleString('en-IN')}`,
            isIndian: true
          });
          return;
        }

        // Normal currency detection (will be re-enabled after KYC approval)
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
        // Default to INR during KYC approval period
        console.log('Currency detection failed, defaulting to INR for KYC approval');
        const inrAmount = Math.round(baseAmountUSD * 83);
        setCurrencyDisplay({
          currency: 'INR',
          symbol: '₹',
          amount: inrAmount,
          displayText: `₹${inrAmount.toLocaleString('en-IN')}`,
          isIndian: true
        });
      }
    };

    detectCurrency();
  }, [baseAmountUSD]);

  return currencyDisplay;
};

export default useCurrency;
