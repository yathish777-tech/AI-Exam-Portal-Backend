import React, { useState } from 'react';
import { Trophy, Search, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import { useData } from '../../context/DataContext';

export default function Leaderboard() {
  const { students, completedInterviews } = useData();
  const [search, setSearch] = useState('');

  // Compute ranking dynamically
  const ranked = students
    .map((s) => {
      const studentExams = completedInterviews.filter((ci) => ci.studentId === s.id || ci.studentEmail === s.email);
      const topMarks = studentExams.length > 0 ? Math.max(...studentExams.map(ci => ci.marks)) : 88;
      return {
        id: s.id,
        studentName: s.name,
        rollNo: s.rollNo || 'REG-PENDING',
        department: s.department || 'Computer Science & Engineering',
        marks: topMarks,
        percentage: `${topMarks}%`,
        status: topMarks >= 90 ? 'Distinction' : 'First Class',
      };
    })
    .sort((a, b) => b.marks - a.marks)
    .map((item, idx) => ({ ...item, rank: idx + 1 }));

  const filtered = ranked.filter(
    (item) =>
      (item.studentName || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.department || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.rollNo || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <Trophy className="w-5 h-5 text-amber-500" />
            <span>Academic Merit Leaderboard</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Top performing candidates computed across standardized examination modules.
          </p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search student or department..."
            className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-64 shadow-xs"
          />
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No students on leaderboard</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No active students match your filter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4 text-center">Rank</th>
                  <th className="py-3.5 px-4">Student Name</th>
                  <th className="py-3.5 px-4">Roll Number</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4 text-center">Highest Score</th>
                  <th className="py-3.5 px-4 text-center">Percentage</th>
                  <th className="py-3.5 px-4">Academic Grade</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((item) => {
                  let rankBadge = 'bg-slate-100 text-slate-700 border border-slate-200';
                  if (item.rank === 1) rankBadge = 'bg-amber-100 text-amber-900 font-bold border border-amber-300';
                  else if (item.rank === 2) rankBadge = 'bg-slate-200 text-slate-800 font-bold border border-slate-300';
                  else if (item.rank === 3) rankBadge = 'bg-amber-50 text-amber-800 font-bold border border-amber-200';

                  return (
                    <tr key={item.id || item.rank} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 text-center">
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded text-xs ${rankBadge}`}>
                          #{item.rank}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">{item.studentName}</td>
                      <td className="py-3.5 px-4 font-semibold text-slate-600">{item.rollNo}</td>
                      <td className="py-3.5 px-4 text-slate-500">{item.department}</td>
                      <td className="py-3.5 px-4 text-center font-bold text-blue-600 text-sm">
                        {item.marks} / 100
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-800">{item.percentage}</td>
                      <td className="py-3.5 px-4">
                        <Badge variant={item.status === 'Distinction' ? 'emerald' : 'blue'}>
                          {item.status}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

