import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, Sparkles, User, LogIn, ChevronDown, Menu, X, UserCheck, ShieldCheck, GraduationCap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { user, role, switchRoleDemo, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [demoDropdownOpen, setDemoDropdownOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const handleDemoSwitch = (targetRole) => {
    switchRoleDemo(targetRole);
    setDemoDropdownOpen(false);
    setMobileMenuOpen(false);
    if (targetRole === 'student') navigate('/student/dashboard');
    else if (targetRole === 'interviewer') navigate('/interviewer/dashboard');
    else if (targetRole === 'admin') navigate('/admin/dashboard');
  };

  return (
    <header className="sticky top-0 z-40 bg-[#020617]/90 backdrop-blur-md border-b border-slate-800/80 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-blue-800 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
              <Shield className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent tracking-tight">
                Exam Portal
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-blue-400 bg-blue-950/60 rounded-full border border-blue-800/80 uppercase">
                AI Secure
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {[
              { name: 'Home', path: '/' },
              { name: 'About', path: '/about' },
              { name: 'Contact', path: '/contact' },
              { name: 'FAQ', path: '/faq' },
            ].map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(link.path)
                    ? 'text-blue-400 bg-blue-950/50 border border-blue-800/50 font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Right Action Controls */}
          <div className="hidden md:flex items-center space-x-3">
            
            {/* Quick Demo Switcher Dropdown */}
            <div className="relative">
              <button
                onClick={() => setDemoDropdownOpen(!demoDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold text-blue-300 bg-blue-950/60 border border-blue-800/80 rounded-lg hover:bg-blue-900/60 transition-colors"
                title="Quick Switch Dashboard Demo"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                <span>Quick Demo Mode</span>
                <ChevronDown className="w-3.5 h-3.5 text-blue-400" />
              </button>

              {demoDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-slate-900 rounded-xl shadow-2xl border border-slate-800 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="px-3 py-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Instant Role Demo
                  </div>
                  <button
                    onClick={() => handleDemoSwitch('student')}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-800 hover:text-blue-400 transition-colors"
                  >
                    <GraduationCap className="w-4 h-4 text-blue-400" />
                    <div>
                      <div className="font-medium">Student Portal</div>
                      <div className="text-[11px] text-slate-400">Exams, Proctoring & Scores</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDemoSwitch('interviewer')}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-800 hover:text-indigo-400 transition-colors"
                  >
                    <UserCheck className="w-4 h-4 text-indigo-400" />
                    <div>
                      <div className="font-medium">Interviewer Portal</div>
                      <div className="text-[11px] text-slate-400">PDF Upload & Leaderboards</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDemoSwitch('admin')}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-800 hover:text-emerald-400 transition-colors"
                  >
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <div>
                      <div className="font-medium">Admin Control Panel</div>
                      <div className="text-[11px] text-slate-400">System Analytics & Management</div>
                    </div>
                  </button>
                </div>
              )}
            </div>

            {/* Dashboard or Auth Button */}
            {user ? (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/${role}/dashboard`}
                  className="inline-flex items-center space-x-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-lg shadow-blue-600/30 transition-all duration-200"
                >
                  <User className="w-4 h-4" />
                  <span>Go to {role.charAt(0).toUpperCase() + role.slice(1)} Dashboard</span>
                </Link>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/student/login"
                  className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/student/register"
                  className="inline-flex items-center space-x-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-lg shadow-blue-600/30 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3">
          <div className="flex flex-col space-y-1">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              Home
            </Link>
            <Link
              to="/about"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              About
            </Link>
            <Link
              to="/contact"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              Contact
            </Link>
            <Link
              to="/faq"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              FAQ
            </Link>
          </div>

          <div className="pt-2 border-t border-slate-800 space-y-2">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2">
              Instant Demo Access
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => handleDemoSwitch('student')}
                className="px-2 py-1.5 text-xs font-medium text-blue-300 bg-blue-950/60 border border-blue-800/80 rounded-lg text-center"
              >
                Student
              </button>
              <button
                onClick={() => handleDemoSwitch('interviewer')}
                className="px-2 py-1.5 text-xs font-medium text-indigo-300 bg-indigo-950/60 border border-indigo-800/80 rounded-lg text-center"
              >
                Interviewer
              </button>
              <button
                onClick={() => handleDemoSwitch('admin')}
                className="px-2 py-1.5 text-xs font-medium text-emerald-300 bg-emerald-950/60 border border-emerald-800/80 rounded-lg text-center"
              >
                Admin
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
