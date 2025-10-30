import React, { useEffect, useState } from 'react';
import LandingPage from './pages/LandingPage';
import PerformanceDashboard from './components/dev/PerformanceDashboard';
import { initializeSecurity } from './utils/security';
import './App.css';
import './styles/ai-animations.css';
import { 
  measureWebVitals, 
  monitorBundlePerformance, 
  monitorMemoryUsage, 
  monitorNetworkPerformance 
} from './utils/performanceMonitoring';
import { 
  optimizeMobileViewport, 
  applyMobileOptimizations, 
  inlineCriticalCSS, 
  preconnectExternalDomains 
} from './utils/responsiveUtils';
import { preloadCriticalImages } from './utils/imageOptimization';
import { 
  preloadCriticalChunks, 
  implementResourceHints, 
  monitorBundleLoading, 
  validateTreeShaking,
  optimizeCriticalResourceLoading
} from './utils/bundleOptimization';
import { register as registerSW } from './utils/serviceWorker';
import { runTask11_2Validation } from './utils/performanceValidator';

function App() {
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);

  useEffect(() => {
    // Initialize security measures
    initializeSecurity();
    
    // Initialize performance monitoring
    measureWebVitals().then(metrics => {
      console.log('Web Vitals:', metrics);
      
      // Send metrics to analytics if needed
      if (metrics.lcp && metrics.lcp > 2500) {
        console.warn('LCP is above 2.5s threshold:', metrics.lcp);
      }
      
      if (metrics.fid && metrics.fid > 100) {
        console.warn('FID is above 100ms threshold:', metrics.fid);
      }
      
      if (metrics.cls && metrics.cls > 0.1) {
        console.warn('CLS is above 0.1 threshold:', metrics.cls);
      }
    });

    // Initialize monitoring
    monitorBundlePerformance();
    monitorMemoryUsage();
    monitorNetworkPerformance();

    // Apply mobile optimizations
    optimizeMobileViewport();
    applyMobileOptimizations();
    inlineCriticalCSS();
    preconnectExternalDomains();
    preloadCriticalImages();

    // Apply bundle optimizations
    preloadCriticalChunks();
    implementResourceHints();
    monitorBundleLoading();
    validateTreeShaking();
    optimizeCriticalResourceLoading();

    // Register service worker for PWA features
    registerSW({
      onSuccess: (registration) => {
        console.log('SW registered successfully');
      },
      onUpdate: (registration) => {
        console.log('SW updated');
      },
      onOfflineReady: () => {
        console.log('App ready for offline use');
      },
      onNeedRefresh: () => {
        console.log('New content available');
      }
    });

    // Run performance validation in development
    if (process.env.NODE_ENV === 'development') {
      setTimeout(() => {
        runTask11_2Validation().catch(console.error);
      }, 3000); // Wait 3 seconds for page to fully load

      // Add keyboard shortcut to open performance dashboard (Ctrl+Shift+P)
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.ctrlKey && event.shiftKey && event.key === 'P') {
          event.preventDefault();
          setShowPerformanceDashboard(true);
        }
      };

      window.addEventListener('keydown', handleKeyDown);
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
      };
    }

    // Cleanup function
    return () => {
      // Clean up any intervals or listeners if needed
    };
  }, []);

  return (
    <div className="App">
      <LandingPage />
      {process.env.NODE_ENV === 'development' && (
        <PerformanceDashboard
          isVisible={showPerformanceDashboard}
          onClose={() => setShowPerformanceDashboard(false)}
        />
      )}
    </div>
  );
}

export default App;
