import React, { useState } from 'react';
import { Search, Plus, Trash2, PauseCircle, CheckCircle2, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/common/Modal';
import { useData } from '../../context/DataContext';

export default function ManageStudents() {
  const { students, addStudent, updateStudent, deleteStudent } = useData();
  const [search, setSearch] = useState('');

  // Add Student modal
  const [modalOpen, setModalOpen] = useState(false);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', rollNo: '', department: 'Computer Science' });

  const handleToggleStatus = (id, currentStatus) => {
    updateStudent(id, {
      status: currentStatus === 'Approved' || currentStatus === 'Active' ? 'Suspended' : 'Approved'
    });
  };

  const handleDelete = (id) => {
    if (confirm('Are you sure you want to delete this student profile?')) {
      deleteStudent(id);
    }
  };

  const handleAddStudent = (e) => {
    e.preventDefault();
    if (!newStudent.name || !newStudent.email) return;

    addStudent({
      name: newStudent.name,
      email: newStudent.email,
      rollNo: newStudent.rollNo || `REG-${Math.floor(1000 + Math.random() * 9000)}`,
      department: newStudent.department,
      status: 'Approved',
      examsTaken: 0,
      avgScore: 'N/A',
      warnings: 0,
    });

    setNewStudent({ name: '', email: '', rollNo: '', department: 'Computer Science' });
    setModalOpen(false);
  };

  const filtered = students.filter(
    (s) =>
      (s.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.email || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.department || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.rollNo || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">University Students Directory</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage student enrollments, exam permissions, and suspension flags.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search student or email..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-blue-500 w-full sm:w-60 shadow-xs"
            />
          </div>

          <button
            onClick={() => setModalOpen(true)}
            className="px-3.5 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs transition-colors flex items-center space-x-1.5 shrink-0"
          >
            <Plus className="w-4 h-4 text-blue-400" />
            <span>Add Student</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No students found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No registered students match your search criteria.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Student Name</th>
                  <th className="py-3.5 px-4">Roll Number</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4 text-center">Exams Taken</th>
                  <th className="py-3.5 px-4 text-center">Warnings</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{s.name}</div>
                      <div className="text-[11px] text-slate-400">{s.email}</div>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-600">{s.rollNo || 'REG-PENDING'}</td>
                    <td className="py-3.5 px-4 text-slate-500">{s.department || 'Engineering'}</td>
                    <td className="py-3.5 px-4 text-center font-bold text-slate-800">{s.examsTaken || 0}</td>
                    <td className="py-3.5 px-4 text-center font-bold text-amber-600">{s.warnings || 0}</td>
                    <td className="py-3.5 px-4">
                      <Badge variant={s.status === 'Approved' || s.status === 'Active' ? 'emerald' : 'rose'}>
                        {s.status}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleToggleStatus(s.id, s.status)}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-medium rounded-md text-xs transition-colors flex items-center space-x-1"
                        >
                          {s.status === 'Approved' || s.status === 'Active' ? (
                            <>
                              <PauseCircle className="w-3.5 h-3.5 text-rose-600" />
                              <span>Suspend</span>
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              <span>Activate</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(s.id)}
                          className="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
                          title="Delete Student"
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
        <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Register New Student">
          <form onSubmit={handleAddStudent} className="space-y-4 text-xs text-slate-800">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={newStudent.name}
                onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
                placeholder="e.g. Meera Iyer"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">University Email</label>
              <input
                type="email"
                required
                value={newStudent.email}
                onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
                placeholder="meera@university.edu"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Roll Number</label>
              <input
                type="text"
                value={newStudent.rollNo}
                onChange={(e) => setNewStudent({ ...newStudent, rollNo: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
                placeholder="21CS104"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Department</label>
              <input
                type="text"
                value={newStudent.department}
                onChange={(e) => setNewStudent({ ...newStudent, department: e.target.value })}
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
                Add Student
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

