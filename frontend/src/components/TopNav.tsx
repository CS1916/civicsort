'use client';

import React from 'react';
import { Sparkles, HelpCircle, Eye, RefreshCw, ShieldCheck, MapPin } from 'lucide-react';

interface TopNavProps {
  highContrast: boolean;
  onToggleHighContrast: () => void;
  onOpenHowItWorks: () => void;
  onRefreshData?: () => void;
  isOptimizing?: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({
  highContrast,
  onToggleHighContrast,
  onOpenHowItWorks,
  onRefreshData,
  isOptimizing = false,
}) => {
  return (
    <header
      className={`w-full border-b transition-colors duration-200 sticky top-0 z-40 ${
        highContrast
          ? 'bg-black text-white border-yellow-400'
          : 'bg-white/95 backdrop-blur-md text-slate-900 border-slate-200 shadow-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          {/* Title and Tagline */}
          <div className="flex items-start gap-3">
            <div
              className={`p-2.5 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                highContrast ? 'bg-yellow-400 text-black' : 'bg-emerald-600 text-white'
              }`}
            >
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    highContrast
                      ? 'bg-yellow-400 text-black font-bold'
                      : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                  }`}
                >
                  Smart City Sustainability System
                </span>
                <span className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Live AI Core & IoT Active
                </span>
              </div>
              <h1
                className={`text-base sm:text-lg lg:text-xl font-bold tracking-tight mt-0.5 ${
                  highContrast ? 'text-white' : 'text-slate-900'
                }`}
              >
                Computer Vision Waste Segregation & Intelligent Route Optimization
              </h1>
              <p
                className={`text-xs sm:text-sm mt-0.5 line-clamp-1 ${
                  highContrast ? 'text-gray-300' : 'text-slate-600'
                }`}
              >
                AI-guided waste classification with OR-Tools smart collection path for urban sanitation
              </p>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2.5 self-end lg:self-center flex-wrap">
            {onRefreshData && (
              <button
                onClick={onRefreshData}
                disabled={isOptimizing}
                title="Refresh IoT telemetry & recalculate routes"
                className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-medium rounded-lg border transition-all ${
                  highContrast
                    ? 'border-yellow-400 text-yellow-300 hover:bg-yellow-400/20'
                    : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 shadow-sm'
                } ${isOptimizing ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <RefreshCw className={`w-4 h-4 ${isOptimizing ? 'animate-spin text-emerald-600' : ''}`} />
                <span className="hidden sm:inline">Refresh Sensors</span>
              </button>
            )}

            <button
              onClick={onOpenHowItWorks}
              className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-medium rounded-lg border transition-all ${
                highContrast
                  ? 'border-yellow-400 text-yellow-300 hover:bg-yellow-400/20'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 shadow-sm'
              }`}
            >
              <HelpCircle className="w-4 h-4 text-emerald-600" />
              <span>How It Works</span>
            </button>

            <button
              onClick={onToggleHighContrast}
              title={highContrast ? 'Switch to Standard Light Mode' : 'Switch to High Contrast Accessibility Mode'}
              className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-semibold rounded-lg border transition-all ${
                highContrast
                  ? 'bg-yellow-400 text-black border-yellow-400 hover:bg-yellow-300'
                  : 'bg-slate-900 text-white border-slate-900 hover:bg-slate-800 shadow-sm'
              }`}
            >
              <Eye className="w-4 h-4" />
              <span>{highContrast ? 'Standard View' : 'High Contrast'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
