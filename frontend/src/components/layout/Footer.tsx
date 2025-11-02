import React from 'react';
import { Zap, Mail, Linkedin, Twitter } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Unitasa</h3>
                <p className="text-sm text-gray-400">Unified Marketing Intelligence Platform</p>
              </div>
            </div>
            <p className="text-gray-400 mb-4 max-w-md">
              One platform. Unified marketing. The only AI marketing intelligence you'll ever need - 
              replacing fragmented tools with complete marketing unity.
            </p>
            <div className="flex space-x-4">
              <a href="mailto:hello@unitasa.in" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
              <a href="https://linkedin.com/company/unitasa" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="https://twitter.com/unitasa" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#integrations" className="hover:text-white transition-colors">Integrations</a></li>
              <li>
                <a
                  href="#assessment"
                  className="hover:text-white transition-colors cursor-pointer"
                  onClick={(e) => {
                    e.preventDefault();
                    window.dispatchEvent(new CustomEvent('openLeadCapture'));
                  }}
                >
                  AI Assessment
                </a>
              </li>
              <li><a href="#pricing" className="hover:text-white transition-colors">Co-Creator Program</a></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#docs" className="hover:text-white transition-colors">Documentation</a></li>
              <li><a href="#help" className="hover:text-white transition-colors">Help Center</a></li>
              <li><a href="#contact" className="hover:text-white transition-colors">Contact Us</a></li>
              <li><a href="#status" className="hover:text-white transition-colors">System Status</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2025 Unitasa. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#privacy" className="text-gray-400 hover:text-white text-sm transition-colors">
              Privacy Policy
            </a>
            <a href="#terms" className="text-gray-400 hover:text-white text-sm transition-colors">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
