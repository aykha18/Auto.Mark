// Performance monitoring utilities

export interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

// Measure Core Web Vitals
export function measureWebVitals(): Promise<Partial<PerformanceMetrics>> {
  return new Promise((resolve) => {
    const metrics: Partial<PerformanceMetrics> = {};

    // First Contentful Paint
    const fcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fcp = entries[entries.length - 1];
      metrics.fcp = fcp.startTime;
      fcpObserver.disconnect();
    });
    fcpObserver.observe({ entryTypes: ['paint'] });

    // Largest Contentful Paint
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lcp = entries[entries.length - 1] as any; // Type assertion for LCP entry
      metrics.lcp = lcp.startTime;
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

    // First Input Delay
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fid = entries[0] as any; // Type assertion for FID entry
      metrics.fid = fid.processingStart - fid.startTime;
      fidObserver.disconnect();
    });
    fidObserver.observe({ entryTypes: ['first-input'] });

    // Cumulative Layout Shift
    let clsValue = 0;
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      metrics.cls = clsValue;
    });
    clsObserver.observe({ entryTypes: ['layout-shift'] });

    // Time to First Byte
    const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationEntry) {
      metrics.ttfb = navigationEntry.responseStart - navigationEntry.requestStart;
    }

    // Resolve after 5 seconds or when all metrics are collected
    setTimeout(() => {
      resolve(metrics);
    }, 5000);
  });
}

// Monitor bundle size and loading performance
export function monitorBundlePerformance(): void {
  if ('performance' in window) {
    window.addEventListener('load', () => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      
      const jsResources = resources.filter(resource => 
        resource.name.includes('.js') && resource.name.includes('static')
      );
      
      const cssResources = resources.filter(resource => 
        resource.name.includes('.css') && resource.name.includes('static')
      );

      const totalJSSize = jsResources.reduce((total, resource) => 
        total + (resource.transferSize || 0), 0
      );
      
      const totalCSSSize = cssResources.reduce((total, resource) => 
        total + (resource.transferSize || 0), 0
      );

      console.log('Bundle Performance:', {
        jsSize: `${(totalJSSize / 1024).toFixed(2)} KB`,
        cssSize: `${(totalCSSSize / 1024).toFixed(2)} KB`,
        totalResources: resources.length,
        loadTime: `${performance.timing.loadEventEnd - performance.timing.navigationStart}ms`
      });
    });
  }
}

// Track component render performance
export function trackComponentPerformance(componentName: string) {
  const startTime = performance.now();
  
  return () => {
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    if (renderTime > 16) { // Longer than one frame (60fps)
      console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms`);
    }
  };
}

// Memory usage monitoring
export function monitorMemoryUsage(): void {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    
    setInterval(() => {
      const memoryInfo = {
        used: `${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
        total: `${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
        limit: `${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`
      };
      
      // Log warning if memory usage is high
      if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.8) {
        console.warn('High memory usage detected:', memoryInfo);
      }
    }, 30000); // Check every 30 seconds
  }
}

// Network performance monitoring
export function monitorNetworkPerformance(): void {
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;
    
    console.log('Network Info:', {
      effectiveType: connection.effectiveType,
      downlink: `${connection.downlink} Mbps`,
      rtt: `${connection.rtt}ms`,
      saveData: connection.saveData
    });

    // Adjust loading strategy based on connection
    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      document.body.classList.add('slow-connection');
    }
  }
}