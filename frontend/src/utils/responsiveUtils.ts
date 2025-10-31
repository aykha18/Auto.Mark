// Responsive design utilities for mobile optimization
import React from 'react';

export interface BreakpointConfig {
  sm: number;
  md: number;
  lg: number;
  xl: number;
}

export const breakpoints: BreakpointConfig = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280
};

// Hook for responsive behavior
export function useResponsive() {
  const [windowSize, setWindowSize] = React.useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  React.useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    ...windowSize,
    isMobile: windowSize.width < breakpoints.md,
    isTablet: windowSize.width >= breakpoints.md && windowSize.width < breakpoints.lg,
    isDesktop: windowSize.width >= breakpoints.lg,
    isSmallScreen: windowSize.width < breakpoints.sm,
  };
}

// Detect touch device
export function isTouchDevice(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// Optimize for mobile viewport
export function optimizeMobileViewport(): void {
  // Prevent zoom on input focus (iOS)
  const viewport = document.querySelector('meta[name="viewport"]');
  if (viewport) {
    viewport.setAttribute('content', 
      'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
    );
  }

  // Add touch-action CSS for better touch performance
  document.body.style.touchAction = 'manipulation';
}

// Intersection Observer for lazy loading
export function createIntersectionObserver(
  callback: IntersectionObserverCallback,
  options?: IntersectionObserverInit
): IntersectionObserver {
  const defaultOptions: IntersectionObserverInit = {
    root: null,
    rootMargin: '50px',
    threshold: 0.1,
    ...options
  };

  return new IntersectionObserver(callback, defaultOptions);
}

// Debounce utility for scroll/resize events
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Throttle utility for high-frequency events
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Mobile-specific optimizations
export function applyMobileOptimizations(): void {
  // Reduce animations on mobile for better performance
  if (isTouchDevice()) {
    document.body.classList.add('touch-device');
  }

  // Optimize scroll performance
  let ticking = false;
  
  function updateScrollPosition() {
    // Update scroll-dependent elements
    ticking = false;
  }

  function requestScrollUpdate() {
    if (!ticking) {
      requestAnimationFrame(updateScrollPosition);
      ticking = true;
    }
  }

  window.addEventListener('scroll', requestScrollUpdate, { passive: true });
}

// Critical CSS inlining for above-the-fold content
export function inlineCriticalCSS(): void {
  const criticalCSS = `
    .hero-section {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .loading-spinner {
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    @media (max-width: 768px) {
      .hero-section {
        min-height: 80vh;
        padding: 2rem 1rem;
      }
    }
  `;

  const style = document.createElement('style');
  style.textContent = criticalCSS;
  document.head.appendChild(style);
}

// Preconnect to external domains
export function preconnectExternalDomains(): void {
  const domains = [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://api.stripe.com',
    'https://js.stripe.com'
  ];

  domains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = domain;
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
}
