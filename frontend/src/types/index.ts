export type WasteCategory = 'organic' | 'recyclable' | 'hazardous' | 'general';

export interface BoundingBox {
  x: number; // percentage (0-100) or normalized
  y: number;
  width: number;
  height: number;
}

export interface WasteDetection {
  id: string;
  label: string;
  category: WasteCategory;
  confidence: number; // 0 to 1
  binName: string; // e.g. "BLUE Bin — Recyclable"
  binColor: 'green' | 'blue' | 'red' | 'gray';
  disposalInstruction: string;
  ecoTip: string;
  bbox?: BoundingBox;
}

export interface ClassifyResponse {
  success: boolean;
  item: WasteDetection;
  alternativeDetections?: WasteDetection[];
  processingTimeMs: number;
  timestamp: string;
}

export interface SmartBin {
  id: string;
  code: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  fillLevel: number; // 0 - 100%
  category: WasteCategory;
  capacityKg: number;
  lastUpdated: string;
  needsPickup: boolean;
}

export interface DepotLocation {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

export interface RoutePoint {
  lat: number;
  lng: number;
  binId?: string;
  name?: string;
  isDepot?: boolean;
  order: number;
  fillLevel?: number;
}

export interface RouteStats {
  totalDistanceKm: number;
  estimatedTimeMins: number;
  fuelConsumedLiters: number;
  co2EmittedKg: number;
  binsVisited: number;
  totalBinsAvailable: number;
}

export interface RouteSavings {
  distanceSavedKm: number;
  distanceSavedPercent: number;
  timeSavedMins: number;
  timeSavedPercent: number;
  fuelSavedLiters: number;
  co2SavedKg: number;
}

export interface RouteOptimizationResult {
  depot: DepotLocation;
  standardRoute: {
    points: RoutePoint[];
    stats: RouteStats;
  };
  aiSmartRoute: {
    points: RoutePoint[];
    stats: RouteStats;
  };
  savings: RouteSavings;
  lastCalculated: string;
}

export interface HistoricalComparison {
  day: string;
  standardDistanceKm: number;
  aiDistanceKm: number;
  standardFuelLiters: number;
  aiFuelLiters: number;
  standardCo2Kg: number;
  aiCo2Kg: number;
}

export interface MaterialBreakdown {
  material: string;
  itemsSorted: number;
  accuracyPercent: number;
  binColor: string;
}
