import React, { useState, useEffect } from 'react';
import { analyzeBundlePerformance, BundleAnalysis } from '../../utils/bundleOptimization';
import { generateMobileOptimizationReport, MobileOptimizationReport } from '../../utils/mobileValidation';
import { measureWebVitals, PerformanceMetrics } from '../../utils/performanceMonitoring';
import { getPWACapabilities } from '../../utils/serviceWorker';

interface PerformanceDashboardProps {
  isVisible: boolean;
  onClose: () => void;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ isVisible, onClose }) => {
  const [bundleAnalysis, setBundleAnalysis] = useState<BundleAnalysis | null>(null);
  const [mobileReport, setMobileReport] = useState<MobileOptimizationReport | null>(null);
  const [webVitals, setWebVitals] = useState<Partial<PerformanceMetrics> | null>(null);
  const [pwaCapabilities, setPwaCapabilities] = useState(getPWACapabilities());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      runPerformanceAnalysis();
    }
  }, [isVisible]);

  const runPerformanceAnalysis = async () => {
    setLoading(true);
    try {
      // Bundle analysis
      const bundle = analyzeBundlePerformance();
      setBundleAnalysis(bundle);

      // Mobile optimization report
      const mobile = await generateMobileOptimizationReport();
      setMobileReport(mobile);

      // Web vitals
      const vitals = await measureWebVitals();
      setWebVitals(vitals);

      // PWA capabilities
      const pwa = getPWACapabilities();
      setPwaCapabilities(pwa);
    } catch (error) {
      console.error('Performance analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Performance Dashboard</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Analyzing performance...</p>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Web Vitals */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Core Web Vitals</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {webVitals?.fcp ? `${Math.round(webVitals.fcp)}ms` : 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">FCP</div>
                    <div className={`text-xs ${webVitals?.fcp && webVitals.fcp <= 1800 ? 'text-green-600' : 'text-red-600'}`}>
                      {webVitals?.fcp && webVitals.fcp <= 1800 ? 'Good' : 'Needs Work'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {webVitals?.lcp ? `${Math.round(webVitals.lcp)}ms` : 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">LCP</div>
                    <div className={`text-xs ${webVitals?.lcp && webVitals.lcp <= 2500 ? 'text-green-600' : 'text-red-600'}`}>
                      {webVitals?.lcp && webVitals.lcp <= 2500 ? 'Good' : 'Needs Work'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {webVitals?.fid ? `${Math.round(webVitals.fid)}ms` : 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">FID</div>
                    <div className={`text-xs ${webVitals?.fid && webVitals.fid <= 100 ? 'text-green-600' : 'text-red-600'}`}>
                      {webVitals?.fid && webVitals.fid <= 100 ? 'Good' : 'Needs Work'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {webVitals?.cls ? webVitals.cls.toFixed(3) : 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">CLS</div>
                    <div className={`text-xs ${webVitals?.cls && webVitals.cls <= 0.1 ? 'text-green-600' : 'text-red-600'}`}>
                      {webVitals?.cls && webVitals.cls <= 0.1 ? 'Good' : 'Needs Work'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Bundle Analysis */}
              {bundleAnalysis && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-4">Bundle Analysis</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(bundleAnalysis.jsSize / 1024).toFixed(1)}KB
                      </div>
                      <div className="text-sm text-gray-600">JavaScript</div>
                      <div className={`text-xs ${bundleAnalysis.jsSize <= 150000 ? 'text-green-600' : 'text-red-600'}`}>
                        {bundleAnalysis.jsSize <= 150000 ? 'Good' : 'Too Large'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(bundleAnalysis.cssSize / 1024).toFixed(1)}KB
                      </div>
                      <div className="text-sm text-gray-600">CSS</div>
                      <div className={`text-xs ${bundleAnalysis.cssSize <= 50000 ? 'text-green-600' : 'text-red-600'}`}>
                        {bundleAnalysis.cssSize <= 50000 ? 'Good' : 'Too Large'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {bundleAnalysis.chunkCount}
                      </div>
                      <div className="text-sm text-gray-600">Chunks</div>
                      <div className={`text-xs ${bundleAnalysis.chunkCount >= 3 ? 'text-green-600' : 'text-yellow-600'}`}>
                        {bundleAnalysis.chunkCount >= 3 ? 'Good' : 'Consider Splitting'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(bundleAnalysis.totalSize / 1024).toFixed(1)}KB
                      </div>
                      <div className="text-sm text-gray-600">Total</div>
                    </div>
                  </div>
                  {bundleAnalysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Recommendations:</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {bundleAnalysis.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-yellow-500 mr-2">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Mobile Optimization */}
              {mobileReport && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-4">Mobile Optimization</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {mobileReport.overallScore}%
                      </div>
                      <div className="text-sm text-gray-600">Overall Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {mobileReport.performanceMetrics.loadTime}ms
                      </div>
                      <div className="text-sm text-gray-600">Load Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {mobileReport.accessibilityScore}%
                      </div>
                      <div className="text-sm text-gray-600">Accessibility</div>
                    </div>
                  </div>
                  {mobileReport.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Mobile Recommendations:</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {mobileReport.recommendations.slice(0, 5).map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* PWA Capabilities */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">PWA Features</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.serviceWorker ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm">Service Worker</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.pushNotifications ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm">Push Notifications</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.backgroundSync ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm">Background Sync</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.webShare ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm">Web Share</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.installPrompt ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm">Install Prompt</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${pwaCapabilities.isInstalled ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm">Installed</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-center space-x-4">
                <button
                  onClick={runPerformanceAnalysis}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Refresh Analysis
                </button>
                <button
                  onClick={onClose}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
