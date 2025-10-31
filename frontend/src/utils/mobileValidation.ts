// Mobile responsiveness validation utilities

export interface ResponsiveTestResult {
  viewport: string;
  width: number;
  height: number;
  passed: boolean;
  issues: string[];
  loadTime: number;
  interactionReady: number;
}

export interface MobileOptimizationReport {
  overallScore: number;
  viewportTests: ResponsiveTestResult[];
  performanceMetrics: {
    bundleSize: number;
    loadTime: number;
    fcp: number;
    lcp: number;
    cls: number;
  };
  accessibilityScore: number;
  recommendations: string[];
}

// Standard mobile viewport sizes for testing
export const MOBILE_VIEWPORTS = [
  { name: 'iPhone SE', width: 375, height: 667 },
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPhone 12 Pro Max', width: 428, height: 926 },
  { name: 'Samsung Galaxy S21', width: 360, height: 800 },
  { name: 'iPad Mini', width: 768, height: 1024 },
  { name: 'iPad Pro', width: 1024, height: 1366 },
  { name: 'Small Mobile', width: 320, height: 568 },
  { name: 'Large Mobile', width: 414, height: 896 }
];

// Test responsive design across different viewports
export async function testResponsiveDesign(): Promise<ResponsiveTestResult[]> {
  const results: ResponsiveTestResult[] = [];

  for (const viewport of MOBILE_VIEWPORTS) {
    const startTime = performance.now();
    
    // Simulate viewport change
    const originalWidth = window.innerWidth;
    const originalHeight = window.innerHeight;
    
    // Mock viewport change (in real testing, this would be done with browser automation)
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: viewport.width,
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: viewport.height,
    });

    // Trigger resize event
    window.dispatchEvent(new Event('resize'));

    const issues: string[] = [];
    
    // Test 1: Check for horizontal scrolling
    if (document.body.scrollWidth > viewport.width) {
      issues.push('Horizontal scrolling detected');
    }

    // Test 2: Check for touch-friendly button sizes
    const buttons = document.querySelectorAll('button, a[role="button"], [onclick]');
    buttons.forEach((button, index) => {
      const rect = button.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        issues.push(`Button ${index + 1} too small for touch (${rect.width}x${rect.height}px)`);
      }
    });

    // Test 3: Check for readable font sizes
    const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
    textElements.forEach((element, index) => {
      const styles = window.getComputedStyle(element);
      const fontSize = parseInt(styles.fontSize);
      if (fontSize < 16) {
        issues.push(`Text element ${index + 1} font size too small (${fontSize}px)`);
      }
    });

    // Test 4: Check for proper spacing
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
    interactiveElements.forEach((element, index) => {
      const rect = element.getBoundingClientRect();
      const nextElement = interactiveElements[index + 1] as HTMLElement;
      if (nextElement) {
        const nextRect = nextElement.getBoundingClientRect();
        const distance = Math.abs(rect.bottom - nextRect.top);
        if (distance < 8) {
          issues.push(`Interactive elements ${index + 1} and ${index + 2} too close (${distance}px apart)`);
        }
      }
    });

    // Test 5: Check for viewport meta tag
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (!viewportMeta) {
      issues.push('Missing viewport meta tag');
    } else {
      const content = viewportMeta.getAttribute('content') || '';
      if (!content.includes('width=device-width')) {
        issues.push('Viewport meta tag missing width=device-width');
      }
    }

    const endTime = performance.now();
    const loadTime = endTime - startTime;

    // Simulate interaction readiness test
    const interactionReady = loadTime + Math.random() * 100;

    results.push({
      viewport: viewport.name,
      width: viewport.width,
      height: viewport.height,
      passed: issues.length === 0,
      issues,
      loadTime,
      interactionReady
    });

    // Restore original dimensions
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalWidth,
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: originalHeight,
    });
  }

  return results;
}

// Generate mobile optimization report
export async function generateMobileOptimizationReport(): Promise<MobileOptimizationReport> {
  const viewportTests = await testResponsiveDesign();
  
  // Calculate performance metrics
  const performanceMetrics = {
    bundleSize: await getBundleSize(),
    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
    fcp: await getFCP(),
    lcp: await getLCP(),
    cls: await getCLS()
  };

  // Calculate accessibility score
  const accessibilityScore = await calculateAccessibilityScore();

  // Generate recommendations
  const recommendations = generateRecommendations(viewportTests, performanceMetrics, accessibilityScore);

  // Calculate overall score
  const passedTests = viewportTests.filter(test => test.passed).length;
  const responsiveScore = (passedTests / viewportTests.length) * 100;
  const performanceScore = calculatePerformanceScore(performanceMetrics);
  const overallScore = Math.round((responsiveScore + performanceScore + accessibilityScore) / 3);

  return {
    overallScore,
    viewportTests,
    performanceMetrics,
    accessibilityScore,
    recommendations
  };
}

// Helper functions
async function getBundleSize(): Promise<number> {
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
  const jsResources = resources.filter(resource => 
    resource.name.includes('.js') && resource.name.includes('static')
  );
  return jsResources.reduce((total, resource) => total + (resource.transferSize || 0), 0);
}

async function getFCP(): Promise<number> {
  return new Promise((resolve) => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fcp = entries.find(entry => entry.name === 'first-contentful-paint');
      resolve(fcp ? fcp.startTime : 0);
      observer.disconnect();
    });
    observer.observe({ entryTypes: ['paint'] });
  });
}

async function getLCP(): Promise<number> {
  return new Promise((resolve) => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lcp = entries[entries.length - 1];
      resolve(lcp ? lcp.startTime : 0);
    });
    observer.observe({ entryTypes: ['largest-contentful-paint'] });
    
    // Fallback timeout
    setTimeout(() => resolve(0), 5000);
  });
}

async function getCLS(): Promise<number> {
  return new Promise((resolve) => {
    let clsValue = 0;
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
    });
    observer.observe({ entryTypes: ['layout-shift'] });
    
    setTimeout(() => {
      resolve(clsValue);
      observer.disconnect();
    }, 5000);
  });
}

async function calculateAccessibilityScore(): Promise<number> {
  let score = 100;
  
  // Check for alt text on images
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    if (!img.alt) score -= 5;
  });

  // Check for proper heading hierarchy
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  let lastLevel = 0;
  headings.forEach(heading => {
    const level = parseInt(heading.tagName.charAt(1));
    if (level > lastLevel + 1) score -= 3;
    lastLevel = level;
  });

  // Check for form labels
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    const id = input.getAttribute('id');
    if (id && !document.querySelector(`label[for="${id}"]`)) {
      score -= 5;
    }
  });

  // Check for focus indicators
  const focusableElements = document.querySelectorAll('button, a, input, select, textarea, [tabindex]');
  focusableElements.forEach(element => {
    const styles = window.getComputedStyle(element, ':focus');
    if (!styles.outline || styles.outline === 'none') {
      score -= 2;
    }
  });

  return Math.max(0, score);
}

function calculatePerformanceScore(metrics: any): number {
  let score = 100;
  
  // Bundle size penalty
  if (metrics.bundleSize > 150000) score -= 20;
  else if (metrics.bundleSize > 100000) score -= 10;
  
  // Load time penalty
  if (metrics.loadTime > 3000) score -= 20;
  else if (metrics.loadTime > 2000) score -= 10;
  
  // FCP penalty
  if (metrics.fcp > 1800) score -= 15;
  else if (metrics.fcp > 1200) score -= 8;
  
  // LCP penalty
  if (metrics.lcp > 2500) score -= 15;
  else if (metrics.lcp > 1800) score -= 8;
  
  // CLS penalty
  if (metrics.cls > 0.1) score -= 10;
  else if (metrics.cls > 0.05) score -= 5;
  
  return Math.max(0, score);
}

function generateRecommendations(
  viewportTests: ResponsiveTestResult[], 
  performanceMetrics: any, 
  accessibilityScore: number
): string[] {
  const recommendations: string[] = [];
  
  // Responsive design recommendations
  const failedTests = viewportTests.filter(test => !test.passed);
  if (failedTests.length > 0) {
    recommendations.push('Fix responsive design issues on mobile viewports');
    
    const commonIssues = failedTests.flatMap(test => test.issues);
    const issueCount = commonIssues.reduce((acc, issue) => {
      acc[issue] = (acc[issue] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    Object.entries(issueCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .forEach(([issue]) => {
        recommendations.push(`Address: ${issue}`);
      });
  }
  
  // Performance recommendations
  if (performanceMetrics.bundleSize > 150000) {
    recommendations.push('Reduce bundle size through code splitting and tree shaking');
  }
  
  if (performanceMetrics.loadTime > 3000) {
    recommendations.push('Optimize loading performance - target <3s load time');
  }
  
  if (performanceMetrics.lcp > 2500) {
    recommendations.push('Improve Largest Contentful Paint - optimize images and critical resources');
  }
  
  if (performanceMetrics.cls > 0.1) {
    recommendations.push('Reduce Cumulative Layout Shift - reserve space for dynamic content');
  }
  
  // Accessibility recommendations
  if (accessibilityScore < 90) {
    recommendations.push('Improve accessibility - add alt text, proper labels, and focus indicators');
  }
  
  return recommendations;
}
