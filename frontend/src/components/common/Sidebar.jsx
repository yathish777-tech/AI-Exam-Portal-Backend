import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import Avatar from './Avatar';
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
  Radio,
  FileCheck,
  ShieldAlert,
  Activity,
  BookOpen,
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
    { name: 'Upcoming Exams', path: '/student/upcoming', icon: Calendar },
    { name: 'Completed Exams', path: '/student/completed', icon: CheckCircle2 },
    { name: 'Hardware Verification', path: '/student/ready', icon: PlayCircle },
    { name: 'Profile & Settings', path: '/student/profile', icon: User },
  ];

  // Interviewer Links
  const interviewerLinks = [
    { name: 'Dashboard', path: '/interviewer/dashboard', icon: LayoutDashboard },
    { name: 'Upload Question PDF', path: '/interviewer/upload', icon: Upload },
    { name: 'Live Monitoring', path: '/interviewer/live-monitoring', icon: Radio },
    { name: 'Candidates Roster', path: '/interviewer/candidates', icon: Users },
    { name: 'Evaluation Reports', path: '/interviewer/reports', icon: BarChart3 },
    { name: 'Past Exams', path: '/interviewer/past', icon: History },
    { name: 'Leaderboard', path: '/interviewer/leaderboard', icon: Trophy },
    { name: 'Profile & Domain', path: '/interviewer/settings', icon: Settings },
  ];

  // Admin Links
  const adminLinks = [
    { name: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Student Directory', path: '/admin/students', icon: GraduationCap },
    { name: 'Faculty Examiners', path: '/admin/interviewers', icon: UserCheck },
    { name: 'Exam Management', path: '/admin/exams', icon: BookOpen },
    { name: 'AI Warning Logs', path: '/admin/warnings', icon: ShieldAlert },
    { name: 'Activity Audit Trail', path: '/admin/activity', icon: Activity },
    { name: 'Reports & Analytics', path: '/admin/reports', icon: BarChart3 },
    { name: 'Student Feedback', path: '/admin/feedback', icon: MessageSquare },
    { name: 'Governance Settings', path: '/admin/settings', icon: Settings },
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
        className={`fixed top-0 left-0 bottom-0 z-50 w-64 bg-white border-r border-emerald-100/80 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 shadow-2xs ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-emerald-100/80 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-2xs">
              <Shield className="w-4.5 h-4.5 stroke-[2.2]" />
            </div>
            <div>
              <div className="font-bold text-slate-900 tracking-tight text-xs">Exam Portal</div>
              <div className="text-[10px] text-emerald-700 font-semibold capitalize">{role} Workspace</div>
            </div>
          </div>
        </div>

        {/* User Card */}
        <div className="p-2.5 mx-3 my-3 bg-[#F9FAF9] border border-emerald-100/80 rounded-lg flex items-center space-x-2.5">
          <Avatar name={user?.name || user?.username} size="sm" />
          <div className="overflow-hidden">
            <div className="text-xs font-bold text-slate-900 truncate">{user?.name}</div>
            <div className="text-[10px] text-slate-500 truncate">{user?.email || user?.username}</div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          <div className="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Navigation
          </div>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-semibold transition-colors ${
                    isActive
                      ? 'bg-emerald-50 text-emerald-900 border-l-2 border-emerald-600'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0 text-emerald-600" />
                <span>{link.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* System Status Pill / Footer */}
        <div className="p-3 m-3 bg-[#F9FAF9] border border-emerald-100 rounded-lg text-xs space-y-0.5 text-slate-700">
          <div className="flex items-center space-x-1.5 font-bold text-emerald-800 text-[11px]">
            <Shield className="w-3.5 h-3.5 text-emerald-600" />
            <span>Secure System Active</span>
          </div>
          <p className="text-[10px] text-slate-500 leading-normal">
            Assessment session protocols verified.
          </p>
        </div>

        {/* Logout Button */}
        <div className="p-3 border-t border-slate-100">
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium text-slate-600 hover:bg-red-50 hover:text-red-700 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}

