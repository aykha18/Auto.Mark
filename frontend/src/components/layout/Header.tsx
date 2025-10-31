import React, { useState } from 'react';
import { Menu, X, Zap } from 'lucide-react';
import { Button } from '../ui';
import PWAInstallButton from '../ui/PWAInstallButton';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Unitasa</h1>
                <p className="text-xs text-gray-500">Unified Marketing Intelligence</p>
              </div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-700 hover:text-primary-600 transition-colors">
              Features
            </a>
            <a href="#integrations" className="text-gray-700 hover:text-primary-600 transition-colors">
              Integrations
            </a>
            <a href="#assessment" className="text-gray-700 hover:text-primary-600 transition-colors">
              Assessment
            </a>
            <a href="#story" className="text-gray-700 hover:text-primary-600 transition-colors">
              Our Story
            </a>
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <PWAInstallButton className="text-xs" />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openAssessment'));
              }}
            >
              Take Assessment
            </Button>
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => {
                const coCreatorSection = document.querySelector('#co-creator');
                if (coCreatorSection) {
                  coCreatorSection.scrollIntoView({ behavior: 'smooth' });
                } else {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }
              }}
            >
              Join Co-Creators
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-700 hover:text-primary-600 transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              <a
                href="#features"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Features
              </a>
              <a
                href="#integrations"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Integrations
              </a>
              <a
                href="#assessment"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Assessment
              </a>
              <a
                href="#story"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Our Story
              </a>
              <div className="pt-4 border-t border-gray-200 space-y-2">
                <PWAInstallButton className="w-full text-sm" />
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => {
                    toggleMenu();
                    window.dispatchEvent(new CustomEvent('openAssessment'));
                  }}
                >
                  Take Assessment
                </Button>
                <Button 
                  variant="primary" 
                  size="sm" 
                  className="w-full"
                  onClick={() => {
                    toggleMenu();
                    const coCreatorSection = document.querySelector('#co-creator');
                    if (coCreatorSection) {
                      coCreatorSection.scrollIntoView({ behavior: 'smooth' });
                    } else {
                      window.dispatchEvent(new CustomEvent('openAssessment'));
                    }
                  }}
                >
                  Join Co-Creators
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
