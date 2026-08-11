import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function LoginForm({ initialRole = 'student' }) {
  const [activeTab, setActiveTab] = useState(initialRole); // 'student' | 'interviewer' | 'admin'
  const [emailOrUser, setEmailOrUser] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const getErrorMessage = (err) => {
    const detail = err?.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail[0]?.msg || 'Login failed.';
    return err?.response?.data?.message || err?.message || 'Login failed.';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!emailOrUser || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    try {
      await login(emailOrUser, password, activeTab);
      setLoading(false);
      navigate(`/${activeTab}/dashboard`);
    } catch (err) {
      setLoading(false);
      setError(getErrorMessage(err));
    }
  };

  const fillDemoAccount = (role) => {
    setActiveTab(role);
    if (role === 'student') {
      setEmailOrUser('student@examportal.edu');
      setPassword('password123');
    } else if (role === 'interviewer') {
      setEmailOrUser('interviewer@examportal.edu');
      setPassword('password123');
    } else if (role === 'admin') {
      setEmailOrUser('admin');
      setPassword('admin123');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6 sm:p-8 max-w-md w-full mx-auto text-slate-800">
      
      {/* Role Navigation Tabs */}
      <div className="grid grid-cols-3 gap-1 p-1 bg-slate-100 border border-slate-200 rounded-lg mb-6 text-xs font-medium">
        <button
          type="button"
          onClick={() => setActiveTab('student')}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'student' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Student
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('interviewer')}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'interviewer' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Interviewer
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('admin')}
          className={`py-2 rounded-md transition-colors ${
            activeTab === 'admin' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'
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
        <p className="text-xs text-slate-500 mt-0.5">
          Sign in to access your secure AI exam environment
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
          <span>{error}</span>
        </div>
      )}

      {/* Form Inputs */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            {activeTab === 'admin' ? 'Admin Username or Email' : 'University Email'}
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
              placeholder={activeTab === 'admin' ? 'admin' : `${activeTab}@examportal.edu`}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-md focus:outline-hidden focus:border-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-md focus:outline-hidden focus:border-blue-500"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 mt-2"
        >
          <span>{loading ? 'Authenticating...' : `Sign In as ${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}`}</span>
          <ArrowRight className="w-4 h-4 text-blue-400" />
        </button>
      </form>

      {/* Quick Demo Fill Helper */}
      <div className="mt-6 pt-5 border-t border-slate-200">
        <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-medium mb-2">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Quick Demo Credentials Auto-Fill</span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <button
            type="button"
            onClick={() => fillDemoAccount('student')}
            className={`p-2 rounded-md border text-center transition-colors ${
              activeTab === 'student' ? 'border-slate-300 bg-slate-100 text-slate-900 font-bold' : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-600'
            }`}
          >
            Student
          </button>
          <button
            type="button"
            onClick={() => fillDemoAccount('interviewer')}
            className={`p-2 rounded-md border text-center transition-colors ${
              activeTab === 'interviewer' ? 'border-slate-300 bg-slate-100 text-slate-900 font-bold' : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-600'
            }`}
          >
            Interviewer
          </button>
          <button
            type="button"
            onClick={() => fillDemoAccount('admin')}
            className={`p-2 rounded-md border text-center transition-colors ${
              activeTab === 'admin' ? 'border-slate-300 bg-slate-100 text-slate-900 font-bold' : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-600'
            }`}
          >
            Admin
          </button>
        </div>
      </div>

      {activeTab !== 'admin' && (
        <p className="text-center text-xs text-slate-500 mt-5">
          Don't have an account?{' '}
          <Link to={`/${activeTab}/register`} className="text-blue-600 font-semibold hover:underline">
            Register here
          </Link>
        </p>
      )}
    </div>
  );
}

