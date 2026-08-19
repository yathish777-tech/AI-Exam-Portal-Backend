import React, { useState } from 'react';
import { Save, CheckCircle2, User, Mail, BookOpen, Building } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function InterviewerSettings() {
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const [name, setName] = useState(user?.name || 'Dr. Harish Kumar');
  const [email] = useState(user?.email || 'harish.k@university.edu');
  const [domain, setDomain] = useState(user?.domain || 'Data Structures & Algorithms');
  const [organization, setOrganization] = useState(user?.organization || 'Dept. of Computer Science');

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 text-slate-800">
      <div className="bg-white rounded-xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">Examiner Profile & Domain Preferences</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage your faculty examiner profile details and academic department association.
          </p>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Profile settings updated successfully.</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Institutional Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="email"
                disabled
                value={email}
                className="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 text-slate-500 rounded-lg cursor-not-allowed"
              />
            </div>
            <span className="text-[10px] text-slate-400 mt-1 block">Institutional email cannot be modified. Contact IT Admin for email updates.</span>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Assigned Domain</label>
            <div className="relative">
              <BookOpen className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Department / Organization</label>
            <div className="relative">
              <Building className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
              />
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center space-x-2 transition-colors"
            >
              <Save className="w-4 h-4 text-emerald-400" />
              <span>Save Profile</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
