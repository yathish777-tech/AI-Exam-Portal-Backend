import React, { useState } from 'react';
import { ShieldAlert, Search, Filter, AlertTriangle, Eye, ArrowUpDown } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/common/Avatar';
import { useData } from '../../context/DataContext';

export default function WarningLogs() {
  const { warningLogs } = useData();
  const [search, setSearch] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');

  const filtered = warningLogs.filter((log) => {
    const matchesSearch =
      (log.studentName || '').toLowerCase().includes(search.toLowerCase()) ||
      (log.examTitle || '').toLowerCase().includes(search.toLowerCase()) ||
      (log.type || '').toLowerCase().includes(search.toLowerCase());

    const matchesSeverity = selectedSeverity === 'ALL' || log.severity === selectedSeverity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">AI Proctoring Violation & Warning Logs</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Centralized telemetry of suspicious behaviors, face-detection losses, and browser focus flags.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search student or violation..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-60 shadow-xs"
            />
          </div>

          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-2 text-xs bg-white border border-slate-200 text-slate-800 rounded-lg shadow-xs focus:outline-hidden focus:border-emerald-600 font-medium"
          >
            <option value="ALL">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <ShieldAlert className="w-10 h-10 text-slate-300 mx-auto" />
            <h3 className="text-sm font-bold text-slate-900">No warning logs recorded</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No examination security violations match your current filters.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Student Candidate</th>
                  <th className="py-3.5 px-4">Examination Paper</th>
                  <th className="py-3.5 px-4">Violation Type</th>
                  <th className="py-3.5 px-4">Severity</th>
                  <th className="py-3.5 px-4">Timestamp</th>
                  <th className="py-3.5 px-4 text-right">Enforcement Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <div className="flex items-center space-x-2">
                        <Avatar name={log.studentName} size="xs" />
                        <span>{log.studentName}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-xs truncate">
                      {log.examTitle}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-rose-700 flex items-center space-x-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                      <span>{log.type}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          log.severity === 'Critical'
                            ? 'bg-rose-100 text-rose-800 border border-rose-200'
                            : log.severity === 'High'
                            ? 'bg-amber-100 text-amber-800 border border-amber-200'
                            : 'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}
                      >
                        {log.severity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 font-mono text-[11px]">
                      {log.timestamp}
                    </td>
                    <td className="py-3.5 px-4 text-right font-medium text-slate-700">
                      {log.actionTaken}
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
