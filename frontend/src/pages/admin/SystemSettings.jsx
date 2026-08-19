import React, { useState } from 'react';
import { Save, CheckCircle2, Sliders, Shield, AlertTriangle } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function SystemSettings() {
  const { settings, updateSettings } = useData();
  const [saved, setSaved] = useState(false);
  const [strictness, setStrictness] = useState(settings?.strictness || 'High');
  const [maxWarnings, setMaxWarnings] = useState(settings?.maxWarnings || 3);
  const [examDuration, setExamDuration] = useState(settings?.examDuration || 45);
  const [fullscreenLock, setFullscreenLock] = useState(settings?.fullscreenLock !== false);
  const [audioDetection, setAudioDetection] = useState(settings?.audioDetectionEnabled !== false);
  const [tabSwitchDetection, setTabSwitchDetection] = useState(settings?.tabSwitchDetectionEnabled !== false);

  const handleSave = (e) => {
    e.preventDefault();
    updateSettings({
      strictness,
      maxWarnings: Number(maxWarnings) || 3,
      examDuration: Number(examDuration) || 45,
      fullscreenLock,
      audioDetectionEnabled: audioDetection,
      tabSwitchDetectionEnabled: tabSwitchDetection,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 text-slate-800">
      <div className="bg-white rounded-xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">University Exam Portal Configuration</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Adjust system default examination policies, proctoring sensitivity, and warning limits.
          </p>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Governance and proctoring settings saved successfully.</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-5 text-xs">
          
          {/* Proctor Sensitivity */}
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              AI Proctor Sensitivity Level
            </label>
            <select
              value={strictness}
              onChange={(e) => setStrictness(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg font-medium focus:outline-hidden focus:border-emerald-600 focus:bg-white"
            >
              <option value="High">High Strictness (University Semester Exams & Certifications)</option>
              <option value="Medium">Medium Strictness (Continuous Internal Assessment Quizzes)</option>
              <option value="Low">Low Strictness (Practice Mock Tests)</option>
            </select>
          </div>

          {/* Max Warnings */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block font-semibold text-slate-700">
                Max Warning Limit Before Automatic Submission
              </label>
              <span className="text-[11px] text-slate-500 font-mono">Current: {maxWarnings} Warnings</span>
            </div>
            <input
              type="number"
              min="1"
              max="10"
              value={maxWarnings}
              onChange={(e) => setMaxWarnings(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg font-medium focus:outline-hidden focus:border-emerald-600 focus:bg-white"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              If a student incurs this number of face loss, tab switch, or proctoring flags, their exam is auto-submitted.
            </p>
          </div>

          {/* Exam Duration */}
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Default Standard Exam Duration (Minutes)
            </label>
            <input
              type="number"
              min="10"
              max="180"
              value={examDuration}
              onChange={(e) => setExamDuration(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg font-medium focus:outline-hidden focus:border-emerald-600 focus:bg-white"
            />
          </div>

          {/* Enforcement Toggles */}
          <div className="space-y-3 pt-2">
            <label className="block font-semibold text-slate-700">Security Enforcement Options</label>
            
            <label className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100/70 transition-colors">
              <input
                type="checkbox"
                checked={fullscreenLock}
                onChange={(e) => setFullscreenLock(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded mt-0.5 border-slate-300 focus:ring-emerald-500"
              />
              <div>
                <span className="font-semibold text-slate-800 block">Enforce Browser Full-Screen Lock</span>
                <span className="text-[11px] text-slate-500">Prompts candidate to enter full-screen mode and logs an alert if full-screen is exited.</span>
              </div>
            </label>

            <label className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100/70 transition-colors">
              <input
                type="checkbox"
                checked={tabSwitchDetection}
                onChange={(e) => setTabSwitchDetection(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded mt-0.5 border-slate-300 focus:ring-emerald-500"
              />
              <div>
                <span className="font-semibold text-slate-800 block">Track Tab Switching & Window Focus</span>
                <span className="text-[11px] text-slate-500">Listens to document visibility changes and window blur events to detect cheating attempts.</span>
              </div>
            </label>

            <label className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100/70 transition-colors">
              <input
                type="checkbox"
                checked={audioDetection}
                onChange={(e) => setAudioDetection(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded mt-0.5 border-slate-300 focus:ring-emerald-500"
              />
              <div>
                <span className="font-semibold text-slate-800 block">Microphone Voice & Noise Detection</span>
                <span className="text-[11px] text-slate-500">Flags ambient human voice activity or suspicious audio spikes during the exam session.</span>
              </div>
            </label>
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center space-x-2 transition-colors"
            >
              <Save className="w-4 h-4 text-emerald-400" />
              <span>Save System Settings</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
