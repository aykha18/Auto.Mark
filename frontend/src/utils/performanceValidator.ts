// Performance validation for task 11.2 completion

import { generateMobileOptimizationReport, MobileOptimizationReport } from './mobileValidation';
import { measureWebVitals, PerformanceMetrics } from './performanceMonitoring';
import { testCRMIntegrationPerformance, mockCRMIntegrationTest, CRMPerformanceReport } from './crmPerformanceTest';

export interface Task11_2ValidationResult {
  bundleOptimization: {
    passed: boolean;
    currentSize: number;
    targetSize: number;
    codeSplittingImplemented: boolean;
    lazyLoadingImplemented: boolean;
  };
  mobileOptimization: {
    passed: boolean;
    loadTimeUnder3s: boolean;
    responsiveDesignScore: number;
    touchFriendly: boolean;
  };
  pwaFeatures: {
    passed: boolean;
    serviceWorkerRegistered: boolean;
    manifestPresent: boolean;
    offlineCapable: boolean;
  };
  crmIntegrationPerformance: {
    passed: boolean;
    apiResponseTime: number;
    errorHandling: boolean;
    report: CRMPerformanceReport;
  };
  overallScore: number;
  recommendations: string[];
}

export async function validateTask11_2Implementation(): Promise<Task11_2ValidationResult> {
  console.log('🔍 Validating Task 11.2: Performance and mobile optimization...');

  // Test 1: Bundle Optimization
  const bundleOptimization = await testBundleOptimization();
  
  // Test 2: Mobile Optimization
  const mobileOptimization = await testMobileOptimization();
  
  // Test 3: PWA Features
  const pwaFeatures = await testPWAFeatures();
  
  // Test 4: CRM Integration Performance
  const crmIntegrationPerformance = await testCRMIntegrationPerformanceValidation();

  // Calculate overall score
  const scores = [
    bundleOptimization.passed ? 25 : 0,
    mobileOptimization.passed ? 25 : 0,
    pwaFeatures.passed ? 25 : 0,
    crmIntegrationPerformance.passed ? 25 : 0
  ];
  const overallScore = scores.reduce((sum, score) => sum + score, 0);

  // Generate recommendations
  const recommendations = generateTaskRecommendations({
    bundleOptimization,
    mobileOptimization,
    pwaFeatures,
    crmIntegrationPerformance
  });

  return {
    bundleOptimization,
    mobileOptimization,
    pwaFeatures,
    crmIntegrationPerformance,
    overallScore,
    recommendations
  };
}

async function testBundleOptimization() {
  console.log('📦 Testing bundle optimization...');
  
  // Check current bundle size
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
  const jsResources = resources.filter(resource => 
    resource.name.includes('.js') && resource.name.includes('static')
  );
  const currentSize = jsResources.reduce((total, resource) => total + (resource.transferSize || 0), 0);
  const targetSize = 150000; // 150KB target

  // Check for code splitting (multiple JS chunks)
  const codeSplittingImplemented = jsResources.length > 1;

  // Check for lazy loading implementation
  const lazyLoadingImplemented = document.querySelectorAll('[loading="lazy"]').length > 0 ||
    document.querySelector('script')?.textContent?.includes('lazy') || false;

  const passed = currentSize <= targetSize && codeSplittingImplemented;

  return {
    passed,
    currentSize,
    targetSize,
    codeSplittingImplemented,
    lazyLoadingImplemented
  };
}

async function testMobileOptimization() {
  console.log('📱 Testing mobile optimization...');
  
  // Test load time
  const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
  const loadTimeUnder3s = loadTime <= 3000;

  // Test responsive design
  const mobileReport = await generateMobileOptimizationReport();
  const responsiveDesignScore = mobileReport.overallScore;

  // Test touch-friendly elements
  const buttons = document.querySelectorAll('button, a[role="button"], [onclick]');
  let touchFriendlyCount = 0;
  buttons.forEach(button => {
    const rect = button.getBoundingClientRect();
    if (rect.width >= 44 && rect.height >= 44) {
      touchFriendlyCount++;
    }
  });
  const touchFriendly = buttons.length === 0 || (touchFriendlyCount / buttons.length) >= 0.8;

  const passed = loadTimeUnder3s && responsiveDesignScore >= 80 && touchFriendly;

  return {
    passed,
    loadTimeUnder3s,
    responsiveDesignScore,
    touchFriendly
  };
}

async function testPWAFeatures() {
  console.log('🔧 Testing PWA features...');
  
  // Test service worker registration
  const serviceWorkerRegistered = 'serviceWorker' in navigator && 
    (await navigator.serviceWorker.getRegistrations()).length > 0;

  // Test manifest presence
  const manifestPresent = !!document.querySelector('link[rel="manifest"]') ||
    !!document.querySelector('link[rel="manifest"][href*="manifest"]');

  // Test offline capability (basic check)
  const offlineCapable = serviceWorkerRegistered && 
    (await caches.keys()).length > 0;

  const passed = serviceWorkerRegistered && manifestPresent;

  return {
    passed,
    serviceWorkerRegistered,
    manifestPresent,
    offlineCapable
  };
}

async function testCRMIntegrationPerformanceValidation() {
  console.log('🔗 Testing CRM integration performance...');
  
  try {
    // Use mock test in development, real test in production
    const report = process.env.NODE_ENV === 'development' 
      ? await mockCRMIntegrationTest()
      : await testCRMIntegrationPerformance();
    
    const passed = report.overallScore >= 75 && 
                   report.averageResponseTime <= 2000 && 
                   report.errorHandlingScore >= 80;

    return {
      passed,
      apiResponseTime: report.averageResponseTime,
      errorHandling: report.errorHandlingScore >= 80,
      report
    };
  } catch (error) {
    console.error('CRM performance test failed:', error);
    
    // Fallback to basic test
    const mockReport: CRMPerformanceReport = {
      overallScore: 50,
      averageResponseTime: 3000,
      successRate: 70,
      errorHandlingScore: 60,
      cacheEfficiency: 30,
      results: [],
      recommendations: ['CRM performance test failed - implement proper error handling']
    };

    return {
      passed: false,
      apiResponseTime: 3000,
      errorHandling: false,
      report: mockReport
    };
  }
}

function generateTaskRecommendations(results: any): string[] {
  const recommendations: string[] = [];

  if (!results.bundleOptimization.passed) {
    if (results.bundleOptimization.currentSize > results.bundleOptimization.targetSize) {
      recommendations.push(`Reduce bundle size from ${(results.bundleOptimization.currentSize / 1024).toFixed(2)}KB to under ${(results.bundleOptimization.targetSize / 1024).toFixed(2)}KB`);
    }
    if (!results.bundleOptimization.codeSplittingImplemented) {
      recommendations.push('Implement code splitting to create multiple chunks');
    }
    if (!results.bundleOptimization.lazyLoadingImplemented) {
      recommendations.push('Add lazy loading for images and components');
    }
  }

  if (!results.mobileOptimization.passed) {
    if (!results.mobileOptimization.loadTimeUnder3s) {
      recommendations.push('Optimize page load time to under 3 seconds on mobile');
    }
    if (results.mobileOptimization.responsiveDesignScore < 80) {
      recommendations.push('Improve responsive design score to 80+');
    }
    if (!results.mobileOptimization.touchFriendly) {
      recommendations.push('Make buttons and interactive elements touch-friendly (44x44px minimum)');
    }
  }

  if (!results.pwaFeatures.passed) {
    if (!results.pwaFeatures.serviceWorkerRegistered) {
      recommendations.push('Register service worker for PWA functionality');
    }
    if (!results.pwaFeatures.manifestPresent) {
      recommendations.push('Add web app manifest for PWA installation');
    }
  }

  if (!results.crmIntegrationPerformance.passed) {
    if (results.crmIntegrationPerformance.apiResponseTime > 2000) {
      recommendations.push('Optimize CRM API response time to under 2 seconds');
    }
    if (!results.crmIntegrationPerformance.errorHandling) {
      recommendations.push('Implement proper error handling for CRM integrations');
    }
    
    // Add specific CRM recommendations
    if (results.crmIntegrationPerformance.report.recommendations.length > 0) {
      recommendations.push(...results.crmIntegrationPerformance.report.recommendations.slice(0, 3));
    }
  }

  return recommendations;
}

// Export validation function for testing
export async function runTask11_2Validation(): Promise<Task11_2ValidationResult> {
  try {
    const results = await validateTask11_2Implementation();
    
    console.log('\n=== Task 11.2 Validation Results ===');
    console.log(`Overall Score: ${results.overallScore}/100`);
    console.log(`Bundle Optimization: ${results.bundleOptimization.passed ? '✅' : '❌'}`);
    console.log(`Mobile Optimization: ${results.mobileOptimization.passed ? '✅' : '❌'}`);
    console.log(`PWA Features: ${results.pwaFeatures.passed ? '✅' : '❌'}`);
    console.log(`CRM Integration Performance: ${results.crmIntegrationPerformance.passed ? '✅' : '❌'}`);
    
    if (results.recommendations.length > 0) {
      console.log('\n📋 Recommendations:');
      results.recommendations.forEach((rec, index) => {
        console.log(`${index + 1}. ${rec}`);
      });
    }

    if (results.overallScore >= 75) {
      console.log('\n🎉 Task 11.2 implementation meets performance requirements!');
    } else {
      console.log('\n⚠️ Task 11.2 implementation needs improvement.');
    }

    return results;
  } catch (error) {
    console.error('❌ Validation failed:', error);
    throw error;
  }
}
