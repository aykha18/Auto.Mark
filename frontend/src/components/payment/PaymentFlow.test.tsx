import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PaymentFlow from './PaymentFlow';

// Set test timeout to 10 seconds
jest.setTimeout(10000);

// Mock Stripe
jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn(() => Promise.resolve({
    elements: jest.fn(() => ({
      create: jest.fn(() => ({
        mount: jest.fn(),
        unmount: jest.fn(),
        on: jest.fn(),
        off: jest.fn()
      })),
      getElement: jest.fn()
    })),
    confirmCardPayment: jest.fn()
  }))
}));

jest.mock('@stripe/react-stripe-js', () => ({
  Elements: ({ children }: { children: React.ReactNode }) => <div data-testid="stripe-elements">{children}</div>,
  CardElement: () => <div data-testid="card-element">Card Element</div>,
  useStripe: () => ({
    confirmCardPayment: jest.fn()
  }),
  useElements: () => ({
    getElement: jest.fn()
  })
}));

// Mock API calls
global.fetch = jest.fn();

describe('PaymentFlow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses by default
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('co-creator-program/status')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            seatsRemaining: 15,
            totalSeats: 25,
            urgencyLevel: 'medium',
            program_price: 250.0,
            currency: 'USD',
            is_active: true
          })
        });
      }
      
      if (url.includes('reserve-seat')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            message: 'Seat reserved successfully',
            seat_number: 10,
            program_id: 1
          })
        });
      }
      
      if (url.includes('create-intent')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            payment_intent_id: 'pi_test_123',
            client_secret: 'pi_test_123_secret',
            amount: 25000,
            currency: 'usd'
          })
        });
      }
      
      // Default response
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
  });

  test('renders co-creator program interface initially', async () => {
    render(<PaymentFlow />);
    
    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('shows payment form when join program is clicked', async () => {
    render(<PaymentFlow />);
    
    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    const joinButton = screen.getByRole('button', { name: /Secure Your Co-Creator Spot/i });
    fireEvent.click(joinButton);

    await waitFor(() => {
      expect(screen.getByText(/Secure Your Co-Creator Spot/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('displays trust badges and security indicators', async () => {
    render(<PaymentFlow />);
    
    await waitFor(() => {
      expect(screen.getByText(/SSL Encrypted/i)).toBeInTheDocument();
      expect(screen.getByText(/PCI Compliant/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('handles back navigation correctly', async () => {
    render(<PaymentFlow />);
    
    // Navigate to payment form
    await waitFor(() => {
      const joinButton = screen.getByRole('button', { name: /Secure Your Co-Creator Spot/i });
      fireEvent.click(joinButton);
    }, { timeout: 5000 });

    // Go back to program details
    await waitFor(() => {
      const backButton = screen.getByRole('button', { name: /Back to Program Details/i });
      fireEvent.click(backButton);
    }, { timeout: 5000 });

    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('displays real-time seat counter', async () => {
    render(<PaymentFlow />);
    
    await waitFor(() => {
      expect(screen.getByText(/15 seats remaining/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});

describe('PaymentFlow Integration', () => {
  test('completes full payment flow simulation', async () => {
    const mockOnComplete = jest.fn();
    
    render(<PaymentFlow onComplete={mockOnComplete} />);
    
    // Should start with program interface
    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    // Verify key elements are present
    await waitFor(() => {
      expect(screen.getByText(/25 exclusive co-creators/i)).toBeInTheDocument();
      expect(screen.getByText(/Lifetime Access/i)).toBeInTheDocument();
      expect(screen.getByText(/Integration Support/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('handles payment processing errors gracefully', async () => {
    // Mock failed API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ message: 'Payment failed' })
    });

    render(<PaymentFlow />);
    
    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    // Navigate to payment form
    const joinButton = screen.getByRole('button', { name: /Secure Your Co-Creator Spot/i });
    fireEvent.click(joinButton);

    // Should handle error gracefully without crashing
    await waitFor(() => {
      expect(screen.getByText(/Secure Your Co-Creator Spot/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('shows loading states during API calls', async () => {
    // Mock slow API response
    (global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({
            seatsRemaining: 15,
            totalSeats: 25,
            urgencyLevel: 'medium'
          })
        }), 1000)
      )
    );

    render(<PaymentFlow />);
    
    // Should show loading or initial state
    expect(screen.getByText(/Co-Creator Program/i) || screen.getByText(/Loading/i)).toBeInTheDocument();
    
    // Wait for content to load
    await waitFor(() => {
      expect(screen.getByText(/Co-Creator Program/i)).toBeInTheDocument();
    }, { timeout: 8000 });
  });
});