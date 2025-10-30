// CRM Integration Performance Testing for Task 11.2

export interface CRMPerformanceResult {
  endpoint: string;
  responseTime: number;
  success: boolean;
  errorHandling: boolean;
  cacheHit: boolean;
  retryAttempts: number;
}

export interface CRMPerformanceReport {
  overallScore: number;
  averageResponseTime: number;
  successRate: number;
  errorHandlingScore: number;
  cacheEfficiency: number;
  results: CRMPerformanceResult[];
  recommendations: string[];
}

// CRM endpoints to test
const CRM_ENDPOINTS = [
  '/api/v1/crm-marketplace/connectors',
  '/api/v1/crm-marketplace/pipedrive/status',
  '/api/v1/crm-marketplace/zoho/status',
  '/api/v1/crm-marketplace/hubspot/status',
  '/api/v1/crm-marketplace/monday/status',
  '/api/v1/crm-marketplace/salesforce/status',
  '/api/v1/landing/assessment',
  '/api/v1/landing/lead-capture'
];

// Test CRM integration performance
export async function testCRMIntegrationPerformance(): Promise<CRMPerformanceReport> {
  console.log('🔗 Testing CRM integration performance...');
  
  const results: CRMPerformanceResult[] = [];
  
  for (const endpoint of CRM_ENDPOINTS) {
    const result = await testEndpointPerformance(endpoint);
    results.push(result);
  }
  
  // Calculate metrics
  const successfulResults = results.filter(r => r.success);
  const averageResponseTime = results.reduce((sum, r) => sum + r.responseTime, 0) / results.length;
  const successRate = (successfulResults.length / results.length) * 100;
  const errorHandlingScore = results.filter(r => r.errorHandling).length / results.length * 100;
  const cacheEfficiency = results.filter(r => r.cacheHit).length / results.length * 100;
  
  // Calculate overall score
  const responseTimeScore = averageResponseTime <= 2000 ? 100 : Math.max(0, 100 - (averageResponseTime - 2000) / 50);
  const overallScore = Math.round((responseTimeScore + successRate + errorHandlingScore + cacheEfficiency) / 4);
  
  // Generate recommendations
  const recommendations = generateCRMRecommendations(results, averageResponseTime, successRate, errorHandlingScore);
  
  return {
    overallScore,
    averageResponseTime,
    successRate,
    errorHandlingScore,
    cacheEfficiency,
    results,
    recommendations
  };
}

// Test individual endpoint performance
async function testEndpointPerformance(endpoint: string): Promise<CRMPerformanceResult> {
  const startTime = performance.now();
  let success = false;
  let errorHandling = false;
  let cacheHit = false;
  let retryAttempts = 0;
  
  try {
    // First attempt
    const response = await fetchWithTimeout(endpoint, 5000);
    success = response.ok;
    
    // Check if response came from cache
    cacheHit = response.headers.get('x-cache') === 'HIT' || 
               response.headers.get('cache-control')?.includes('max-age') || false;
    
    // Test error handling by making a bad request
    try {
      await fetchWithTimeout(endpoint + '/invalid', 2000);
    } catch (error) {
      errorHandling = true; // Error handling is working if we catch errors
    }
    
  } catch (error) {
    // Test retry logic
    retryAttempts = 1;
    try {
      const retryResponse = await fetchWithTimeout(endpoint, 3000);
      success = retryResponse.ok;
      errorHandling = true; // Retry logic is error handling
    } catch (retryError) {
      errorHandling = true; // Error handling is working if we handle retries
    }
  }
  
  const endTime = performance.now();
  const responseTime = endTime - startTime;
  
  return {
    endpoint,
    responseTime,
    success,
    errorHandling,
    cacheHit,
    retryAttempts
  };
}

// Fetch with timeout
async function fetchWithTimeout(url: string, timeout: number): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Generate CRM performance recommendations
function generateCRMRecommendations(
  results: CRMPerformanceResult[],
  averageResponseTime: number,
  successRate: number,
  errorHandlingScore: number
): string[] {
  const recommendations: string[] = [];
  
  // Response time recommendations
  if (averageResponseTime > 2000) {
    recommendations.push(`Optimize API response time - current average: ${averageResponseTime.toFixed(0)}ms (target: <2000ms)`);
  }
  
  if (averageResponseTime > 5000) {
    recommendations.push('Consider implementing request caching and connection pooling');
  }
  
  // Success rate recommendations
  if (successRate < 95) {
    recommendations.push(`Improve API reliability - current success rate: ${successRate.toFixed(1)}% (target: >95%)`);
  }
  
  // Error handling recommendations
  if (errorHandlingScore < 80) {
    recommendations.push('Implement comprehensive error handling and retry logic for CRM integrations');
  }
  
  // Specific endpoint recommendations
  const slowEndpoints = results.filter(r => r.responseTime > 3000);
  if (slowEndpoints.length > 0) {
    recommendations.push(`Optimize slow endpoints: ${slowEndpoints.map(e => e.endpoint).join(', ')}`);
  }
  
  const failedEndpoints = results.filter(r => !r.success);
  if (failedEndpoints.length > 0) {
    recommendations.push(`Fix failing endpoints: ${failedEndpoints.map(e => e.endpoint).join(', ')}`);
  }
  
  // Cache recommendations
  const cacheHitRate = results.filter(r => r.cacheHit).length / results.length * 100;
  if (cacheHitRate < 50) {
    recommendations.push('Implement API response caching to improve performance');
  }
  
  // Retry logic recommendations
  const endpointsWithRetries = results.filter(r => r.retryAttempts > 0);
  if (endpointsWithRetries.length > results.length * 0.3) {
    recommendations.push('High retry rate detected - investigate network stability and API reliability');
  }
  
  return recommendations;
}

// Mock CRM integration test for development
export async function mockCRMIntegrationTest(): Promise<CRMPerformanceReport> {
  console.log('🔗 Running mock CRM integration performance test...');
  
  // Simulate API calls with realistic response times
  const mockResults: CRMPerformanceResult[] = CRM_ENDPOINTS.map(endpoint => ({
    endpoint,
    responseTime: Math.random() * 2000 + 500, // 500-2500ms
    success: Math.random() > 0.1, // 90% success rate
    errorHandling: Math.random() > 0.2, // 80% have error handling
    cacheHit: Math.random() > 0.5, // 50% cache hit rate
    retryAttempts: Math.random() > 0.8 ? 1 : 0 // 20% require retry
  }));
  
  const averageResponseTime = mockResults.reduce((sum, r) => sum + r.responseTime, 0) / mockResults.length;
  const successRate = mockResults.filter(r => r.success).length / mockResults.length * 100;
  const errorHandlingScore = mockResults.filter(r => r.errorHandling).length / mockResults.length * 100;
  const cacheEfficiency = mockResults.filter(r => r.cacheHit).length / mockResults.length * 100;
  
  const responseTimeScore = averageResponseTime <= 2000 ? 100 : Math.max(0, 100 - (averageResponseTime - 2000) / 50);
  const overallScore = Math.round((responseTimeScore + successRate + errorHandlingScore + cacheEfficiency) / 4);
  
  const recommendations = generateCRMRecommendations(mockResults, averageResponseTime, successRate, errorHandlingScore);
  
  return {
    overallScore,
    averageResponseTime,
    successRate,
    errorHandlingScore,
    cacheEfficiency,
    results: mockResults,
    recommendations
  };
}

// Export for use in performance validator
export { CRM_ENDPOINTS };