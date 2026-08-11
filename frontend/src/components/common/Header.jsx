import React, { useState } from 'react';
import { Menu, Bell, Search } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Header({ title, subtitle, setMobileOpen }) {
  const { user, role } = useAuth();
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const notifications = [
    { id: 1, title: 'AI Proctor Active', desc: 'Secure lockdown browser checks passed.', time: 'Just now' },
    { id: 2, title: 'New Exam Scheduled', desc: 'Data Structures test on 10th Aug.', time: '1 hr ago' },
  ];

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-30 px-4 sm:px-6 py-3 flex items-center justify-between">
      
      {/* Mobile Menu & Page Title */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setMobileOpen(true)}
          className="lg:hidden p-1.5 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">{title}</h1>
          {subtitle && <p className="text-xs text-slate-500 hidden sm:block">{subtitle}</p>}
        </div>
      </div>

      {/* Right Tools & Profile */}
      <div className="flex items-center space-x-3">
        
        {/* Search Input Bar */}
        <div className="hidden md:flex items-center relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search exams, candidates..."
            className="pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 focus:border-blue-500 w-48 lg:w-60 transition-all"
          />
        </div>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 relative transition-colors"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full ring-2 ring-white"></span>
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-slate-200 p-3 z-50 text-slate-800">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-2">
                <span className="text-xs font-bold text-slate-900">Notifications</span>
                <span className="text-[10px] text-blue-600 font-semibold cursor-pointer hover:underline">Mark as read</span>
              </div>
              <div className="space-y-2">
                {notifications.map((n) => (
                  <div key={n.id} className="p-2 bg-slate-50 border border-slate-100 rounded-lg text-xs space-y-0.5">
                    <div className="font-semibold text-slate-800 flex justify-between">
                      <span>{n.title}</span>
                      <span className="text-[10px] text-slate-400">{n.time}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">{n.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Pill */}
        <div className="flex items-center space-x-2.5 pl-2 border-l border-slate-200">
          <img
            src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250'}
            alt={user?.name}
            className="w-8 h-8 rounded-full object-cover ring-1 ring-slate-200"
          />
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-800 leading-tight">{user?.name}</div>
            <div className="text-[10px] text-blue-600 font-medium capitalize">{role} Account</div>
          </div>
        </div>
      </div>
    </header>
  );
}

