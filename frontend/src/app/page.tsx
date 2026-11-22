'use client';

import React, { useState } from 'react';
import { TopNav } from '../components/TopNav';
import { SummaryCards } from '../components/SummaryCards';
import { WasteScanner } from '../components/WasteScanner';
import { RouteMap } from '../components/RouteMap';
import { PerformanceCharts } from '../components/PerformanceCharts';
import { HowItWorksModal } from '../components/HowItWorksModal';
import { INITIAL_SMART_BINS, MOCK_ROUTE_RESULT } from '../lib/mockData';
import { optimizeRoute } from '../lib/api';
import { SmartBin, RouteOptimizationResult, WasteDetection } from '../types';

export default function Home() {
  const [highContrast, setHighContrast] = useState<boolean>(false);
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState<boolean>(false);

  // Core application state
  const [bins, setBins] = useState<SmartBin[]>(INITIAL_SMART_BINS);
  const [routeResult, setRouteResult] = useState<RouteOptimizationResult>(MOCK_ROUTE_RESULT);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);

  // Live counters
  const [totalItemsSorted, setTotalItemsSorted] = useState<number>(14820);
  const [lastScannedItem, setLastScannedItem] = useState<WasteDetection | null>(null);

  // Simulate updating bin fill levels (e.g. sensor updates from field)
  const handleTriggerFillSim = async () => {
    setIsOptimizing(true);
    try {
      const updatedBins = bins.map((b) => {
        // Randomly simulate fill fluctuation
        const change = Math.floor(Math.random() * 35) - 15;
        const newLevel = Math.max(5, Math.min(98, b.fillLevel + change));
        return {
          ...b,
          fillLevel: newLevel,
          needsPickup: newLevel >= 75,
          lastUpdated: 'Just now',
        };
      });

      setBins(updatedBins);

      // Re-solve vehicle routing via OR-Tools endpoint / solver
      const newRoute = await optimizeRoute(updatedBins);
      setRouteResult(newRoute);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleScanComplete = (detection: WasteDetection) => {
    setTotalItemsSorted((prev) => prev + 1);
    setLastScannedItem(detection);
  };

  const fullBinsCount = bins.filter((b) => b.fillLevel >= 75).length;

  return (
    <div
      className={`min-h-screen transition-colors duration-200 flex flex-col font-sans ${
        highContrast ? 'bg-black text-white' : 'bg-[#F8FAFC] text-slate-900'
      }`}
    >
      {/* Top Navigation */}
      <TopNav
        highContrast={highContrast}
        onToggleHighContrast={() => setHighContrast(!highContrast)}
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
        onRefreshData={handleTriggerFillSim}
        isOptimizing={isOptimizing}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* 4 Summary Cards */}
        <SummaryCards
          highContrast={highContrast}
          totalSorted={totalItemsSorted}
          accuracyRate={96.4}
          savingsPercent={routeResult.savings.distanceSavedPercent}
          activeBinsCount={bins.length}
          totalBinsCount={bins.length}
          binsNeedingPickup={fullBinsCount}
        />

        {/* 2-Column Core Dashboard: Left = Waste Scanner (CV), Right = Route Map (OR-Tools) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Left Panel: Waste Scanner (approx 5 cols on desktop) */}
          <div className="lg:col-span-5 h-full">
            <WasteScanner
              highContrast={highContrast}
              onScanComplete={handleScanComplete}
            />
          </div>

          {/* Right Panel: Intelligent Route Map (approx 7 cols on desktop) */}
          <div className="lg:col-span-7 h-full">
            <RouteMap
              highContrast={highContrast}
              routeResult={routeResult}
              bins={bins}
              onTriggerFillSim={handleTriggerFillSim}
            />
          </div>
        </div>

        {/* Bottom Section: Simple Performance Comparison & Charts */}
        <PerformanceCharts
          highContrast={highContrast}
          routeResult={routeResult}
        />
      </main>

      {/* Executive Footer */}
      <footer
        className={`w-full border-t py-6 mt-8 transition-colors ${
          highContrast ? 'bg-black border-yellow-400 text-gray-400' : 'bg-white border-slate-200 text-slate-500'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <div>
            <p className="font-bold text-slate-800">
              Computer Vision Based Waste Segregation and Intelligent Collection Route Optimization
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Designed for Sustainable Urban Waste Management, Zero-Jargon Municipal Operations & University Evaluation
            </p>
          </div>

          <div className="flex items-center gap-3 text-[11px] font-medium">
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Next.js 14</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">FastAPI</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">YOLO Vision</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Google OR-Tools</span>
          </div>
        </div>
      </footer>

      {/* How It Works Modal */}
      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
        highContrast={highContrast}
      />
    </div>
  );
}
