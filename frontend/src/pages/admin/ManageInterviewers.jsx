import React, { useState } from 'react';
import { Search, Plus, Trash2, CheckCircle2, PauseCircle, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/common/Modal';
import { useData } from '../../context/DataContext';

export default function ManageInterviewers() {
  const { interviewers, addInterviewer, updateInterviewer, deleteInterviewer } = useData();
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [newInterviewer, setNewInterviewer] = useState({
    name: '',
    email: '',
    domain: 'Computer Science',
    department: 'Department of CSE',
    experience: '5 Years',
  });

  const handleToggleStatus = (id, currentStatus) => {
    updateInterviewer(id, {
      status: currentStatus === 'Approved' || currentStatus === 'Active' ? 'On Hold' : 'Approved'
    });
  };

  const handleDelete = (id) => {
    if (confirm('Are you sure you want to remove this faculty interviewer?')) {
      deleteInterviewer(id);
    }
  };

  const handleAddInterviewer = (e) => {
    e.preventDefault();
    if (!newInterviewer.name) return;

    addInterviewer({
      name: newInterviewer.name,
      email: newInterviewer.email || `${newInterviewer.name.toLowerCase().replace(/\s+/g, '')}@university.edu`,
      domain: newInterviewer.domain,
      department: newInterviewer.department,
      experience: newInterviewer.experience,
      status: 'Approved',
      examsCreated: 0,
      rating: '5.0/5',
    });

    setNewInterviewer({
      name: '',
      email: '',
      domain: 'Computer Science',
      department: 'Department of CSE',
      experience: '5 Years',
    });
    setModalOpen(false);
  };

  const filtered = interviewers.filter(
    (i) =>
      (i.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (i.domain || '').toLowerCase().includes(search.toLowerCase()) ||
      (i.department || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Faculty Interviewers & Examiners</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Governance of assigned domain leads, question paper approval rights, and faculty credentials.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search faculty name..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-60 shadow-xs"
            />
          </div>

          <button
            onClick={() => setModalOpen(true)}
            className="px-3.5 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs transition-colors flex items-center space-x-1.5 shrink-0"
          >
            <Plus className="w-4 h-4 text-blue-400" />
            <span>Add Interviewer</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No interviewers found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No faculty examiners match your search query.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Faculty Name</th>
                  <th className="py-3.5 px-4">Assigned Domain</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4 text-center">Exams Created</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((i) => (
                  <tr key={i.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{i.name}</div>
                      <div className="text-[11px] text-slate-400">{i.email}</div>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-blue-700">{i.domain}</td>
                    <td className="py-3.5 px-4 text-slate-500">{i.department || 'Computer Science'}</td>
                    <td className="py-3.5 px-4 text-center font-bold text-slate-800">{i.examsCreated || 0}</td>
                    <td className="py-3.5 px-4">
                      <Badge variant={i.status === 'Approved' || i.status === 'Active' ? 'emerald' : 'amber'}>
                        {i.status}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleToggleStatus(i.id, i.status)}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-medium rounded-md text-xs transition-colors flex items-center space-x-1"
                        >
                          {i.status === 'Approved' || i.status === 'Active' ? (
                            <>
                              <PauseCircle className="w-3.5 h-3.5 text-amber-600" />
                              <span>Hold</span>
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              <span>Approve</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(i.id)}
                          className="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
                          title="Delete Faculty"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modalOpen && (
        <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Add Faculty Interviewer">
          <form onSubmit={handleAddInterviewer} className="space-y-4 text-xs text-slate-800">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Faculty Full Name</label>
              <input
                type="text"
                required
                value={newInterviewer.name}
                onChange={(e) => setNewInterviewer({ ...newInterviewer, name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
                placeholder="Dr. Harish Kumar"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">University Email</label>
              <input
                type="email"
                value={newInterviewer.email}
                onChange={(e) => setNewInterviewer({ ...newInterviewer, email: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
                placeholder="harish.k@university.edu"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Assigned Domain</label>
              <input
                type="text"
                value={newInterviewer.domain}
                onChange={(e) => setNewInterviewer({ ...newInterviewer, domain: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="px-3.5 py-1.5 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-md font-medium"
              >
                Cancel
              </button>
              <button type="submit" className="px-4 py-1.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium rounded-md shadow-xs">
                Add Faculty
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

