'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Camera,
  Upload,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  X,
  RefreshCw,
  Info,
  Maximize2,
} from 'lucide-react';
import { WasteDetection } from '../types';
import { SAMPLE_WASTE_ITEMS } from '../lib/mockData';
import { classifyWasteImage } from '../lib/api';

interface WasteScannerProps {
  highContrast: boolean;
  onScanComplete?: (detection: WasteDetection) => void;
}

export const WasteScanner: React.FC<WasteScannerProps> = ({
  highContrast,
  onScanComplete,
}) => {
  const [activeMode, setActiveMode] = useState<'upload' | 'camera'>('upload');
  const [previewImage, setPreviewImage] = useState<string>(SAMPLE_WASTE_ITEMS.bottle.image);
  const [currentDetection, setCurrentDetection] = useState<WasteDetection>(SAMPLE_WASTE_ITEMS.bottle.result);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Stop camera on unmount or mode switch
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    setCameraActive(false);
  };

  const startCamera = async () => {
    setCameraError(null);
    setActiveMode('camera');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraActive(true);
    } catch (err: any) {
      console.error('Camera access error:', err);
      setCameraError('Camera access unavailable. You can upload any photo or pick a sample below!');
      setCameraActive(false);
    }
  };

  const captureCameraFrame = async () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

    setPreviewImage(dataUrl);
    stopCamera();
    setActiveMode('upload');

    await runInference(dataUrl);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      const result = event.target?.result as string;
      setPreviewImage(result);
      await runInference(file);
    };
    reader.readAsDataURL(file);
  };

  const handleSelectSample = async (sampleKey: 'bottle' | 'banana' | 'battery') => {
    stopCamera();
    setActiveMode('upload');
    const sample = SAMPLE_WASTE_ITEMS[sampleKey];
    setPreviewImage(sample.image);
    setIsScanning(true);

    try {
      const res = await classifyWasteImage(sample.image, sampleKey);
      setCurrentDetection(res.item);
      if (onScanComplete) onScanComplete(res.item);
    } finally {
      setIsScanning(false);
    }
  };

  const runInference = async (fileOrBase64: File | string) => {
    setIsScanning(true);
    try {
      const res = await classifyWasteImage(fileOrBase64);
      setCurrentDetection(res.item);
      if (onScanComplete) onScanComplete(res.item);
    } catch (err) {
      console.error('Error during classification:', err);
    } finally {
      setIsScanning(false);
    }
  };

  // Bin theme styling helpers
  const getBinStyle = (color: string) => {
    switch (color) {
      case 'green':
        return {
          bg: 'bg-emerald-600',
          lightBg: 'bg-emerald-50',
          border: 'border-emerald-500',
          text: 'text-emerald-800',
          badgeText: 'text-white',
          pillBg: 'bg-emerald-600',
          boxBorder: '#059669',
        };
      case 'blue':
        return {
          bg: 'bg-blue-600',
          lightBg: 'bg-blue-50',
          border: 'border-blue-500',
          text: 'text-blue-800',
          badgeText: 'text-white',
          pillBg: 'bg-blue-600',
          boxBorder: '#2563EB',
        };
      case 'red':
        return {
          bg: 'bg-red-600',
          lightBg: 'bg-red-50',
          border: 'border-red-500',
          text: 'text-red-800',
          badgeText: 'text-white',
          pillBg: 'bg-red-600',
          boxBorder: '#DC2626',
        };
      default:
        return {
          bg: 'bg-slate-700',
          lightBg: 'bg-slate-50',
          border: 'border-slate-500',
          text: 'text-slate-800',
          badgeText: 'text-white',
          pillBg: 'bg-slate-700',
          boxBorder: '#475569',
        };
    }
  };

  const binTheme = getBinStyle(currentDetection?.binColor || 'blue');

  return (
    <div
      className={`rounded-2xl border p-5 sm:p-6 transition-all shadow-sm flex flex-col h-full ${
        highContrast ? 'bg-black border-2 border-yellow-400 text-white' : 'bg-white border-slate-200'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <span
            className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
              highContrast ? 'bg-yellow-400 text-black' : 'bg-emerald-100 text-emerald-800'
            }`}
          >
            Module 1
          </span>
          <h2
            className={`text-lg sm:text-xl font-bold mt-1 ${
              highContrast ? 'text-white' : 'text-slate-900'
            }`}
          >
            Easy Waste Scanner
          </h2>
          <p className={`text-xs sm:text-sm ${highContrast ? 'text-gray-300' : 'text-slate-500'}`}>
            Point your camera or upload a photo for instant AI bin advice
          </p>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
          <Sparkles className="w-3.5 h-3.5" />
          <span>YOLO Vision Active</span>
        </div>
      </div>

      {/* Two Big Action Buttons */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <button
          onClick={startCamera}
          className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm transition-all shadow-sm ${
            cameraActive
              ? 'bg-emerald-600 text-white ring-2 ring-emerald-400'
              : highContrast
              ? 'bg-yellow-400 text-black hover:bg-yellow-300'
              : 'bg-slate-900 text-white hover:bg-slate-800'
          }`}
        >
          <Camera className="w-4 h-4" />
          <span>Use Live Camera</span>
        </button>

        <button
          onClick={() => {
            stopCamera();
            setActiveMode('upload');
            fileInputRef.current?.click();
          }}
          className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm border transition-all shadow-sm ${
            highContrast
              ? 'border-yellow-400 text-yellow-300 hover:bg-yellow-400/20'
              : 'border-slate-300 bg-slate-50 text-slate-800 hover:bg-slate-100'
          }`}
        >
          <Upload className="w-4 h-4 text-emerald-600" />
          <span>Upload Photo</span>
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileUpload}
        />
      </div>

      {cameraError && (
        <div className="mb-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
          <span>{cameraError}</span>
        </div>
      )}

      {/* 3 Clickable Sample Waste Photos */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <p
            className={`text-xs font-semibold uppercase tracking-wider ${
              highContrast ? 'text-yellow-400' : 'text-slate-500'
            }`}
          >
            Or Try 1-Click Sample Waste Items:
          </p>
          <span className="text-[11px] text-slate-400">Zero file needed</span>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => handleSelectSample('bottle')}
            className={`p-2 rounded-xl border text-left transition-all flex flex-col items-center gap-1.5 ${
              currentDetection?.category === 'recyclable' && !cameraActive
                ? highContrast
                  ? 'border-yellow-400 bg-yellow-400/20'
                  : 'border-blue-500 bg-blue-50/60 ring-2 ring-blue-300'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">
              🥤
            </div>
            <span
              className={`text-[11px] font-semibold text-center leading-tight line-clamp-1 ${
                highContrast ? 'text-white' : 'text-slate-800'
              }`}
            >
              Water Bottle
            </span>
            <span className="text-[10px] text-blue-600 font-medium">Recyclable</span>
          </button>

          <button
            onClick={() => handleSelectSample('banana')}
            className={`p-2 rounded-xl border text-left transition-all flex flex-col items-center gap-1.5 ${
              currentDetection?.category === 'organic' && !cameraActive
                ? highContrast
                  ? 'border-yellow-400 bg-yellow-400/20'
                  : 'border-emerald-500 bg-emerald-50/60 ring-2 ring-emerald-300'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold">
              🍌
            </div>
            <span
              className={`text-[11px] font-semibold text-center leading-tight line-clamp-1 ${
                highContrast ? 'text-white' : 'text-slate-800'
              }`}
            >
              Banana Peel
            </span>
            <span className="text-[10px] text-emerald-600 font-medium">Organic / Wet</span>
          </button>

          <button
            onClick={() => handleSelectSample('battery')}
            className={`p-2 rounded-xl border text-left transition-all flex flex-col items-center gap-1.5 ${
              currentDetection?.category === 'hazardous' && !cameraActive
                ? highContrast
                  ? 'border-yellow-400 bg-yellow-400/20'
                  : 'border-red-500 bg-red-50/60 ring-2 ring-red-300'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            <div className="w-7 h-7 rounded-lg bg-red-100 text-red-700 flex items-center justify-center text-xs font-bold">
              🔋
            </div>
            <span
              className={`text-[11px] font-semibold text-center leading-tight line-clamp-1 ${
                highContrast ? 'text-white' : 'text-slate-800'
              }`}
            >
              Battery / E-Waste
            </span>
            <span className="text-[10px] text-red-600 font-medium">Hazardous</span>
          </button>
        </div>
      </div>

      {/* Main Visual Display (Camera stream or Image with Bounding Box) */}
      <div className="relative w-full aspect-video sm:aspect-[4/3] rounded-2xl overflow-hidden bg-slate-900 border border-slate-300 shadow-inner mb-4 flex items-center justify-center">
        {cameraActive ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 pointer-events-none border-2 border-emerald-400/50 rounded-2xl flex items-center justify-center">
              <div className="w-48 h-48 border-2 border-dashed border-emerald-400 rounded-xl relative flex items-center justify-center">
                <span className="text-emerald-300 text-xs font-semibold bg-black/60 px-2 py-1 rounded">
                  Center Waste Here
                </span>
              </div>
            </div>
            <div className="absolute bottom-4 inset-x-0 flex justify-center gap-3">
              <button
                onClick={captureCameraFrame}
                className="px-5 py-2.5 rounded-full bg-emerald-600 text-white font-bold text-sm shadow-lg hover:bg-emerald-500 transition-all flex items-center gap-2"
              >
                <Camera className="w-4 h-4" />
                <span>Snap & Analyze</span>
              </button>
              <button
                onClick={stopCamera}
                className="px-3 py-2.5 rounded-full bg-slate-800/80 text-white font-medium text-xs hover:bg-slate-700 transition-all flex items-center gap-1"
              >
                <X className="w-4 h-4" />
                <span>Close</span>
              </button>
            </div>
          </>
        ) : (
          <>
            {previewImage && (
              <img
                src={previewImage}
                alt="Scanned waste"
                className="w-full h-full object-cover transition-opacity duration-300"
              />
            )}

            {/* Simulated Clean Bounding Box */}
            {currentDetection?.bbox && !isScanning && (
              <div
                style={{
                  position: 'absolute',
                  left: `${currentDetection.bbox.x}%`,
                  top: `${currentDetection.bbox.y}%`,
                  width: `${currentDetection.bbox.width}%`,
                  height: `${currentDetection.bbox.height}%`,
                  borderColor: binTheme.boxBorder,
                }}
                className="border-2 rounded-lg pointer-events-none shadow-[0_0_15px_rgba(0,0,0,0.4)] animate-pulse"
              >
                <div
                  style={{ backgroundColor: binTheme.boxBorder }}
                  className="absolute -top-3 left-2 px-2 py-0.5 rounded text-[11px] font-bold text-white shadow-sm flex items-center gap-1"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>{currentDetection.label}</span>
                </div>
              </div>
            )}

            {/* Scanning Overlay */}
            {isScanning && (
              <div className="absolute inset-0 bg-slate-900/75 backdrop-blur-xs flex flex-col items-center justify-center text-white gap-3 z-10">
                <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
                <p className="text-sm font-semibold tracking-wide">
                  Analyzing Waste Geometry & Texture...
                </p>
                <span className="text-xs text-slate-300">YOLO Model running</span>
              </div>
            )}
          </>
        )}
      </div>

      {/* Detection Results & Plain English Guidance Card */}
      {currentDetection && (
        <div className="flex-1 flex flex-col justify-between space-y-3">
          {/* Item Name & Confidence Progress Bar */}
          <div
            className={`p-3.5 rounded-xl border ${
              highContrast ? 'bg-black border-yellow-400' : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="flex items-center justify-between gap-2 mb-1.5">
              <div>
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
                  Detected Item
                </span>
                <p
                  className={`text-base font-bold ${
                    highContrast ? 'text-yellow-400' : 'text-slate-900'
                  }`}
                >
                  {currentDetection.label}
                </p>
              </div>

              <div className="text-right">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
                  AI Confidence
                </span>
                <p className="text-sm font-extrabold text-emerald-600">
                  {(currentDetection.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Simple Progress Bar */}
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="bg-emerald-600 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, currentDetection.confidence * 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Large Color-Coded Disposal Instruction Card */}
          <div
            className={`p-4 rounded-2xl border-2 transition-all ${
              highContrast
                ? 'bg-black border-yellow-400 text-white'
                : `${binTheme.lightBg} ${binTheme.border} ${binTheme.text}`
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              <div
                className={`px-3 py-1.5 rounded-xl font-extrabold text-sm flex items-center gap-2 shadow-sm ${
                  highContrast ? 'bg-yellow-400 text-black' : `${binTheme.bg} text-white`
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{currentDetection.binName}</span>
              </div>
            </div>

            <p className="text-xs sm:text-sm font-medium leading-relaxed mb-2">
              {currentDetection.disposalInstruction}
            </p>

            {/* Eco Tip */}
            <div className="flex items-start gap-2 pt-2 border-t border-slate-200/60 text-xs text-slate-600">
              <Lightbulb className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              <p className="italic">{currentDetection.ecoTip}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
