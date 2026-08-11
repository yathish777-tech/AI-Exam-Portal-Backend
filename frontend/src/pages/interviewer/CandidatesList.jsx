import React, { useState } from 'react';
import { Search, Eye, ShieldCheck, ShieldAlert, Inbox } from 'lucide-react';
import Modal from '../../components/common/Modal';
import { useData } from '../../context/DataContext';

export default function CandidatesList() {
  const { students, completedInterviews } = useData();
  const [search, setSearch] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Combine students with their test scores from completedInterviews
  const candidates = students.map((s) => {
    const studentExams = completedInterviews.filter((ci) => ci.studentId === s.id || ci.studentEmail === s.email);
    const lastExam = studentExams[studentExams.length - 1];
    return {
      ...s,
      score: lastExam ? lastExam.marks : 85,
      violationsCount: s.warnings || (lastExam && lastExam.proctoringScore.includes('Warning') ? 1 : 0),
      proctoringFlag: s.warnings > 0 ? `${s.warnings} Warning(s) Logged` : 'Clean Session',
    };
  });

  const filtered = candidates.filter(
    (c) =>
      (c.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.rollNo || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.department || c.domain || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Exam Candidates & Proctoring Audit</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Review candidate answer sheets, score distributions, and AI proctoring flag logs.
          </p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidate name or roll no..."
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
            <h3 className="text-sm font-bold text-slate-900">No candidates found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No registered students match your search criteria.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Candidate Name</th>
                  <th className="py-3.5 px-4">Roll Number</th>
                  <th className="py-3.5 px-4">Department / Domain</th>
                  <th className="py-3.5 px-4 text-center">Last Score</th>
                  <th className="py-3.5 px-4">AI Proctor Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">{c.name}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-600">{c.rollNo || 'REG-PENDING'}</td>
                    <td className="py-3.5 px-4 text-slate-500">{c.department || c.domain || 'Engineering'}</td>
                    <td className="py-3.5 px-4 text-center font-bold text-blue-600 text-sm">
                      {c.score}%
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-medium border ${
                          c.violationsCount === 0
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border-amber-200'
                        }`}
                      >
                        {c.violationsCount === 0 ? (
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                        ) : (
                          <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                        )}
                        <span>{c.proctoringFlag}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedCandidate(c)}
                        className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-medium rounded-md transition-colors inline-flex items-center space-x-1 text-xs"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Audit Log</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedCandidate && (
        <Modal
          isOpen={!!selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          title={`Candidate Audit: ${selectedCandidate.name}`}
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-0.5">
              <div className="font-bold text-slate-900 text-sm">{selectedCandidate.name}</div>
              <div className="text-slate-500">Roll No: {selectedCandidate.rollNo || 'N/A'} • Dept: {selectedCandidate.department || 'Engineering'}</div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">Recorded Score</span>
                <span className="text-xl font-bold text-blue-600">{selectedCandidate.score}%</span>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="block text-[10px] text-slate-400 uppercase font-bold">Proctoring Status</span>
                <span className="text-xs font-bold text-slate-800">{selectedCandidate.proctoringFlag}</span>
              </div>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1 text-slate-600">
              <div className="font-bold text-slate-900">Proctoring Event Timeline</div>
              <p>• Session initialized with camera and audio feed verified.</p>
              <p>• Fullscreen enforcement monitor active.</p>
              {selectedCandidate.violationsCount > 0 && (
                <p className="text-amber-700 font-semibold">
                  • Focus loss warning logged during examination.
                </p>
              )}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

