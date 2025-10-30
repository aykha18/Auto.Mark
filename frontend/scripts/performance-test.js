#!/usr/bin/env node

const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs');
const path = require('path');

async function runPerformanceAudit() {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {
    logLevel: 'info',
    output: 'html',
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: chrome.port,
  };

  // Test URLs
  const urls = [
    'http://localhost:3000',
    'http://localhost:3000/?mobile=true'
  ];

  const results = [];

  for (const url of urls) {
    console.log(`Testing ${url}...`);
    
    try {
      const runnerResult = await lighthouse(url, options);
      const reportHtml = runnerResult.report;
      const scores = runnerResult.lhr.categories;

      // Save report
      const reportPath = path.join(__dirname, `../lighthouse-report-${Date.now()}.html`);
      fs.writeFileSync(reportPath, reportHtml);

      // Extract key metrics
      const metrics = {
        url,
        performance: scores.performance.score * 100,
        accessibility: scores.accessibility.score * 100,
        bestPractices: scores['best-practices'].score * 100,
        seo: scores.seo.score * 100,
        fcp: runnerResult.lhr.audits['first-contentful-paint'].numericValue,
        lcp: runnerResult.lhr.audits['largest-contentful-paint'].numericValue,
        cls: runnerResult.lhr.audits['cumulative-layout-shift'].numericValue,
        fid: runnerResult.lhr.audits['max-potential-fid']?.numericValue || 0,
        bundleSize: runnerResult.lhr.audits['total-byte-weight'].numericValue,
        reportPath
      };

      results.push(metrics);
      console.log(`Performance Score: ${metrics.performance}`);
      console.log(`FCP: ${metrics.fcp}ms`);
      console.log(`LCP: ${metrics.lcp}ms`);
      console.log(`CLS: ${metrics.cls}`);
      console.log(`Bundle Size: ${(metrics.bundleSize / 1024).toFixed(2)} KB`);
      console.log(`Report saved to: ${reportPath}\n`);

    } catch (error) {
      console.error(`Error testing ${url}:`, error.message);
    }
  }

  await chrome.kill();

  // Generate summary report
  const summaryPath = path.join(__dirname, '../performance-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(results, null, 2));
  
  console.log('Performance audit complete!');
  console.log(`Summary saved to: ${summaryPath}`);

  // Check if performance targets are met
  const desktopResult = results.find(r => !r.url.includes('mobile'));
  if (desktopResult) {
    console.log('\n=== Performance Targets ===');
    console.log(`Performance Score: ${desktopResult.performance >= 90 ? '✅' : '❌'} ${desktopResult.performance}/100 (target: 90+)`);
    console.log(`FCP: ${desktopResult.fcp <= 1800 ? '✅' : '❌'} ${desktopResult.fcp}ms (target: <1.8s)`);
    console.log(`LCP: ${desktopResult.lcp <= 2500 ? '✅' : '❌'} ${desktopResult.lcp}ms (target: <2.5s)`);
    console.log(`CLS: ${desktopResult.cls <= 0.1 ? '✅' : '❌'} ${desktopResult.cls} (target: <0.1)`);
    console.log(`Bundle Size: ${desktopResult.bundleSize <= 150000 ? '✅' : '❌'} ${(desktopResult.bundleSize / 1024).toFixed(2)} KB (target: <150KB)`);
  }

  return results;
}

// Run if called directly
if (require.main === module) {
  runPerformanceAudit().catch(console.error);
}

module.exports = { runPerformanceAudit };