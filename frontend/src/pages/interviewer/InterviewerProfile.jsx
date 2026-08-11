import React, { useState } from 'react';
import { User, Mail, BookOpen, Save, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function InterviewerProfile() {
  const { user, updateProfile } = useAuth();

  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [domain, setDomain] = useState(user?.domain || 'Artificial Intelligence & Data Science');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    updateProfile({ name, email, domain });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 text-slate-100">
      <div className="bg-slate-900/90 rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-md space-y-6">
        <div className="flex items-center space-x-4 border-b border-slate-800 pb-6">
          <img
            src={user?.avatar || 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=250'}
            alt={user?.name}
            className="w-16 h-16 rounded-2xl object-cover ring-4 ring-indigo-500/30"
          />
          <div>
            <h2 className="text-xl font-bold text-white">{user?.name}</h2>
            <p className="text-xs text-indigo-400 font-semibold">{user?.domain}</p>
            <p className="text-xs text-slate-400">{user?.department}</p>
          </div>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-950/80 border border-emerald-800 text-emerald-300 rounded-xl text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Profile settings updated successfully!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              University Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Assigned Domain Area
            </label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-indigo-500"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all"
            >
              <Save className="w-4 h-4" />
              <span>Save Workstation Profile</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
