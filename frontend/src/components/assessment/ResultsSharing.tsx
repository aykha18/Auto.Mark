import React, { useState } from 'react';
import { CRMAssessmentResult } from '../../types';
import Button from '../ui/Button';
import { Share2, Download, Mail, Copy, Check } from 'lucide-react';

interface ResultsSharingProps {
  result: CRMAssessmentResult;
}

const ResultsSharing: React.FC<ResultsSharingProps> = ({ result }) => {
  const [copied, setCopied] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  // Normalize property names to handle both camelCase and snake_case
  const normalizedResult = {
    currentCRM: result.currentCRM || (result as any).current_crm || 'Unknown',
    integrationScore: result.integrationScore || (result as any).overall_score || 0,
    readinessLevel: result.readinessLevel || (result as any).readiness_level || 'nurture_with_guides',
    integrationRecommendations: result.integrationRecommendations || (result as any).integration_recommendations || [],
    automationOpportunities: result.automationOpportunities || (result as any).automation_opportunities || [],
    technicalRequirements: result.technicalRequirements || (result as any).technical_requirements || [],
    nextSteps: result.nextSteps || (result as any).next_steps || []
  };

  const generateShareableUrl = () => {
    const baseUrl = window.location.origin;
    const params = new URLSearchParams({
      score: normalizedResult.integrationScore.toString(),
      level: normalizedResult.readinessLevel,
      crm: normalizedResult.currentCRM,
    });
    return `${baseUrl}/assessment-results?${params.toString()}`;
  };

  const generateShareText = () => {
    const readinessText = normalizedResult.readinessLevel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    const topRecommendation = normalizedResult.integrationRecommendations?.[0] || 'Ready for AI automation';
    
    return `🚀 Just completed an AI Readiness Assessment and scored ${normalizedResult.integrationScore}/100!

📊 Readiness Level: ${readinessText}
🔧 Current CRM: ${normalizedResult.currentCRM}
💡 Key Insight: ${topRecommendation}

Discover how Auto.Mark can automate your marketing with any CRM: ${generateShareableUrl()}

#AIAutomation #CRMIntegration #MarketingTech`;
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(generateShareableUrl());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy link:', error);
    }
  };

  const handleEmailResults = async () => {
    try {
      // Send email with comprehensive results summary
      const emailData = {
        subject: `Your AI Readiness Assessment Results - Score: ${normalizedResult.integrationScore}/100`,
        template: 'assessment_results',
        data: {
          score: normalizedResult.integrationScore,
          readinessLevel: normalizedResult.readinessLevel,
          currentCRM: normalizedResult.currentCRM,
          recommendations: normalizedResult.integrationRecommendations,
          automationOpportunities: normalizedResult.automationOpportunities,
          technicalRequirements: normalizedResult.technicalRequirements,
          nextSteps: normalizedResult.nextSteps,
          shareUrl: generateShareableUrl(),
          timestamp: new Date().toISOString()
        }
      };
      
      // Call the backend API to send email
      await fetch('/api/v1/landing/email-results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });
      
      setEmailSent(true);
      setTimeout(() => setEmailSent(false), 3000);
    } catch (error) {
      console.error('Failed to send email:', error);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      // Generate comprehensive PDF report
      const reportData = {
        title: 'AI Readiness Assessment Report',
        subtitle: `${normalizedResult.currentCRM} Integration Analysis`,
        score: normalizedResult.integrationScore,
        readinessLevel: normalizedResult.readinessLevel,
        currentCRM: normalizedResult.currentCRM,
        generatedAt: new Date().toLocaleDateString(),
        sections: [
          {
            title: 'Executive Summary',
            content: `Your business scored ${normalizedResult.integrationScore}/100 on AI readiness, qualifying for ${normalizedResult.readinessLevel.replace('_', ' ')} status.`
          },
          {
            title: 'Integration Recommendations',
            items: normalizedResult.integrationRecommendations
          },
          {
            title: 'Automation Opportunities',
            items: normalizedResult.automationOpportunities
          },
          {
            title: 'Technical Requirements',
            items: normalizedResult.technicalRequirements
          },
          {
            title: 'Implementation Roadmap',
            items: normalizedResult.nextSteps
          }
        ]
      };
      
      // Call backend PDF generation service
      const response = await fetch('/api/v1/landing/generate-pdf-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AI-Readiness-Report-${normalizedResult.currentCRM}-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to generate PDF:', error);
    }
  };

  const handleSocialShare = (platform: 'linkedin' | 'twitter') => {
    const text = encodeURIComponent(generateShareText());
    const url = encodeURIComponent(generateShareableUrl());
    
    let shareUrl = '';
    
    switch (platform) {
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&summary=${text}`;
        break;
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${text}`;
        break;
    }
    
    window.open(shareUrl, '_blank', 'width=600,height=400');
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <Share2 className="w-6 h-6 text-primary-600 mr-3" />
        <h3 className="text-xl font-bold text-gray-900">Share Your Results</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Copy Link */}
        <Button
          variant="outline"
          onClick={handleCopyLink}
          icon={copied ? Check : Copy}
          iconPosition="left"
          className="w-full"
        >
          {copied ? 'Copied!' : 'Copy Link'}
        </Button>

        {/* Email Results */}
        <Button
          variant="outline"
          onClick={handleEmailResults}
          icon={emailSent ? Check : Mail}
          iconPosition="left"
          className="w-full"
        >
          {emailSent ? 'Sent!' : 'Email Results'}
        </Button>

        {/* Download PDF */}
        <Button
          variant="outline"
          onClick={handleDownloadPDF}
          icon={Download}
          iconPosition="left"
          className="w-full"
        >
          Download PDF Report
        </Button>

        {/* LinkedIn Share */}
        <Button
          variant="outline"
          onClick={() => handleSocialShare('linkedin')}
          className="w-full bg-blue-600 text-white hover:bg-blue-700 border-blue-600"
        >
          Share on LinkedIn
        </Button>
      </div>

      {/* Additional Sharing Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Button
          variant="ghost"
          onClick={() => handleSocialShare('twitter')}
          className="w-full text-blue-400 hover:bg-blue-50"
        >
          Share on Twitter
        </Button>
        
        <Button
          variant="ghost"
          onClick={() => {
            const subject = encodeURIComponent(`Check out my AI Readiness Assessment results`);
            const body = encodeURIComponent(generateShareText());
            window.location.href = `mailto:?subject=${subject}&body=${body}`;
          }}
          className="w-full text-gray-600 hover:bg-gray-50"
        >
          Share via Email
        </Button>
      </div>

      {/* Results Summary for Sharing */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-900 mb-2">Results Summary:</h4>
        <div className="text-sm text-gray-700 space-y-1">
          <div>AI Readiness Score: <span className="font-semibold">{normalizedResult.integrationScore}/100</span></div>
          <div>Current CRM: <span className="font-semibold">{normalizedResult.currentCRM}</span></div>
          <div>Readiness Level: <span className="font-semibold">{normalizedResult.readinessLevel.replace('_', ' ')}</span></div>
          <div>Key Recommendations: <span className="font-semibold">{normalizedResult.integrationRecommendations?.length || 0} items</span></div>
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        Results are saved to your account and can be accessed anytime
      </div>
    </div>
  );
};

export default ResultsSharing;