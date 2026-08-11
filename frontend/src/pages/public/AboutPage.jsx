import React from 'react';
import { Shield, Award, Users, CheckCircle, BookOpen, Lock } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-12 space-y-12 text-slate-100">
      <div className="text-center space-y-3">
        <span className="px-3 py-1 bg-blue-950/80 text-blue-300 border border-blue-800/80 text-xs font-semibold rounded-full uppercase tracking-wider">
          About Exam Portal
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Empowering Educational Excellence with Secure AI
        </h1>
        <p className="text-slate-400 text-sm max-w-2xl mx-auto">
          Exam Portal was created to protect academic integrity, remove administrative overhead from professors, and give students a seamless online testing experience.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
        <div className="space-y-4 text-sm text-slate-300 leading-relaxed">
          <h2 className="text-xl font-bold text-white">Built for Modern University Governance</h2>
          <p>
            Traditional examination systems struggle with remote proctoring scale, slow manual question drafting, and vulnerability to digital cheating techniques.
          </p>
          <p>
            Our engine provides a complete end-to-end framework: PDF question parsing, AI MCQ conversion, multi-modal proctoring checks (gaze tracking, tab locks, multi-person alert), and real-time rank computation.
          </p>
          <div className="pt-2 space-y-2 font-medium text-slate-200">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Zero client installation required — runs fully in modern browsers</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>FERPA & GDPR compliant data security protocols</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Instant AI analytics for department heads and faculty</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4 text-slate-100">
          <h3 className="text-base font-bold text-white border-b border-slate-800 pb-3">Core Platform Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">Exam Completion Reliability</span>
              <span className="font-bold text-blue-400">99.94%</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">Proctoring Latency</span>
              <span className="font-bold text-emerald-400">&lt; 200 ms</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">AI MCQ Conversion Time</span>
              <span className="font-bold text-indigo-400">3 Seconds / Page</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">Data Encryption</span>
              <span className="font-bold text-slate-200">256-bit AES</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
