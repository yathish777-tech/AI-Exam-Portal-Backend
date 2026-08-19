import React, { useState } from 'react';
import { Search, Plus, Trash2, CheckCircle2, PauseCircle, Inbox, Mail, Send, KeyRound, Building, BookOpen, UserCheck, ShieldAlert, Check, Copy } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/common/Modal';
import Avatar from '../../components/common/Avatar';
import { useData } from '../../context/DataContext';

export default function ManageInterviewers() {
  const { interviewers, createInterviewerInvitation, toggleInterviewerStatus, deleteInterviewer } = useData();
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [invitedSuccessInfo, setInvitedSuccessInfo] = useState(null);
  const [copiedOtp, setCopiedOtp] = useState(false);

  const [newInterviewer, setNewInterviewer] = useState({
    name: '',
    email: '',
    domain: 'Artificial Intelligence & Data Science',
    organization: 'Department of Computer Science & Engineering',
  });

  const handleDelete = (id, name) => {
    if (window.confirm(`Are you sure you want to remove faculty member ${name}? This will revoke their examiner permissions.`)) {
      deleteInterviewer(id);
    }
  };

  const handleCreateInvitation = (e) => {
    e.preventDefault();
    if (!newInterviewer.name || !newInterviewer.email) return;

    const result = createInterviewerInvitation({
      name: newInterviewer.name.trim(),
      email: newInterviewer.email.trim(),
      domain: newInterviewer.domain,
      organization: newInterviewer.organization,
    });

    setInvitedSuccessInfo(result);
    setNewInterviewer({
      name: '',
      email: '',
      domain: 'Artificial Intelligence & Data Science',
      organization: 'Department of Computer Science & Engineering',
    });
  };

  const handleCopyInvitation = (otp, code) => {
    navigator.clipboard?.writeText(`Activation Code: ${code} | OTP: ${otp}`);
    setCopiedOtp(true);
    setTimeout(() => setCopiedOtp(false), 2000);
  };

  const filtered = interviewers.filter(
    (i) =>
      (i.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (i.email || '').toLowerCase().includes(search.toLowerCase()) ||
      (i.domain || '').toLowerCase().includes(search.toLowerCase()) ||
      (i.organization || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Faculty Examiners & Interviewers</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Admin governance of faculty accounts, question paper authorization rights, and invitation lifecycle.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search faculty name or email..."
              className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 w-full sm:w-64 shadow-xs"
            />
          </div>

          <button
            onClick={() => { setInvitedSuccessInfo(null); setModalOpen(true); }}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center space-x-1.5 shrink-0"
          >
            <Plus className="w-4 h-4 text-emerald-400" />
            <span>+ Create Interviewer</span>
          </button>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No interviewers found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No faculty examiners match your query. Click "+ Create Interviewer" to invite a new examiner.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Faculty Member</th>
                  <th className="py-3.5 px-4">Assigned Domain</th>
                  <th className="py-3.5 px-4">Department / Org</th>
                  <th className="py-3.5 px-4">Account Status</th>
                  <th className="py-3.5 px-4 text-center">Exams Authored</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((i) => (
                  <tr key={i.id} className="hover:bg-slate-50/70 transition-colors">
                    
                    {/* Faculty Member */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2.5">
                        <Avatar name={i.name} size="sm" />
                        <div>
                          <div className="font-bold text-slate-900">{i.name}</div>
                          <div className="text-[11px] text-slate-400 flex items-center space-x-1 mt-0.5">
                            <Mail className="w-3 h-3 text-slate-400" />
                            <span>{i.email}</span>
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Assigned Domain */}
                    <td className="py-3.5 px-4">
                      <span className="font-medium text-slate-800">{i.domain}</span>
                    </td>

                    {/* Department */}
                    <td className="py-3.5 px-4 text-slate-600">
                      <span>{i.organization || i.department || 'University Computing'}</span>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <div className="space-y-1">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            i.status === 'Active' || i.status === 'Approved'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : i.status === 'Pending Activation'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-slate-100 text-slate-600 border border-slate-200'
                          }`}
                        >
                          {i.status}
                        </span>

                        {i.status === 'Pending Activation' && i.otp && (
                          <div className="text-[10px] text-slate-500 font-mono">
                            OTP: <strong>{i.otp}</strong>
                          </div>
                        )}
                      </div>
                    </td>

                    {/* Exams */}
                    <td className="py-3.5 px-4 text-center font-bold text-slate-800">
                      {i.examsCreated || 0}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {i.status !== 'Pending Activation' && (
                          <button
                            onClick={() => toggleInterviewerStatus(i.id)}
                            className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-medium rounded-md text-xs transition-colors flex items-center space-x-1"
                            title={i.status === 'Active' ? 'Put on Hold' : 'Activate Account'}
                          >
                            {i.status === 'Active' ? (
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
                        )}

                        <button
                          onClick={() => handleDelete(i.id, i.name)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md hover:bg-rose-50 transition-colors"
                          title="Revoke and Delete Faculty Member"
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

      {/* Modal: Create & Send Interviewer Invitation */}
      {modalOpen && (
        <Modal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          title="Create Faculty Interviewer Account"
        >
          {invitedSuccessInfo ? (
            <div className="space-y-4 text-xs text-slate-800">
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2 text-center">
                <div className="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h4 className="text-sm font-bold text-emerald-950">Invitation Created & Dispatched!</h4>
                <p className="text-xs text-emerald-800">
                  An invitation has been generated for <strong>{invitedSuccessInfo.interviewer.name}</strong> ({invitedSuccessInfo.interviewer.email}).
                </p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">Account Activation Details:</span>
                  <button
                    type="button"
                    onClick={() => handleCopyInvitation(invitedSuccessInfo.otp, invitedSuccessInfo.invitationCode)}
                    className="inline-flex items-center space-x-1 text-emerald-700 hover:text-emerald-800 font-semibold"
                  >
                    {copiedOtp ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedOtp ? 'Copied!' : 'Copy Code'}</span>
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-400 block font-sans">Activation OTP</span>
                    <span className="text-emerald-800 font-bold">{invitedSuccessInfo.otp}</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-400 block font-sans">Invitation Code</span>
                    <span className="text-slate-800 font-bold">{invitedSuccessInfo.invitationCode}</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 leading-normal">
                  The faculty member can now open the <strong>Interviewer Activation Portal</strong> (<code className="bg-slate-200 px-1 py-0.5 rounded text-[10px]">/interviewer/activate</code>) and establish their permanent password.
                </p>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-lg shadow-xs"
                >
                  Done
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleCreateInvitation} className="space-y-4 text-xs text-slate-800">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-[11px] leading-relaxed">
                Interviewer credentials cannot be assigned manually. An invitation verification OTP is issued to the faculty member so they can establish their own secure password.
              </div>

              {/* Full Name */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Faculty Full Name</label>
                <input
                  type="text"
                  required
                  value={newInterviewer.name}
                  onChange={(e) => setNewInterviewer({ ...newInterviewer, name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                  placeholder="e.g. Dr. Harish Kumar"
                />
              </div>

              {/* University Email */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Institutional Email Address</label>
                <input
                  type="email"
                  required
                  value={newInterviewer.email}
                  onChange={(e) => setNewInterviewer({ ...newInterviewer, email: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                  placeholder="e.g. harish.k@university.edu"
                />
              </div>

              {/* Assigned Domain */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Assigned Domain / Subject Area</label>
                <select
                  value={newInterviewer.domain}
                  onChange={(e) => setNewInterviewer({ ...newInterviewer, domain: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                >
                  <option value="Artificial Intelligence & Data Science">Artificial Intelligence & Data Science</option>
                  <option value="Data Structures & Algorithms">Data Structures & Algorithms</option>
                  <option value="Network Security & Cryptography">Network Security & Cryptography</option>
                  <option value="Database Management Systems">Database Management Systems</option>
                  <option value="Software Architecture & Cloud Computing">Software Architecture & Cloud Computing</option>
                  <option value="Cyber Physical Systems">Cyber Physical Systems</option>
                </select>
              </div>

              {/* Organization / Department */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Organization / Academic Department</label>
                <input
                  type="text"
                  value={newInterviewer.organization}
                  onChange={(e) => setNewInterviewer({ ...newInterviewer, organization: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                  placeholder="e.g. Department of Computer Science & Engineering"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-3.5 py-2 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-lg shadow-xs flex items-center space-x-1.5 transition-colors"
                >
                  <Send className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Create & Send Invitation</span>
                </button>
              </div>
            </form>
          )}
        </Modal>
      )}

    </div>
  );
}
