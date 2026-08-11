import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, ArrowRight, ShieldCheck, Search, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function UpcomingInterviews() {
  const { user } = useAuth();
  const { interviews } = useData();
  const [search, setSearch] = useState('');

  const assigned = interviews.filter((item) => {
    if (!user) return false;
    if (user.id === 'std_01') return true;
    if (!item.assignedStudents) return false;
    return (
      item.assignedStudents.includes(user.id) ||
      item.assignedStudents.includes(user.email) ||
      item.assignedStudents.includes(user.department) ||
      item.assignedStudents.includes('ALL')
    );
  });

  const filtered = assigned.filter(
    (item) =>
      (item.company || item.title || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.domain || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.code || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Upcoming Examinations</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Registered test modules and scheduled AI proctored interview evaluations.
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter subject or domain..."
            className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-64 shadow-xs"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="bg-white rounded-xl p-10 border border-slate-200/80 shadow-xs text-center space-y-3">
          <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
            <Inbox className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">No interviews assigned</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              There are no active examination schedules assigned to your account.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                    {item.code || 'EXAM-CODE'}
                  </span>
                  <Badge variant={item.status === 'Ready' ? 'emerald' : 'amber'}>{item.status}</Badge>
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900">{item.company || item.title || 'Technical Assessment'}</h3>
                  <p className="text-xs font-medium text-slate-600 mt-0.5">Domain: {item.domain}</p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-semibold">Date</span>
                    <span className="font-semibold text-slate-800">{item.date}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-semibold">Time</span>
                    <span className="font-semibold text-slate-800">{item.time}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-semibold">Duration</span>
                    <span className="font-semibold text-slate-800">{item.duration}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-semibold">Questions</span>
                    <span className="font-semibold text-slate-800">{item.questions ? item.questions.length : 10} MCQs</span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-600 leading-relaxed bg-blue-50/60 p-2.5 rounded-lg border border-blue-100 flex items-start space-x-1.5">
                  <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <span>{item.instructions || 'Ensure camera and microphone are connected. Fullscreen lock active.'}</span>
                </p>
              </div>

              <div className="pt-2">
                <Link
                  to={`/student/ready/${item.id}`}
                  className="w-full py-2.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2"
                >
                  <span>Proceed to Proctor Pre-Check</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

