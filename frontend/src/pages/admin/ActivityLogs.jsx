import React, { useState } from 'react';
import { Activity, Search, RefreshCw } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/common/Avatar';
import { useData } from '../../context/DataContext';

export default function ActivityLogs() {
  const { activityLogs } = useData();
  const [search, setSearch] = useState('');

  const filtered = activityLogs.filter(
    (a) =>
      (a.user || '').toLowerCase().includes(search.toLowerCase()) ||
      (a.type || '').toLowerCase().includes(search.toLowerCase()) ||
      (a.description || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">System Audit & Activity Logs</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable university examination audit trail and event recordings.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audit trail..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-60 shadow-xs"
            />
          </div>
        </div>
      </div>

      {/* Activity Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-4">Event Type</th>
                <th className="py-3.5 px-4">Initiated By</th>
                <th className="py-3.5 px-4">Role</th>
                <th className="py-3.5 px-4">Action Details</th>
                <th className="py-3.5 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {filtered.map((act) => (
                <tr key={act.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    {act.type}
                  </td>
                  <td className="py-3.5 px-4 font-medium text-slate-800">
                    <div className="flex items-center space-x-2">
                      <Avatar name={act.user} size="xs" />
                      <span>{act.user}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 capitalize">
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[10px] font-medium">
                      {act.role}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">
                    {act.description}
                  </td>
                  <td className="py-3.5 px-4 text-right text-slate-400 font-mono text-[11px]">
                    {act.timestamp}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
