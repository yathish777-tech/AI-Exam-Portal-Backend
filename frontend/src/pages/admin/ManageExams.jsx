import React, { useState } from 'react';
import { Search, Calendar, Users, BookOpen, Trash2, CheckCircle2, Shield } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import { useData } from '../../context/DataContext';

export default function ManageExams() {
  const { interviews, deleteInterview } = useData();
  const [search, setSearch] = useState('');

  const handleDelete = (id, title) => {
    if (window.confirm(`Are you sure you want to remove exam "${title}"?`)) {
      deleteInterview(id);
    }
  };

  const filtered = interviews.filter(
    (item) =>
      (item.company || item.title || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.domain || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">University Examination Management</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Admin oversight of active exam sessions, question set assignments, and duration limits.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search exam title or domain..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-60 shadow-xs"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-4">Examination Title</th>
                <th className="py-3.5 px-4">Domain</th>
                <th className="py-3.5 px-4">Duration</th>
                <th className="py-3.5 px-4">Scheduled Date</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    {item.company || item.title}
                  </td>
                  <td className="py-3.5 px-4 font-medium text-slate-700">
                    {item.domain}
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">
                    {item.duration || '45 Mins'}
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 font-mono text-[11px]">
                    {item.date} • {item.time}
                  </td>
                  <td className="py-3.5 px-4">
                    <Badge variant={item.status === 'Ready' || item.status === 'Active' ? 'emerald' : 'blue'}>
                      {item.status}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleDelete(item.id, item.company || item.title)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md hover:bg-rose-50 transition-colors"
                      title="Delete Examination"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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
