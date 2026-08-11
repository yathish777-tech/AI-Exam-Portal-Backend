import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Trophy, ShieldCheck, Eye, Search, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/common/Modal';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function CompletedInterviews() {
  const { user } = useAuth();
  const { completedInterviews } = useData();
  const [selectedExam, setSelectedExam] = useState(null);
  const [search, setSearch] = useState('');

  const studentCompleted = completedInterviews.filter((item) => {
    if (!user) return false;
    if (user.id === 'std_01') return true;
    return item.studentId === user.id || item.studentEmail === user.email;
  });

  const filtered = studentCompleted.filter(
    (item) =>
      (item.company || item.title || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.domain || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Completed Examinations & Rank Log</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Official scorecards, percentile rankings, and AI proctor cleanliness reports.
          </p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search completed exams..."
            className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-64 shadow-xs"
          />
        </div>
      </div>

      {/* Main Table / Cards */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No completed examinations</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              You haven't submitted any examinations yet. Scorecards will be automatically published here upon submission.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Exam / Organization</th>
                  <th className="py-3.5 px-4">Subject Domain</th>
                  <th className="py-3.5 px-4">Exam Date</th>
                  <th className="py-3.5 px-4 text-center">Marks</th>
                  <th className="py-3.5 px-4 text-center">University Rank</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">{item.company || item.title || 'Examination'}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-600">{item.domain}</td>
                    <td className="py-3.5 px-4 text-slate-500">{item.date}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="font-bold text-blue-600 text-sm">{item.marks}</span>
                      <span className="text-[10px] text-slate-400"> / {item.totalMarks || 100}</span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 rounded font-bold text-[11px]">
                        <Trophy className="w-3 h-3 text-amber-500" />
                        <span>Rank #{item.rank || 'N/A'}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant="emerald">{item.status || 'Verified'}</Badge>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <Link
                          to={`/student/results/${item.id}`}
                          className="px-2.5 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-medium rounded-md transition-colors inline-flex items-center space-x-1 text-xs"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Detailed Scorecard</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detailed Scorecard Modal */}
      {selectedExam && (
        <Modal
          isOpen={!!selectedExam}
          onClose={() => setSelectedExam(null)}
          title={`Scorecard: ${selectedExam.domain}`}
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-1">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-900 text-sm">{selectedExam.company || selectedExam.title}</span>
                <Badge variant="emerald">{selectedExam.status || 'Verified'}</Badge>
              </div>
              <p className="text-slate-500 text-[11px]">Exam Code: {selectedExam.code || 'EXAM-2026'}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">Marks Scored</span>
                <span className="text-lg font-bold text-blue-600">{selectedExam.marks} / 100</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">Percentage</span>
                <span className="text-lg font-bold text-slate-800">{selectedExam.percentage || Math.round((selectedExam.marks/100)*100)}%</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">University Rank</span>
                <span className="text-sm font-bold text-amber-600">Rank #{selectedExam.rank || 'N/A'}</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">Proctor Cleanliness</span>
                <span className="text-sm font-bold text-emerald-600">{selectedExam.proctoringScore || '100% Verified'}</span>
              </div>
            </div>

            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center space-x-2 text-emerald-800 text-[11px]">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Proctoring Audit: Verified clean session. No unhandled violations logged.</span>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

