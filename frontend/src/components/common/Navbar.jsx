import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, User, LogIn, ChevronDown, Menu, X, UserCheck, ShieldCheck, GraduationCap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { user, role, switchRoleDemo, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const handleRoleSwitch = (targetRole) => {
    if (switchRoleDemo) switchRoleDemo(targetRole);
    setRoleDropdownOpen(false);
    setMobileMenuOpen(false);
    if (targetRole === 'student') navigate('/student/login');
    else if (targetRole === 'interviewer') navigate('/interviewer/login');
    else if (targetRole === 'admin') navigate('/admin/login');
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-emerald-100/80 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-2xs group-hover:bg-emerald-700 transition-colors">
              <Shield className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold text-slate-900 tracking-tight">
                Exam Portal
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-semibold text-emerald-800 bg-emerald-50 rounded-md border border-emerald-200">
                Official
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
                className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                  isActive(link.path)
                    ? 'text-emerald-800 bg-emerald-50 border border-emerald-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Right Action Controls */}
          <div className="hidden md:flex items-center space-x-3">
            
            {/* Role Portals Dropdown */}
            <div className="relative">
              <button
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-50 border border-slate-200 rounded-md hover:bg-slate-100 transition-colors"
                title="Select Examination Portal"
              >
                <span>Select Portal</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              </button>

              {roleDropdownOpen && (
                <div className="absolute right-0 mt-2 w-52 bg-white rounded-lg shadow-lg border border-slate-200 py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Role Gateways
                  </div>
                  <button
                    onClick={() => handleRoleSwitch('student')}
                    className="w-full flex items-center space-x-2.5 px-3 py-2 text-left text-xs text-slate-700 hover:bg-emerald-50 hover:text-emerald-800 transition-colors"
                  >
                    <GraduationCap className="w-4 h-4 text-emerald-600" />
                    <div>
                      <div className="font-semibold">Student Portal</div>
                      <div className="text-[10px] text-slate-500">Exams & Scorecards</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleRoleSwitch('interviewer')}
                    className="w-full flex items-center space-x-2.5 px-3 py-2 text-left text-xs text-slate-700 hover:bg-emerald-50 hover:text-emerald-800 transition-colors"
                  >
                    <UserCheck className="w-4 h-4 text-emerald-600" />
                    <div>
                      <div className="font-semibold">Faculty Examiner</div>
                      <div className="text-[10px] text-slate-500">Paper Upload & Results</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleRoleSwitch('admin')}
                    className="w-full flex items-center space-x-2.5 px-3 py-2 text-left text-xs text-slate-700 hover:bg-emerald-50 hover:text-emerald-800 transition-colors"
                  >
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    <div>
                      <div className="font-semibold">Administrator</div>
                      <div className="text-[10px] text-slate-500">Governance & Directory</div>
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
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-md shadow-2xs transition-colors"
                >
                  <User className="w-3.5 h-3.5" />
                  <span>Go to {role.charAt(0).toUpperCase() + role.slice(1)} Portal</span>
                </Link>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/student/login"
                  className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-emerald-800 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/student/register"
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-md shadow-2xs transition-colors"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-emerald-100 px-4 pt-2 pb-4 space-y-3">
          <div className="flex flex-col space-y-1">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:bg-emerald-50"
            >
              Home
            </Link>
            <Link
              to="/about"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:bg-emerald-50"
            >
              About
            </Link>
            <Link
              to="/contact"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:bg-emerald-50"
            >
              Contact
            </Link>
            <Link
              to="/faq"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:bg-emerald-50"
            >
              FAQ
            </Link>
          </div>

          <div className="pt-2 border-t border-slate-100 space-y-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">
              Role Access
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => handleRoleSwitch('student')}
                className="px-2 py-1.5 text-xs font-medium text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-md text-center"
              >
                Student
              </button>
              <button
                onClick={() => handleRoleSwitch('interviewer')}
                className="px-2 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-md text-center"
              >
                Faculty
              </button>
              <button
                onClick={() => handleRoleSwitch('admin')}
                className="px-2 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-md text-center"
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
