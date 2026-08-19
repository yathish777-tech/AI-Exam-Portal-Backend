import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, KeyRound, Mail, Lock, CheckCircle2, AlertCircle, ArrowRight, Check } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function InterviewerActivation() {
  const { activateInterviewerAccount } = useData();
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve optional query params or state passed from admin invitation
  const queryParams = new URLSearchParams(location.search);
  const initialEmail = queryParams.get('email') || '';
  const initialCode = queryParams.get('code') || queryParams.get('otp') || '';

  const [email, setEmail] = useState(initialEmail);
  const [otp, setOtp] = useState(initialCode);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  // Password validation rules
  const hasMinLength = newPassword.length >= 8;
  const hasUpperCase = /[A-Z]/.test(newPassword);
  const hasNumber = /[0-9]/.test(newPassword);
  const hasSpecial = /[^A-Za-z0-9]/.test(newPassword);
  const passwordsMatch = newPassword && newPassword === confirmPassword;
  const isPasswordValid = hasMinLength && hasUpperCase && hasNumber && hasSpecial && passwordsMatch;

  const handleActivate = (e) => {
    e.preventDefault();
    setError('');

    if (!email || !otp) {
      setError('Please provide your university email and invitation OTP/Code.');
      return;
    }

    if (!isPasswordValid) {
      setError('Please ensure your password meets all security requirements.');
      return;
    }

    setLoading(true);

    try {
      // Execute account activation in DataContext
      activateInterviewerAccount({
        email: email.trim(),
        otp: otp.trim(),
        newPassword,
      });

      setSuccess(true);
      setLoading(false);

      // Redirect to Interviewer Login after 2.5s
      setTimeout(() => {
        navigate('/interviewer/login', {
          state: { activationSuccess: 'Your account has been activated successfully. You can now sign in.' },
        });
      }, 2500);
    } catch (err) {
      setError(err.message || 'Account activation failed. Please verify your OTP or contact Administrator.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans text-slate-800">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-3">
        <Link to="/" className="inline-flex items-center space-x-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-xs group-hover:bg-slate-800 transition-colors">
            <Shield className="w-5 h-5 text-emerald-400 stroke-[2.5]" />
          </div>
          <span className="text-xl font-bold text-slate-900 tracking-tight">Exam Portal</span>
        </Link>

        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Activate Your Interviewer Account
        </h1>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Interviewer accounts are provisioned by university administrators. Enter your invitation code and establish your permanent password.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 sm:px-8 rounded-xl border border-slate-200/80 shadow-xs space-y-6">
          
          {/* Success Banner */}
          {success ? (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-center space-y-3">
              <div className="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-emerald-900">Activation Successful!</h3>
              <p className="text-xs text-emerald-700 leading-relaxed">
                Your faculty account has been activated and your permanent password has been set. Redirecting to sign in...
              </p>
              <Link
                to="/interviewer/login"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-emerald-700 hover:text-emerald-800 underline"
              >
                <span>Proceed to Sign In immediately</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : (
            <form onSubmit={handleActivate} className="space-y-4">
              
              {/* Error Message */}
              {error && (
                <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Email Address */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Invited University Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. harish.k@university.edu"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              {/* OTP or Invitation Verification Code */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-semibold text-slate-700">
                    Invitation OTP / Verification Code
                  </label>
                  <span className="text-[10px] text-slate-400">Check invitation email</span>
                </div>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="text"
                    required
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="6-digit OTP (e.g. 123456) or INV-CODE"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white tracking-wider font-mono transition-colors"
                  />
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Create Permanent Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
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
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              {/* Password Requirements Checklist */}
              <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-lg space-y-1 text-[11px] text-slate-600">
                <span className="font-semibold text-slate-700 block mb-1">Password Requirements:</span>
                <div className={`flex items-center space-x-1.5 ${hasMinLength ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <Check className={`w-3.5 h-3.5 ${hasMinLength ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>At least 8 characters long</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${hasUpperCase ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <Check className={`w-3.5 h-3.5 ${hasUpperCase ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>At least one uppercase letter (A-Z)</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${hasNumber ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <Check className={`w-3.5 h-3.5 ${hasNumber ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>At least one numeric digit (0-9)</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${hasSpecial ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <Check className={`w-3.5 h-3.5 ${hasSpecial ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>At least one special symbol (!@#$%^&*)</span>
                </div>
                {confirmPassword && (
                  <div className={`flex items-center space-x-1.5 ${passwordsMatch ? 'text-emerald-700 font-medium' : 'text-rose-600'}`}>
                    <Check className={`w-3.5 h-3.5 ${passwordsMatch ? 'text-emerald-600' : 'text-rose-400'}`} />
                    <span>Passwords match</span>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !isPasswordValid}
                className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 mt-2"
              >
                <span>{loading ? 'Activating Account...' : 'Set Password & Activate Account'}</span>
                <ArrowRight className="w-4 h-4 text-emerald-400" />
              </button>
            </form>
          )}

          {/* Navigation Links */}
          <div className="pt-4 border-t border-slate-100 flex flex-col space-y-2 text-center text-xs">
            <Link to="/interviewer/login" className="text-slate-600 hover:text-slate-900 font-medium">
              Already activated your account? <span className="text-emerald-700 font-semibold underline">Sign In</span>
            </Link>
            <Link to="/" className="text-slate-400 hover:text-slate-600">
              ← Return to Home
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
