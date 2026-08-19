import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Lock, Mail, User, ArrowRight, ShieldCheck, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function LoginForm({ initialRole = 'student' }) {
  const [activeTab, setActiveTab] = useState(initialRole); // 'student' | 'interviewer' | 'admin'
  const [emailOrUser, setEmailOrUser] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Show activation message if passed via redirect state
  const activationNotice = location.state?.activationSuccess || '';

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!emailOrUser || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    setTimeout(() => {
      try {
        login(emailOrUser, password, activeTab);
        setLoading(false);
        navigate(`/${activeTab}/dashboard`);
      } catch (err) {
        setError(err.message || 'Unable to sign in. Please verify your credentials and try again.');
        setLoading(false);
      }
    }, 350);
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6 sm:p-8 max-w-md w-full mx-auto text-slate-800">
      
      {/* Role Selection Tabs */}
      <div className="grid grid-cols-3 gap-1 p-1 bg-slate-100 border border-slate-200 rounded-lg mb-6 text-xs font-medium">
        <button
          type="button"
          onClick={() => { setActiveTab('student'); setError(''); }}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'student'
              ? 'bg-white text-slate-900 font-bold shadow-xs border-b-2 border-emerald-600'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Student
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('interviewer'); setError(''); }}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'interviewer'
              ? 'bg-white text-slate-900 font-bold shadow-xs border-b-2 border-emerald-600'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Interviewer
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('admin'); setError(''); }}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'admin'
              ? 'bg-white text-slate-900 font-bold shadow-xs border-b-2 border-emerald-600'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Admin
        </button>
      </div>

      <div className="text-center mb-6">
        <h2 className="text-lg font-bold text-slate-900 tracking-tight">
          {activeTab === 'student' && 'Student Exam Portal Login'}
          {activeTab === 'interviewer' && 'Interviewer Workstation Login'}
          {activeTab === 'admin' && 'University Admin Governance Login'}
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          {activeTab === 'student' && 'Sign in to access your proctored examinations and scorecards.'}
          {activeTab === 'interviewer' && 'Sign in to manage question sets, examinees, and live evaluations.'}
          {activeTab === 'admin' && 'Access university-wide examination infrastructure and governance.'}
        </p>
      </div>

      {activationNotice && (
        <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-lg flex items-start space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <span>{activationNotice}</span>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {activeTab === 'admin' ? 'Administrator Username or Email' : 'University Institutional Email'}
          </label>
          <div className="relative">
            {activeTab === 'admin' ? (
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            ) : (
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            )}
            <input
              type={activeTab === 'admin' ? 'text' : 'email'}
              value={emailOrUser}
              onChange={(e) => setEmailOrUser(e.target.value)}
              placeholder={activeTab === 'admin' ? 'e.g. admin' : 'e.g. name@university.edu'}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
              required
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-xs font-semibold text-slate-700">
              Password
            </label>
            <Link
              to="/forgot-password"
              className="text-[11px] text-emerald-700 hover:text-emerald-800 font-semibold hover:underline"
            >
              Forgot Password?
            </Link>
          </div>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 mt-3"
        >
          <span>{loading ? 'Authenticating...' : `Sign In to ${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Portal`}</span>
          <ArrowRight className="w-4 h-4 text-emerald-400" />
        </button>
      </form>

      {/* Role-Specific Context Helpers */}
      <div className="mt-6 pt-5 border-t border-slate-100 text-center text-xs space-y-2">
        {activeTab === 'student' && (
          <p className="text-slate-600">
            Don't have a student account?{' '}
            <Link to="/student/register" className="text-emerald-700 font-semibold hover:underline">
              Register as Student
            </Link>
          </p>
        )}

        {activeTab === 'interviewer' && (
          <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-lg text-left space-y-1">
            <span className="text-[11px] font-semibold text-slate-800 block">Received an Invitation?</span>
            <p className="text-[11px] text-slate-500 leading-normal">
              Interviewer credentials are created by University Admins.{' '}
              <Link to="/interviewer/activate" className="text-emerald-700 font-semibold hover:underline">
                Activate your account with OTP →
              </Link>
            </p>
          </div>
        )}

        {activeTab === 'admin' && (
          <p className="text-[11px] text-slate-500 flex items-center justify-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 inline" />
            <span>Central University IT Governance Access</span>
          </p>
        )}

        <div className="pt-2">
          <Link to="/" className="text-slate-400 hover:text-slate-600 text-xs">
            ← Return to Homepage
          </Link>
        </div>
      </div>

    </div>
  );
}
