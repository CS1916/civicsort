'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { SmartBin, DepotLocation, RoutePoint } from '../types';

interface RouteMapLeafletProps {
  depot: DepotLocation;
  bins: SmartBin[];
  activeRoutePoints: RoutePoint[];
  routeType: 'standard' | 'smart';
  highContrast: boolean;
  onSelectBin?: (bin: SmartBin) => void;
}

// Helper to create custom SVG div icons for Leaflet
function createBinPin(fillLevel: number, code: string, highContrast: boolean) {
  let color = '#059669'; // Green (< 40%)
  let statusText = 'Empty';
  let badgeBg = '#ECFDF5';
  let textColor = '#065F46';

  if (fillLevel >= 75) {
    color = '#DC2626'; // Red (Needs Pickup)
    statusText = 'FULL';
    badgeBg = '#FEF2F2';
    textColor = '#991B1B';
  } else if (fillLevel >= 40) {
    color = '#D97706'; // Yellow (Half-full)
    statusText = 'Half';
    badgeBg = '#FFFBEB';
    textColor = '#92400E';
  }

  if (highContrast) {
    color = fillLevel >= 75 ? '#FF4444' : fillLevel >= 40 ? '#FFBB00' : '#00FF66';
  }

  const html = `
    <div style="
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transform: translate(-50%, -100%);
    ">
      <div style="
        background: ${color};
        color: white;
        padding: 3px 6px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 800;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
        border: 2px solid white;
        display: flex;
        align-items: center;
        gap: 3px;
        white-space: nowrap;
      ">
        <span>${fillLevel}%</span>
      </div>
      <div style="
        width: 14px;
        height: 14px;
        background: ${color};
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        margin-top: -3px;
      "></div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-bin-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 36],
    popupAnchor: [0, -32],
  });
}

function createDepotPin(name: string, highContrast: boolean) {
  const bg = highContrast ? '#FFD700' : '#0F172A';
  const text = highContrast ? '#000000' : '#FFFFFF';

  const html = `
    <div style="
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transform: translate(-50%, -100%);
    ">
      <div style="
        background: ${bg};
        color: ${text};
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        box-shadow: 0 4px 8px rgba(0,0,0,0.35);
        border: 2px solid white;
        display: flex;
        align-items: center;
        gap: 4px;
      ">
        🏢 <span>Depot HQ</span>
      </div>
      <div style="
        width: 12px;
        height: 12px;
        background: ${bg};
        transform: rotate(45deg);
        margin-top: -6px;
        border: 2px solid white;
        border-top: none;
        border-left: none;
      "></div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-depot-marker',
    iconSize: [60, 40],
    iconAnchor: [30, 36],
    popupAnchor: [0, -30],
  });
}

function createTruckPin() {
  const html = `
    <div style="
      background: #059669;
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      border: 3px solid white;
      box-shadow: 0 4px 10px rgba(0,0,0,0.35);
      animation: pulse 2s infinite;
      transform: translate(-50%, -50%);
    ">
      🚚
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-truck-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

// Recenter map helper when route changes
function RouteBoundsWatcher({ points }: { points: RoutePoint[] }) {
  const map = useMap();
  useEffect(() => {
    if (points && points.length > 0) {
      const latLngs = points.map((p) => [p.lat, p.lng] as [number, number]);
      const bounds = L.latLngBounds(latLngs);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    }
  }, [points, map]);
  return null;
}

export const RouteMapLeaflet: React.FC<RouteMapLeafletProps> = ({
  depot,
  bins,
  activeRoutePoints,
  routeType,
  highContrast,
  onSelectBin,
}) => {
  const [truckIndex, setTruckIndex] = useState<number>(0);

  // Animated truck along route waypoints
  useEffect(() => {
    if (!activeRoutePoints || activeRoutePoints.length === 0) return;
    setTruckIndex(0);
    const interval = setInterval(() => {
      setTruckIndex((prev) => (prev + 1) % activeRoutePoints.length);
    }, 2200);
    return () => clearInterval(interval);
  }, [activeRoutePoints]);

  const polylineCoordinates = activeRoutePoints.map((p) => [p.lat, p.lng] as [number, number]);
  const truckLocation = activeRoutePoints[truckIndex] || activeRoutePoints[0];

  return (
    <div className="w-full h-full min-h-[420px] rounded-2xl overflow-hidden relative">
      <MapContainer
        center={[depot.lat, depot.lng]}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
        style={{ height: '100%', minHeight: '420px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url={
            highContrast
              ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
              : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
          }
          subdomains="abcd"
        />

        <RouteBoundsWatcher points={activeRoutePoints} />

        {/* Collection Route Line */}
        {polylineCoordinates.length > 1 && (
          <Polyline
            positions={polylineCoordinates}
            pathOptions={{
              color: routeType === 'smart' ? '#059669' : '#3B82F6',
              weight: routeType === 'smart' ? 5 : 4,
              opacity: 0.85,
              dashArray: routeType === 'smart' ? undefined : '8, 8',
            }}
          />
        )}

        {/* Central Depot Marker */}
        <Marker
          position={[depot.lat, depot.lng]}
          icon={createDepotPin(depot.name, highContrast)}
        >
          <Popup>
            <div className="p-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Logistics Base
              </span>
              <p className="font-bold text-sm text-slate-900">{depot.name}</p>
              <p className="text-xs text-slate-600">{depot.address}</p>
              <div className="mt-1.5 pt-1.5 border-t border-slate-200 text-[11px] text-emerald-700 font-semibold">
                Fleet Starting & Return Point
              </div>
            </div>
          </Popup>
        </Marker>

        {/* Smart Bins Markers */}
        {bins.map((bin) => {
          const isVisitedInActiveRoute = activeRoutePoints.some((p) => p.binId === bin.id);

          return (
            <Marker
              key={bin.id}
              position={[bin.lat, bin.lng]}
              icon={createBinPin(bin.fillLevel, bin.code, highContrast)}
              eventHandlers={{
                click: () => onSelectBin && onSelectBin(bin),
              }}
            >
              <Popup>
                <div className="p-1 min-w-[180px]">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-mono text-xs font-bold text-slate-700">
                      {bin.code}
                    </span>
                    <span
                      className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded ${
                        bin.fillLevel >= 75
                          ? 'bg-red-100 text-red-800'
                          : bin.fillLevel >= 40
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {bin.fillLevel >= 75
                        ? 'PICKUP REQUIRED'
                        : bin.fillLevel >= 40
                        ? 'HALF FULL'
                        : 'CAPACITY OK'}
                    </span>
                  </div>

                  <p className="font-semibold text-sm text-slate-900">{bin.name}</p>
                  <p className="text-xs text-slate-500 mb-2">{bin.address}</p>

                  <div className="space-y-1 text-xs border-t pt-1.5 border-slate-200">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Current Fill:</span>
                      <span className="font-bold text-slate-800">{bin.fillLevel}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Waste Type:</span>
                      <span className="font-medium capitalize text-slate-700">
                        {bin.category}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">In Current Route:</span>
                      <span
                        className={`font-bold ${
                          isVisitedInActiveRoute ? 'text-emerald-600' : 'text-slate-400'
                        }`}
                      >
                        {isVisitedInActiveRoute ? 'YES (Scheduled)' : 'Skipped (Not full)'}
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Animated Truck Marker */}
        {truckLocation && (
          <Marker
            position={[truckLocation.lat, truckLocation.lng]}
            icon={createTruckPin()}
          >
            <Popup>
              <div className="text-xs font-semibold text-slate-800">
                🚚 Collection Truck En Route
                <br />
                <span className="text-slate-500 font-normal">
                  Heading to: {truckLocation.name || 'Next Waypoint'}
                </span>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default RouteMapLeaflet;
