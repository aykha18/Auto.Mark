import React, { useState, useEffect } from 'react';
import { showInstallPrompt, getPWACapabilities } from '../../utils/serviceWorker';

interface PWAInstallButtonProps {
  className?: string;
}

const PWAInstallButton: React.FC<PWAInstallButtonProps> = ({ className = '' }) => {
  const [showButton, setShowButton] = useState(false);
  const [capabilities, setCapabilities] = useState(getPWACapabilities());

  useEffect(() => {
    // Check if install prompt is available
    const checkInstallPrompt = () => {
      const updatedCapabilities = getPWACapabilities();
      setCapabilities(updatedCapabilities);
      setShowButton(updatedCapabilities.installPrompt && !updatedCapabilities.isInstalled);
    };

    // Initial check
    checkInstallPrompt();

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = () => {
      setShowButton(true);
    };

    // Listen for app installed event
    const handleAppInstalled = () => {
      setShowButton(false);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = () => {
    showInstallPrompt();
  };

  if (!showButton || capabilities.isInstalled) {
    return null;
  }

  return (
    <button
      id="pwa-install-button"
      onClick={handleInstallClick}
      className={`
        inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md
        text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500
        transition-colors duration-200
        ${className}
      `}
      aria-label="Install Auto.Mark as a Progressive Web App"
    >
      <svg 
        className="w-4 h-4 mr-2" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
        />
      </svg>
      Install App
    </button>
  );
};

export default PWAInstallButton;