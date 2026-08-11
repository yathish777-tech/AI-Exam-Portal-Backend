import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  CheckCircle2,
  PlayCircle,
  User,
  LogOut,
  Upload,
  Users,
  History,
  Trophy,
  UserCheck,
  BarChart3,
  MessageSquare,
  Settings,
  Shield,
  GraduationCap,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar({ mobileOpen, setMobileOpen }) {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Student Links
  const studentLinks = [
    { name: 'Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
    { name: 'Upcoming Interviews', path: '/student/upcoming', icon: Calendar },
    { name: 'Completed Interviews', path: '/student/completed', icon: CheckCircle2 },
    { name: 'Ready for Interview', path: '/student/ready', icon: PlayCircle },
    { name: 'Profile', path: '/student/profile', icon: User },
  ];

  // Interviewer Links
  const interviewerLinks = [
    { name: 'Dashboard', path: '/interviewer/dashboard', icon: LayoutDashboard },
    { name: 'Upload Questions', path: '/interviewer/upload', icon: Upload },
    { name: 'Candidates', path: '/interviewer/candidates', icon: Users },
    { name: 'Past Interviews', path: '/interviewer/past', icon: History },
    { name: 'Leaderboard', path: '/interviewer/leaderboard', icon: Trophy },
    { name: 'Profile', path: '/interviewer/profile', icon: User },
  ];

  // Admin Links
  const adminLinks = [
    { name: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', path: '/admin/students', icon: GraduationCap },
    { name: 'Interviewers', path: '/admin/interviewers', icon: UserCheck },
    { name: 'Reports', path: '/admin/reports', icon: BarChart3 },
    { name: 'Feedback', path: '/admin/feedback', icon: MessageSquare },
    { name: 'Settings', path: '/admin/settings', icon: Settings },
  ];

  const getLinks = () => {
    if (role === 'interviewer') return interviewerLinks;
    if (role === 'admin') return adminLinks;
    return studentLinks;
  };

  const links = getLinks();

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 left-0 bottom-0 z-50 w-64 bg-[#1F2937] border-r border-slate-700/60 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-700/60 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-[#2563EB] flex items-center justify-center text-white shadow-xs">
              <Shield className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <div className="font-semibold text-white tracking-tight text-sm">Secure AI Platform</div>
              <div className="text-[10px] text-slate-400 font-medium capitalize">{role} Portal</div>
            </div>
          </div>
        </div>

        {/* User Card */}
        <div className="p-3 mx-3 my-3 bg-slate-800/60 border border-slate-700/60 rounded-lg flex items-center space-x-3">
          <img
            src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250'}
            alt={user?.name}
            className="w-8 h-8 rounded-full object-cover ring-1 ring-slate-600"
          />
          <div className="overflow-hidden">
            <div className="text-xs font-semibold text-white truncate">{user?.name}</div>
            <div className="text-[10px] text-slate-400 truncate">{user?.email || user?.username}</div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            NAVIGATION
          </div>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-[#374151] text-white border-l-2 border-[#2563EB]'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/70'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{link.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* AI Proctor Status Pill / Footer */}
        <div className="p-3 m-3 bg-slate-800/40 border border-slate-700/50 rounded-lg text-xs space-y-1 text-slate-300">
          <div className="flex items-center space-x-1.5 font-medium text-blue-400 text-[11px]">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>AI Proctoring Engine</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-normal">
            Automated compliance & verification active.
          </p>
        </div>

        {/* Logout Button */}
        <div className="p-3 border-t border-slate-700/60">
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}

