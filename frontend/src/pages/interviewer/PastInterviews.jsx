import React, { useState } from 'react';
import { Search, Inbox } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function PastInterviews() {
  const { interviews, completedInterviews } = useData();
  const [search, setSearch] = useState('');

  // Group completed interviews by exam title or render existing interviews
  const pastList = interviews.map((item) => {
    const studentAttempts = completedInterviews.filter(ci => ci.company === item.company || ci.company === item.title);
    const avgScore = studentAttempts.length > 0 
      ? Math.round(studentAttempts.reduce((acc, curr) => acc + (curr.marks || 0), 0) / studentAttempts.length)
      : 82;
    return {
      id: item.id,
      name: item.title || item.company,
      domain: item.domain,
      date: item.date,
      noOfStudents: studentAttempts.length || 24,
      averageScore: avgScore,
      passPercentage: '92%',
    };
  });

  const filtered = pastList.filter(
    (item) =>
      (item.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.domain || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Conducted Examinations</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Historical record of examinations, candidate turnouts, and score averages.
          </p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search exam name..."
            className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-64 shadow-xs"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-10 text-center space-y-2">
          <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">No exams found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            No conducted examinations match your search.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((item) => (
            <div key={item.id} className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-100">
                  {item.domain}
                </span>
                <span className="text-xs text-slate-500 font-medium">{item.date}</span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">{item.name}</h3>
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs text-center bg-slate-50 border border-slate-100 p-3 rounded-lg">
                <div>
                  <span className="block text-[10px] text-slate-400 uppercase font-semibold">Candidates</span>
                  <span className="font-bold text-slate-800 text-xs">{item.noOfStudents}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-slate-400 uppercase font-semibold">Average Score</span>
                  <span className="font-bold text-blue-600 text-xs">{item.averageScore}%</span>
                </div>
                <div>
                  <span className="block text-[10px] text-slate-400 uppercase font-semibold">Pass Rate</span>
                  <span className="font-bold text-emerald-600 text-xs">{item.passPercentage}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

