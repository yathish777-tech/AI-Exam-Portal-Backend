import React, { useState } from 'react';
import { BarChart3, FileText, Download, Award, Search, Filter } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function InterviewerReports() {
  const { completedInterviews } = useData();
  const [search, setSearch] = useState('');

  const filtered = completedInterviews.filter(
    (item) =>
      (item.studentName || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.company || item.domain || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Domain Assessment & Evaluation Reports</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Statistical performance summaries, score distributions, and AI integrity verification records.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search candidate..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-60 shadow-xs"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No completed assessments logged yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Student Candidate</th>
                  <th className="py-3.5 px-4">Examination Paper</th>
                  <th className="py-3.5 px-4 text-center">Score</th>
                  <th className="py-3.5 px-4 text-center">Integrity Status</th>
                  <th className="py-3.5 px-4 text-right">Completion Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      {item.studentName || 'Aarav Sharma'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {item.company || item.domain || 'Data Structures Exam'}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-emerald-700">
                      {item.marks}/100
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {item.warnings > 0 ? `${item.warnings} Warnings` : 'Clean Session'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right text-slate-500 font-mono text-[11px]">
                      {item.date || '2026-08-08'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
