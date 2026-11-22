'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import {
  Navigation,
  Sparkles,
  Clock,
  Gauge,
  Leaf,
  Fuel,
  TrendingDown,
  Info,
  Sliders,
  CheckCircle,
} from 'lucide-react';
import { SmartBin, RouteOptimizationResult } from '../types';

// Dynamic import with SSR disabled for Leaflet map
const RouteMapLeaflet = dynamic(() => import('./RouteMapLeaflet'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[420px] bg-slate-100 rounded-2xl flex flex-col items-center justify-center text-slate-500 gap-3">
      <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-sm font-semibold">Loading Urban Smart Grid Map...</p>
    </div>
  ),
});

interface RouteMapProps {
  highContrast: boolean;
  routeResult: RouteOptimizationResult;
  bins: SmartBin[];
  onTriggerFillSim?: () => void;
  onSelectBin?: (bin: SmartBin) => void;
}

export const RouteMap: React.FC<RouteMapProps> = ({
  highContrast,
  routeResult,
  bins,
  onTriggerFillSim,
  onSelectBin,
}) => {
  const [routeType, setRouteType] = useState<'smart' | 'standard'>('smart');

  const activeRouteData =
    routeType === 'smart' ? routeResult.aiSmartRoute : routeResult.standardRoute;
  const standardStats = routeResult.standardRoute.stats;
  const aiStats = routeResult.aiSmartRoute.stats;
  const savings = routeResult.savings;

  return (
    <div
      className={`rounded-2xl border p-5 sm:p-6 transition-all shadow-sm flex flex-col h-full ${
        highContrast ? 'bg-black border-2 border-yellow-400 text-white' : 'bg-white border-slate-200'
      }`}
    >
      {/* Header & Prominent Mode Toggle Switch */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100">
        <div>
          <span
            className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
              highContrast ? 'bg-yellow-400 text-black' : 'bg-emerald-100 text-emerald-800'
            }`}
          >
            Module 2
          </span>
          <h2
            className={`text-lg sm:text-xl font-bold mt-1 ${
              highContrast ? 'text-white' : 'text-slate-900'
            }`}
          >
            Intelligent Route Map
          </h2>
          <p className={`text-xs sm:text-sm ${highContrast ? 'text-gray-300' : 'text-slate-500'}`}>
            Live GPS telemetry & Google OR-Tools vehicle routing
          </p>
        </div>

        {/* The Prominent Toggle Switch */}
        <div
          className={`p-1 rounded-xl flex items-center border ${
            highContrast ? 'bg-black border-yellow-400' : 'bg-slate-100 border-slate-200'
          }`}
        >
          <button
            onClick={() => setRouteType('smart')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm ${
              routeType === 'smart'
                ? highContrast
                  ? 'bg-yellow-400 text-black'
                  : 'bg-emerald-600 text-white shadow'
                : highContrast
                ? 'text-yellow-400 hover:bg-yellow-400/20'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Smart Route (Full Only)</span>
          </button>

          <button
            onClick={() => setRouteType('standard')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              routeType === 'standard'
                ? highContrast
                  ? 'bg-yellow-400 text-black'
                  : 'bg-blue-600 text-white shadow'
                : highContrast
                ? 'text-yellow-400 hover:bg-yellow-400/20'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Navigation className="w-3.5 h-3.5" />
            <span>Standard Route (All Bins)</span>
          </button>
        </div>
      </div>

      {/* Map Legend & Fast Sim Trigger */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 text-xs">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px]">
            Bin Status:
          </span>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
            <span className="text-slate-700 font-medium">Empty (&lt;40%)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-700 font-medium">Half-Full (40-74%)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse"></span>
            <span className="text-red-700 font-bold">Full / Needs Pickup (≥75%)</span>
          </div>
        </div>

        {onTriggerFillSim && (
          <button
            onClick={onTriggerFillSim}
            title="Randomize bin sensor levels to test OR-Tools adaptation"
            className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 hover:text-emerald-700 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-md transition-colors"
          >
            <Sliders className="w-3 h-3 text-emerald-600" />
            <span>Simulate Sensor Changes</span>
          </button>
        )}
      </div>

      {/* Map Container */}
      <div className="w-full flex-1 min-h-[380px] rounded-2xl overflow-hidden border border-slate-200 shadow-sm mb-4 relative">
        <RouteMapLeaflet
          depot={routeResult.depot}
          bins={bins}
          activeRoutePoints={activeRouteData.points}
          routeType={routeType}
          highContrast={highContrast}
          onSelectBin={onSelectBin}
        />

        {/* Floating Route Banner */}
        <div className="absolute top-3 right-3 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 shadow-md z-[1000] text-xs flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              routeType === 'smart' ? 'bg-emerald-500' : 'bg-blue-500'
            }`}
          ></span>
          <span className="font-bold text-slate-800">
            {routeType === 'smart' ? 'AI Optimized Path' : 'Conventional Fixed Loop'}
          </span>
          <span className="text-slate-500 text-[11px]">
            ({activeRouteData.stats.binsVisited} bins stopped)
          </span>
        </div>
      </div>

      {/* Side-by-Side Comparison Box Below Map */}
      <div
        className={`p-4 rounded-2xl border transition-all ${
          highContrast
            ? 'bg-black border-2 border-yellow-400 text-white'
            : 'bg-emerald-50/70 border-emerald-200'
        }`}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-emerald-600" />
            <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-emerald-900">
              Live Impact & Savings Audit
            </h3>
          </div>
          <span className="text-[11px] font-semibold text-emerald-700 bg-white px-2 py-0.5 rounded border border-emerald-200">
            AI Smart vs. Standard Fixed Route
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Distance Saved */}
          <div className="bg-white p-3 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-[11px] font-medium">Distance Saved</span>
              <Gauge className="w-3.5 h-3.5 text-emerald-600" />
            </div>
            <p className="text-lg font-black text-slate-900">
              {savings.distanceSavedKm} km
            </p>
            <span className="text-[11px] font-bold text-emerald-600">
              ↓ {savings.distanceSavedPercent}% shorter
            </span>
          </div>

          {/* Time Saved */}
          <div className="bg-white p-3 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-[11px] font-medium">Time Saved</span>
              <Clock className="w-3.5 h-3.5 text-blue-600" />
            </div>
            <p className="text-lg font-black text-slate-900">
              {savings.timeSavedMins} mins
            </p>
            <span className="text-[11px] font-bold text-blue-600">
              ↓ {savings.timeSavedPercent}% faster turnaround
            </span>
          </div>

          {/* CO2 Reduced */}
          <div className="bg-white p-3 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-[11px] font-medium">CO₂ Avoided</span>
              <Leaf className="w-3.5 h-3.5 text-emerald-600" />
            </div>
            <p className="text-lg font-black text-emerald-700">
              {savings.co2SavedKg} kg
            </p>
            <span className="text-[11px] font-semibold text-slate-500">
              Per collection cycle
            </span>
          </div>

          {/* Fuel Saved */}
          <div className="bg-white p-3 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-[11px] font-medium">Diesel Saved</span>
              <Fuel className="w-3.5 h-3.5 text-amber-600" />
            </div>
            <p className="text-lg font-black text-slate-900">
              {savings.fuelSavedLiters} Liters
            </p>
            <span className="text-[11px] font-semibold text-slate-500">
              Direct municipal savings
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
