import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, BookOpen, ArrowRight, Check, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function RegisterForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('Computer Science & Engineering');
  const [rollNo, setRollNo] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  // Validation
  const hasMinLength = password.length >= 8;
  const passwordsMatch = password && password === confirmPassword;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!hasMinLength) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setTimeout(() => {
      try {
        register({ name, email, department, rollNo });
        setLoading(false);
        navigate('/student/dashboard');
      } catch (err) {
        setError(err.message || 'Registration failed. Please try again.');
        setLoading(false);
      }
    }, 400);
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6 sm:p-8 max-w-md w-full mx-auto text-slate-800">
      <div className="text-center mb-6">
        <h2 className="text-lg font-bold text-slate-900 tracking-tight">
          Student Examination Registration
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Register with your institutional credentials to enroll in upcoming assessments.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Candidate Full Name
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aarav Sharma"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
              required
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            University Institutional Email
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. aarav.s@university.edu"
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
              required
            />
          </div>
        </div>

        {/* Department & Roll Number */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Roll / Reg No.
            </label>
            <input
              type="text"
              value={rollNo}
              onChange={(e) => setRollNo(e.target.value)}
              placeholder="e.g. 2026-CS-042"
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Department
            </label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full px-2.5 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
            >
              <option value="Computer Science & Engineering">CSE</option>
              <option value="Information Technology">IT</option>
              <option value="Electronics & Communication">ECE</option>
              <option value="Data Science & AI">AI & DS</option>
            </select>
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Password (min. 8 characters)
          </label>
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

        {/* Confirm Password */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
          <span>{loading ? 'Registering Account...' : 'Complete Student Registration'}</span>
          <ArrowRight className="w-4 h-4 text-emerald-400" />
        </button>
      </form>

      <div className="pt-4 mt-6 border-t border-slate-100 text-center text-xs space-y-2">
        <p className="text-slate-600">
          Already have a student account?{' '}
          <Link to="/student/login" className="text-emerald-700 font-semibold hover:underline">
            Sign In
          </Link>
        </p>
        <Link to="/" className="block text-slate-400 hover:text-slate-600 text-xs">
          ← Return to Homepage
        </Link>
      </div>
    </div>
  );
}
