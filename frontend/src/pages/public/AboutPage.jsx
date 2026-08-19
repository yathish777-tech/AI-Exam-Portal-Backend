import React from 'react';
import { Shield, Award, Users, CheckCircle, BookOpen, Lock } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-10 text-slate-800 font-sans">
      <div className="text-center space-y-2">
        <span className="px-3 py-1 bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold rounded-full uppercase tracking-wider">
          About Exam Portal
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Academic Integrity with Transparent AI Proctoring
        </h1>
        <p className="text-slate-500 text-xs sm:text-sm max-w-xl mx-auto">
          Built to protect examination integrity, streamline faculty assessment generation, and provide students a consistent, distraction-free environment.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        <div className="space-y-3 text-xs sm:text-sm text-slate-600 leading-relaxed">
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Modern University Examination Standards</h2>
          <p>
            LocalSM Exam Portal delivers an end-to-end framework: PDF question parsing, AI MCQ conversion, multi-modal proctoring checks (gaze tracking, tab locks, multi-person alert), and real-time rank computation.
          </p>
          <div className="pt-2 space-y-2 text-xs font-medium text-slate-700">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Zero client installation required — runs in standard modern web browsers</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Continuous face verification and focus deviation detection</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Immediate post-exam scoring and proctor telemetry logs</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">Core Platform Metrics</h3>
          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Session Stability</span>
              <span className="font-bold text-slate-900">99.9%</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Proctoring Telemetry Latency</span>
              <span className="font-bold text-emerald-700">&lt; 250 ms</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Concurrent Candidates</span>
              <span className="font-bold text-slate-900">100+ Nodes</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Security Encryption</span>
              <span className="font-bold text-slate-900">256-bit AES</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
