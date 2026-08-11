import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, BookOpen, ArrowRight } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function RegisterForm({ role = 'student' }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [domain, setDomain] = useState('Data Structures & Algorithms');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const getErrorMessage = (err) => {
    const detail = err?.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail[0]?.msg || 'Registration failed.';
    return err?.response?.data?.message || err?.message || 'Registration failed.';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all required fields.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 10) {
      setError('Password should be at least 10 characters long.');
      return;
    }

    setLoading(true);
    try {
      await register({ name, email, password, domain }, role);
      setLoading(false);
      navigate(`/${role}/dashboard`);
    } catch (err) {
      setLoading(false);
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6 sm:p-8 max-w-md w-full mx-auto text-slate-800">
      <div className="text-center mb-6">
        <h2 className="text-lg font-bold text-slate-900 tracking-tight">
          {role === 'student' ? 'Register Student Account' : 'Register Interviewer Account'}
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Create credentials to access the university examination network
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Full Name
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aarav Sharma"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-md focus:outline-hidden focus:border-blue-500"
              required
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            University Email
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="student@university.edu"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-md focus:outline-hidden focus:border-blue-500"
              required
            />
          </div>
        </div>

        {/* Domain if Interviewer */}
        {role === 'interviewer' && (
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Assigned Domain / Subject Area
            </label>
            <div className="relative">
              <BookOpen className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
              >
                <option value="Data Structures & Algorithms">Data Structures & Algorithms</option>
                <option value="Artificial Intelligence & ML">Artificial Intelligence & ML</option>
                <option value="Database Management Systems">Database Management Systems</option>
                <option value="Network Security & Cryptography">Network Security & Cryptography</option>
                <option value="Full Stack Web Development">Full Stack Web Development</option>
              </select>
            </div>
          </div>
        )}

        {/* Password */}
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

        {/* Confirm Password */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
          <span>{loading ? 'Creating Account...' : 'Complete Registration'}</span>
          <ArrowRight className="w-4 h-4 text-blue-400" />
        </button>
      </form>

      <p className="text-center text-xs text-slate-500 mt-5">
        Already have an account?{' '}
        <Link to={`/${role}/login`} className="text-blue-600 font-semibold hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}

