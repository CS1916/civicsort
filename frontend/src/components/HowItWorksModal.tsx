'use client';

import React from 'react';
import { X, Camera, Radio, Navigation, CheckCircle2, ArrowRight } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
  highContrast: boolean;
}

export const HowItWorksModal: React.FC<HowItWorksModalProps> = ({
  isOpen,
  onClose,
  highContrast,
}) => {
  if (!isOpen) return null;

  const steps = [
    {
      step: '1',
      title: 'Scan & Segregate',
      actor: 'City Resident / Sanitation Worker',
      icon: Camera,
      color: 'bg-blue-600',
      lightColor: 'bg-blue-50 text-blue-700 border-blue-200',
      description:
        'Point your smartphone or webcam at any waste item. Our deep-learning YOLO vision model instantly identifies the material and shows a clear color-coded bin badge (Blue = Recyclable, Green = Organic, Red = Hazardous).',
      tag: 'Zero Confusion at Source',
    },
    {
      step: '2',
      title: 'IoT Fill Monitoring',
      actor: 'Smart Urban Bins',
      icon: Radio,
      color: 'bg-amber-600',
      lightColor: 'bg-amber-50 text-amber-700 border-amber-200',
      description:
        'Ultrasonic IoT sensors track bin capacity in real-time. Bins are flagged as Empty (<40%), Half-Full (40–74%), or Full (≥75% Alert). Only full bins request immediate truck pickup, eliminating empty trips.',
      tag: 'Real-Time Sensor Telemetry',
    },
    {
      step: '3',
      title: 'Smart Fleet Routing',
      actor: 'Municipal Collection Trucks',
      icon: Navigation,
      color: 'bg-emerald-600',
      lightColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      description:
        'Instead of driving rigid fixed loops through every street, Google OR-Tools dynamically solves the optimal path for collection trucks to service only full bins. This saves over 50% in travel distance, diesel fuel, and CO₂ emissions.',
      tag: 'Google OR-Tools Optimization',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div
        className={`w-full max-w-2xl rounded-2xl border p-6 sm:p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto ${
          highContrast ? 'bg-black border-2 border-yellow-400 text-white' : 'bg-white border-slate-200'
        }`}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className={`absolute top-4 right-4 p-2 rounded-xl border transition-colors ${
            highContrast
              ? 'border-yellow-400 text-yellow-300 hover:bg-yellow-400/20'
              : 'border-slate-200 text-slate-500 hover:bg-slate-100 hover:text-slate-800'
          }`}
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <span
            className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
              highContrast ? 'bg-yellow-400 text-black' : 'bg-emerald-100 text-emerald-800'
            }`}
          >
            Quick 3-Step Guide
          </span>
          <h2
            className={`text-xl sm:text-2xl font-bold mt-2 ${
              highContrast ? 'text-white' : 'text-slate-900'
            }`}
          >
            How the Smart Waste System Works
          </h2>
          <p className={`text-xs sm:text-sm mt-1 ${highContrast ? 'text-gray-300' : 'text-slate-600'}`}>
            Simple, sustainable waste handling for residents, sanitation workers, and city planners.
          </p>
        </div>

        {/* 3 Step Cards */}
        <div className="space-y-4 mb-6">
          {steps.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className={`p-4 rounded-xl border transition-all ${
                  highContrast
                    ? 'bg-black border-yellow-400'
                    : 'bg-slate-50/70 border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 font-extrabold text-white shadow-sm ${
                      highContrast ? 'bg-yellow-400 text-black' : item.color
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
                      <h3
                        className={`text-sm sm:text-base font-bold ${
                          highContrast ? 'text-yellow-400' : 'text-slate-900'
                        }`}
                      >
                        Step {item.step}: {item.title}
                      </h3>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          highContrast ? 'bg-yellow-400 text-black border-yellow-400' : item.lightColor
                        }`}
                      >
                        {item.tag}
                      </span>
                    </div>

                    <p
                      className={`text-xs sm:text-sm leading-relaxed mb-1 ${
                        highContrast ? 'text-gray-200' : 'text-slate-600'
                      }`}
                    >
                      {item.description}
                    </p>

                    <div className="text-[11px] font-semibold text-slate-500">
                      Primary User: <span className="text-slate-700 font-bold">{item.actor}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Call to action footer */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm flex items-center gap-2 ${
              highContrast
                ? 'bg-yellow-400 text-black hover:bg-yellow-300'
                : 'bg-emerald-600 text-white hover:bg-emerald-700'
            }`}
          >
            <span>Got It — Let's Explore</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
