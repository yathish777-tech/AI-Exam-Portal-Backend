import React, { useState } from 'react';
import { Shield, Eye, AlertTriangle, CheckCircle2, User, Users, Search, RefreshCw } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import { useData } from '../../context/DataContext';

export default function LiveMonitoring() {
  const { students } = useData();
  const [search, setSearch] = useState('');

  // Real-time simulated proctored test session candidates
  const activeCandidates = [
    {
      id: 'c1',
      name: 'Aarav Sharma',
      rollNo: '2026-CS-042',
      exam: 'Advanced Data Structures Final',
      status: 'Normal',
      faceStatus: 'Face Detected',
      warnings: 0,
      focusScore: '98%',
      lastFlag: 'None',
      cameraOn: true,
    },
    {
      id: 'c2',
      name: 'Diya Patel',
      rollNo: '2026-CS-018',
      exam: 'Advanced Data Structures Final',
      status: 'Warning',
      faceStatus: 'Looking Away (2s)',
      warnings: 1,
      focusScore: '89%',
      lastFlag: 'Focus shifted away from camera',
      cameraOn: true,
    },
    {
      id: 'c3',
      name: 'Rohan Verma',
      rollNo: '2026-CS-089',
      exam: 'Advanced Data Structures Final',
      status: 'Flagged',
      faceStatus: 'Multiple Faces Detected',
      warnings: 2,
      focusScore: '74%',
      lastFlag: 'Second person in background',
      cameraOn: true,
    },
    {
      id: 'c4',
      name: 'Ananya Deshmukh',
      rollNo: '2026-CS-055',
      exam: 'Advanced Data Structures Final',
      status: 'Normal',
      faceStatus: 'Face Detected',
      warnings: 0,
      focusScore: '96%',
      lastFlag: 'None',
      cameraOn: true,
    },
  ];

  const filtered = activeCandidates.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.rollNo.toLowerCase().includes(search.toLowerCase()) ||
      c.exam.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>Live Stream Active (100+ Concurrent Nodes Supported)</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Examiner Live Proctoring Monitor</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time multi-candidate AI proctor stream inspection, face status verification, and instant flag controls.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search active candidate..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-60 shadow-xs"
            />
          </div>
        </div>
      </div>

      {/* Grid of Candidate Video Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filtered.map((candidate) => (
          <div
            key={candidate.id}
            className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col justify-between"
          >
            {/* Top Stream Window Preview */}
            <div className="relative bg-slate-900 aspect-video flex items-center justify-center p-3 text-center">
              <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center">
                <User className="w-6 h-6" />
              </div>

              {/* Status Overlay */}
              <div className="absolute top-2 left-2 flex items-center space-x-1.5 px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-xs text-[10px] font-mono text-white border border-slate-700">
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    candidate.status === 'Normal'
                      ? 'bg-emerald-400'
                      : candidate.status === 'Warning'
                      ? 'bg-amber-400 animate-pulse'
                      : 'bg-rose-400 animate-ping'
                  }`}
                />
                <span>{candidate.faceStatus}</span>
              </div>

              {/* Warnings Pill */}
              <div className="absolute top-2 right-2">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    candidate.warnings === 0
                      ? 'bg-emerald-900/80 text-emerald-200 border border-emerald-700'
                      : candidate.warnings === 1
                      ? 'bg-amber-900/80 text-amber-200 border border-amber-700'
                      : 'bg-rose-900/80 text-rose-200 border border-rose-700'
                  }`}
                >
                  Warn: {candidate.warnings}/3
                </span>
              </div>
            </div>

            {/* Candidate Metadata */}
            <div className="p-4 space-y-2 text-xs flex-1 flex flex-col justify-between">
              <div>
                <div className="font-bold text-slate-900">{candidate.name}</div>
                <div className="text-[11px] text-slate-400 font-mono">{candidate.rollNo}</div>
              </div>

              <div className="pt-2 border-t border-slate-100 text-[11px] space-y-1 text-slate-600">
                <div className="flex justify-between">
                  <span>Focus Integrity:</span>
                  <span className="font-semibold text-slate-800">{candidate.focusScore}</span>
                </div>
                <div className="flex justify-between text-rose-700 font-medium">
                  <span>Last Flag:</span>
                  <span className="truncate max-w-[120px]">{candidate.lastFlag}</span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    candidate.status === 'Normal'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : candidate.status === 'Warning'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}
                >
                  {candidate.status} State
                </span>

                <button
                  type="button"
                  className="text-[11px] font-semibold text-emerald-700 hover:text-emerald-800 underline"
                >
                  Inspect Log
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
