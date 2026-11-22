'use client';

import React from 'react';
import { Trash2, CheckCircle2, TrendingDown, Radio } from 'lucide-react';

interface SummaryCardsProps {
  highContrast: boolean;
  totalSorted?: number;
  accuracyRate?: number;
  savingsPercent?: number;
  activeBinsCount?: number;
  totalBinsCount?: number;
  binsNeedingPickup?: number;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({
  highContrast,
  totalSorted = 14820,
  accuracyRate = 96.4,
  savingsPercent = 50.2,
  activeBinsCount = 12,
  totalBinsCount = 12,
  binsNeedingPickup = 6,
}) => {
  const cards = [
    {
      id: 'items-sorted',
      title: 'Total Items Sorted',
      value: totalSorted.toLocaleString(),
      subtext: '+348 items processed today',
      icon: Trash2,
      accent: 'emerald',
      badge: 'Real-time AI',
    },
    {
      id: 'accuracy',
      title: 'Recycling Accuracy',
      value: `${accuracyRate.toFixed(1)}%`,
      subtext: 'Computer vision verified',
      icon: CheckCircle2,
      accent: 'blue',
      badge: 'YOLO Model',
    },
    {
      id: 'savings',
      title: 'Fuel & Distance Saved',
      value: `${savingsPercent.toFixed(1)}%`,
      subtext: '24.4 km cut per collection run',
      icon: TrendingDown,
      accent: 'emerald',
      badge: 'OR-Tools VRP',
    },
    {
      id: 'active-bins',
      title: 'Active Smart Bins',
      value: `${activeBinsCount} / ${totalBinsCount}`,
      subtext: `${binsNeedingPickup} bins full & ready for pickup`,
      icon: Radio,
      accent: binsNeedingPickup > 0 ? 'amber' : 'emerald',
      badge: 'IoT Ultrasonic',
    },
  ];

  return (
    <section className="w-full">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.id}
              className={`p-5 rounded-2xl border transition-all duration-200 shadow-sm ${
                highContrast
                  ? 'bg-black border-2 border-yellow-400 text-white'
                  : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-md'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span
                  className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                    highContrast
                      ? 'bg-yellow-400 text-black font-bold'
                      : card.accent === 'blue'
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : card.accent === 'amber'
                      ? 'bg-amber-50 text-amber-800 border border-amber-200'
                      : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  }`}
                >
                  {card.badge}
                </span>

                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                    highContrast
                      ? 'bg-yellow-400 text-black'
                      : card.accent === 'blue'
                      ? 'bg-blue-100 text-blue-700'
                      : card.accent === 'amber'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-emerald-100 text-emerald-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              <div className="space-y-1">
                <p
                  className={`text-xs sm:text-sm font-medium ${
                    highContrast ? 'text-gray-300' : 'text-slate-500'
                  }`}
                >
                  {card.title}
                </p>
                <p
                  className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${
                    highContrast ? 'text-yellow-400' : 'text-slate-900'
                  }`}
                >
                  {card.value}
                </p>
                <p
                  className={`text-xs font-medium pt-1 ${
                    highContrast ? 'text-gray-400' : 'text-slate-600'
                  }`}
                >
                  {card.subtext}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
