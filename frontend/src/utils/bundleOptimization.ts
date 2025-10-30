// Bundle optimization utilities for Task 11.2

export interface BundleAnalysis {
  totalSize: number;
  jsSize: number;
  cssSize: number;
  imageSize: number;
  chunkCount: number;
  duplicateModules: string[];
  unusedCode: string[];
  recommendations: string[];
}

// Analyze current bundle performance
export function analyzeBundlePerformance(): BundleAnalysis {
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
  
  const jsResources = resources.filter(resource => 
    resource.name.includes('.js') && resource.name.includes('static')
  );
  
  const cssResources = resources.filter(resource => 
    resource.name.includes('.css') && resource.name.includes('static')
  );
  
  const imageResources = resources.filter(resource => 
    /\.(jpg|jpeg|png|gif|webp|svg)/.test(resource.name)
  );

  const jsSize = jsResources.reduce((total, resource) => total + (resource.transferSize || 0), 0);
  const cssSize = cssResources.reduce((total, resource) => total + (resource.transferSize || 0), 0);
  const imageSize = imageResources.reduce((total, resource) => total + (resource.transferSize || 0), 0);
  const totalSize = jsSize + cssSize + imageSize;
  const chunkCount = jsResources.length;

  const recommendations: string[] = [];
  
  // Generate recommendations based on analysis
  if (jsSize > 150000) {
    recommendations.push('JavaScript bundle exceeds 150KB - implement more aggressive code splitting');
  }
  
  if (chunkCount < 3) {
    recommendations.push('Consider splitting into more chunks for better caching');
  }
  
  if (cssSize > 50000) {
    recommendations.push('CSS bundle is large - consider critical CSS extraction');
  }
  
  if (imageSize > 500000) {
    recommendations.push('Images are large - implement WebP conversion and compression');
  }

  return {
    totalSize,
    jsSize,
    cssSize,
    imageSize,
    chunkCount,
    duplicateModules: [], // Would need build-time analysis
    unusedCode: [], // Would need build-time analysis
    recommendations
  };
}

// Preload critical chunks
export function preloadCriticalChunks(): void {
  const criticalChunks = [
    'main', // Main application chunk
    'vendor', // Third-party libraries
    'runtime' // Webpack runtime
  ];

  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
  const jsResources = resources.filter(resource => 
    resource.name.includes('.js') && resource.name.includes('static')
  );

  jsResources.forEach(resource => {
    const chunkName = extractChunkName(resource.name);
    if (criticalChunks.some(critical => chunkName.includes(critical))) {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'script';
      link.href = resource.name;
      document.head.appendChild(link);
    }
  });
}

// Extract chunk name from resource URL
function extractChunkName(url: string): string {
  const match = url.match(/static\/js\/(.+?)\..*\.js$/);
  return match ? match[1] : '';
}

// Implement resource hints for better loading
export function implementResourceHints(): void {
  // DNS prefetch for external domains
  const externalDomains = [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://api.stripe.com',
    'https://js.stripe.com',
    'https://www.google-analytics.com'
  ];

  externalDomains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'dns-prefetch';
    link.href = domain;
    document.head.appendChild(link);
  });

  // Preconnect to critical external resources
  const criticalDomains = [
    'https://fonts.googleapis.com',
    'https://api.stripe.com'
  ];

  criticalDomains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = domain;
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
}

// Monitor bundle loading performance
export function monitorBundleLoading(): void {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach(entry => {
        if (entry.name.includes('static/js/') && entry.name.includes('.js')) {
          const resourceEntry = entry as PerformanceResourceTiming;
          const loadTime = resourceEntry.responseEnd - resourceEntry.requestStart;
          const size = resourceEntry.transferSize || 0;
          
          console.log(`Chunk loaded: ${extractChunkName(entry.name)}`);
          console.log(`  Load time: ${loadTime.toFixed(2)}ms`);
          console.log(`  Size: ${(size / 1024).toFixed(2)}KB`);
          
          // Warn about slow-loading chunks
          if (loadTime > 1000) {
            console.warn(`Slow chunk detected: ${entry.name} took ${loadTime.toFixed(2)}ms`);
          }
        }
      });
    });

    observer.observe({ entryTypes: ['resource'] });
  }
}

// Tree shaking validation (runtime check)
export function validateTreeShaking(): void {
  // Check for common unused imports that should be tree-shaken
  const potentialUnusedImports = [
    'lodash', // Should use lodash-es or specific imports
    'moment', // Should use date-fns or native Date
    'jquery' // Should not be needed in React
  ];

  const scripts = Array.from(document.querySelectorAll('script[src]'));
  const scriptContent = scripts.map(script => script.getAttribute('src') || '').join(' ');

  potentialUnusedImports.forEach(lib => {
    if (scriptContent.includes(lib)) {
      console.warn(`Potential tree-shaking issue: ${lib} detected in bundle`);
    }
  });
}

// Critical resource loading strategy
export function optimizeCriticalResourceLoading(): void {
  // Inline critical CSS for above-the-fold content
  const criticalCSS = `
    /* Critical styles for above-the-fold content */
    .hero-section {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .hero-title {
      font-size: 3rem;
      font-weight: 700;
      color: white;
      text-align: center;
      margin-bottom: 1rem;
    }
    
    .hero-subtitle {
      font-size: 1.25rem;
      color: rgba(255, 255, 255, 0.9);
      text-align: center;
      margin-bottom: 2rem;
    }
    
    .cta-button {
      background: #10b981;
      color: white;
      padding: 1rem 2rem;
      border-radius: 0.5rem;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    
    .cta-button:hover {
      background: #059669;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
      .hero-title {
        font-size: 2rem;
      }
      
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