import React, { useState } from 'react';
import { User, Mail, BookOpen, Shield, Save, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function StudentProfile() {
  const { user, updateProfile } = useAuth();

  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [department, setDepartment] = useState(user?.department || 'Computer Science & Engineering');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    updateProfile({ name, email, department });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 text-slate-800">
      <div className="bg-white rounded-xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
        <div className="flex items-center space-x-4 border-b border-slate-200 pb-6">
          <img
            src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250'}
            alt={user?.name}
            className="w-16 h-16 rounded-full object-cover ring-2 ring-slate-200"
          />
          <div>
            <h2 className="text-xl font-bold text-slate-900">{user?.name}</h2>
            <p className="text-xs text-blue-700 font-bold">{user?.rollNo || 'CS2026-089'}</p>
            <p className="text-xs text-slate-500">{user?.department}</p>
          </div>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs flex items-center space-x-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Profile details updated successfully!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 rounded-md focus:bg-white focus:outline-hidden focus:border-slate-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              University Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 rounded-md focus:bg-white focus:outline-hidden focus:border-slate-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Department
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 rounded-md focus:bg-white focus:outline-hidden focus:border-slate-400"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="px-5 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md shadow-xs flex items-center space-x-2 transition-colors"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

