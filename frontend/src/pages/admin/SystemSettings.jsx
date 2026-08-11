import React, { useState } from 'react';
import { Save, CheckCircle2 } from 'lucide-react';

export default function SystemSettings() {
  const [saved, setSaved] = useState(false);
  const [strictness, setStrictness] = useState('High');
  const [maxWarnings, setMaxWarnings] = useState('3');
  const [examDuration, setExamDuration] = useState('45');
  const [fullscreenLock, setFullscreenLock] = useState(true);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
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
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>System configuration saved successfully!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">
              AI Proctor Sensitivity Level
            </label>
            <select
              value={strictness}
              onChange={(e) => setStrictness(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md font-medium focus:outline-hidden focus:border-blue-500"
            >
              <option value="High">High Strictness (University Semester Exams)</option>
              <option value="Medium">Medium Strictness (Class Quizzes)</option>
              <option value="Low">Low Strictness (Practice Mock Tests)</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">
              Max Warning Limit Before Auto-Submit
            </label>
            <input
              type="number"
              value={maxWarnings}
              onChange={(e) => setMaxWarnings(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md font-medium focus:outline-hidden focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">
              Default Exam Duration (Minutes)
            </label>
            <input
              type="number"
              value={examDuration}
              onChange={(e) => setExamDuration(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md font-medium focus:outline-hidden focus:border-blue-500"
            />
          </div>

          <div className="flex items-center space-x-3 p-3 bg-slate-50 rounded-md border border-slate-200">
            <input
              type="checkbox"
              id="fullscreen-lock"
              checked={fullscreenLock}
              onChange={(e) => setFullscreenLock(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded-md border-slate-300"
            />
            <label htmlFor="fullscreen-lock" className="font-medium text-slate-800 cursor-pointer">
              Enforce strict full-screen browser lock during active test
            </label>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="px-4 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md shadow-xs flex items-center space-x-2 transition-colors"
            >
              <Save className="w-4 h-4 text-blue-400" />
              <span>Save Governance Settings</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

