'use client';

import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { Download, FileText, CheckCircle2, TrendingUp, BarChart2, Shield } from 'lucide-react';
import { HISTORICAL_CHART_DATA, MATERIAL_STATS_DATA } from '../lib/mockData';
import { RouteOptimizationResult } from '../types';

interface PerformanceChartsProps {
  highContrast: boolean;
  routeResult: RouteOptimizationResult;
}

export const PerformanceCharts: React.FC<PerformanceChartsProps> = ({
  highContrast,
  routeResult,
}) => {
  const [downloading, setDownloading] = useState(false);

  // Generate downloadable CSV report
  const handleDownloadCsv = () => {
    setDownloading(true);

    const headers = ['Metric', 'Standard Manual Collection', 'AI Smart System', 'Net Savings / Improvement'];
    const rows = [
      ['Collection Route Distance (km)', `${routeResult.standardRoute.stats.totalDistanceKm} km`, `${routeResult.aiSmartRoute.stats.totalDistanceKm} km`, `${routeResult.savings.distanceSavedKm} km (${routeResult.savings.distanceSavedPercent}%)`],
      ['Driver & Truck Time (mins)', `${routeResult.standardRoute.stats.estimatedTimeMins} mins`, `${routeResult.aiSmartRoute.stats.estimatedTimeMins} mins`, `${routeResult.savings.timeSavedMins} mins (${routeResult.savings.timeSavedPercent}%)`],
      ['Diesel Fuel Consumed (L)', `${routeResult.standardRoute.stats.fuelConsumedLiters} L`, `${routeResult.aiSmartRoute.stats.fuelConsumedLiters} L`, `${routeResult.savings.fuelSavedLiters} L`],
      ['Carbon Emissions (kg CO2)', `${routeResult.standardRoute.stats.co2EmittedKg} kg`, `${routeResult.aiSmartRoute.stats.co2EmittedKg} kg`, `${routeResult.savings.co2SavedKg} kg CO2`],
      ['Segregation Classification Accuracy', '68.0% (Manual Sorting)', '96.4% (YOLO Vision)', '+28.4% Purity'],
      ['Active Connected Bins', '12 / 12', '12 / 12', '100% Telemetry Coverage'],
    ];

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += '=== URBAN WASTE MANAGEMENT AI BENCHMARK REPORT ===\r\n';
    csvContent += `Generated On: ${new Date().toLocaleString()}\r\n`;
    csvContent += `Depot Location: ${routeResult.depot.name} (${routeResult.depot.address})\r\n\r\n`;
    csvContent += headers.join(',') + '\r\n';

    rows.forEach((row) => {
      csvContent += row.map((cell) => `"${cell}"`).join(',') + '\r\n';
    });

    csvContent += '\r\n=== 7-DAY HISTORICAL PERFORMANCE LOG ===\r\n';
    csvContent += 'Day,Standard Distance (km),AI Smart Distance (km),Standard Fuel (L),AI Smart Fuel (L),CO2 Saved (kg)\r\n';
    HISTORICAL_CHART_DATA.forEach((d) => {
      const co2Diff = +(d.standardCo2Kg - d.aiCo2Kg).toFixed(1);
      csvContent += `${d.day},${d.standardDistanceKm},${d.aiDistanceKm},${d.standardFuelLiters},${d.aiFuelLiters},${co2Diff}\r\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Waste_AI_Evaluation_Report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => setDownloading(false), 600);
  };

  return (
    <section
      className={`rounded-2xl border p-5 sm:p-6 transition-all shadow-sm ${
        highContrast ? 'bg-black border-2 border-yellow-400 text-white' : 'bg-white border-slate-200'
      }`}
    >
      {/* Header and Download Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100">
        <div>
          <span
            className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
              highContrast ? 'bg-yellow-400 text-black' : 'bg-emerald-100 text-emerald-800'
            }`}
          >
            Module 3
          </span>
          <h2
            className={`text-lg sm:text-xl font-bold mt-1 ${
              highContrast ? 'text-white' : 'text-slate-900'
            }`}
          >
            System Performance & Municipal Impact
          </h2>
          <p className={`text-xs sm:text-sm ${highContrast ? 'text-gray-300' : 'text-slate-500'}`}>
            Side-by-side verification: Traditional manual collection vs. AI-powered intelligent system
          </p>
        </div>

        <button
          onClick={handleDownloadCsv}
          disabled={downloading}
          className={`inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs sm:text-sm transition-all shadow-sm ${
            highContrast
              ? 'bg-yellow-400 text-black hover:bg-yellow-300'
              : 'bg-emerald-600 text-white hover:bg-emerald-700'
          }`}
        >
          <Download className="w-4 h-4" />
          <span>{downloading ? 'Preparing Report...' : 'Download Simple Report (CSV)'}</span>
        </button>
      </div>

      {/* Two Clean Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Daily Route Distance Comparison */}
        <div
          className={`p-4 rounded-xl border ${
            highContrast ? 'bg-black border-yellow-400' : 'bg-slate-50/60 border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3
                className={`text-sm font-bold ${
                  highContrast ? 'text-white' : 'text-slate-900'
                }`}
              >
                Daily Fleet Route Distance (km)
              </h3>
              <p className="text-xs text-slate-500">
                Comparing standard fixed route vs. dynamic AI path
              </p>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
              ~50% Daily Cut
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={HISTORICAL_CHART_DATA}
                margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis unit="km" tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip
                  formatter={(value: any) => [`${value} km`]}
                  contentStyle={{
                    borderRadius: '8px',
                    borderColor: '#E2E8F0',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar
                  dataKey="standardDistanceKm"
                  name="Standard Fixed Route"
                  fill="#94A3B8"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="aiDistanceKm"
                  name="AI Smart Route"
                  fill="#059669"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Segregation Accuracy & Items by Material */}
        <div
          className={`p-4 rounded-xl border ${
            highContrast ? 'bg-black border-yellow-400' : 'bg-slate-50/60 border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3
                className={`text-sm font-bold ${
                  highContrast ? 'text-white' : 'text-slate-900'
                }`}
              >
                Segregation Purity & Items Sorted
              </h3>
              <p className="text-xs text-slate-500">
                AI classification accuracy across primary waste streams
              </p>
            </div>
            <span className="text-xs font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
              Avg 96.4% Accuracy
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={MATERIAL_STATS_DATA}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 35, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[80, 100]}
                  unit="%"
                  tick={{ fontSize: 12, fill: '#64748B' }}
                />
                <YAxis
                  dataKey="material"
                  type="category"
                  tick={{ fontSize: 11, fill: '#334155' }}
                  width={110}
                />
                <Tooltip
                  formatter={(value: any) => [`${value}% Accuracy`]}
                  contentStyle={{
                    borderRadius: '8px',
                    borderColor: '#E2E8F0',
                    fontSize: '12px',
                  }}
                />
                <Bar
                  dataKey="accuracyPercent"
                  name="Sorting Accuracy (%)"
                  fill="#2563EB"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
};
