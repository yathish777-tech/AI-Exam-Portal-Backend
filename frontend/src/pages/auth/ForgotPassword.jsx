import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Mail, KeyRound, Lock, CheckCircle2, AlertCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function ForgotPassword() {
  const { requestPasswordReset, verifyResetOtp, resetPassword } = useData();
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1: Enter Email, 2: Enter OTP, 3: Set New Password, 4: Success
  const [role, setRole] = useState('student');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [generatedOtpHint, setGeneratedOtpHint] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Step 1: Submit email to request OTP
  const handleRequestOtp = (e) => {
    e.preventDefault();
    setError('');
    if (!email) {
      setError('Please provide your registered university email.');
      return;
    }

    setLoading(true);
    setTimeout(() => {
      try {
        const res = requestPasswordReset(email, role);
        setGeneratedOtpHint(res.otp);
        setLoading(false);
        setStep(2);
      } catch (err) {
        setError(err.message || 'Failed to request reset code.');
        setLoading(false);
      }
    }, 400);
  };

  // Step 2: Verify OTP
  const handleVerifyOtp = (e) => {
    e.preventDefault();
    setError('');
    if (!otp) {
      setError('Please enter the 6-digit OTP code.');
      return;
    }

    try {
      verifyResetOtp(email, otp);
      setStep(3);
    } catch (err) {
      setError(err.message || 'Invalid or expired OTP verification code.');
    }
  };

  // Step 3: Set New Password
  const handleResetPassword = (e) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setTimeout(() => {
      try {
        resetPassword({ email, otp, newPassword });
        setLoading(false);
        setStep(4);
      } catch (err) {
        setError(err.message || 'Failed to update password.');
        setLoading(false);
      }
    }, 400);
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
          Reset Your Password
        </h1>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Recover access to your account via your registered institutional email address.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 sm:px-8 rounded-xl border border-slate-200/80 shadow-xs space-y-6">
          
          {/* Progress Indicators */}
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 border-b border-slate-100 pb-3">
            <span className={step >= 1 ? 'text-emerald-700 font-bold' : ''}>1. Email</span>
            <span>→</span>
            <span className={step >= 2 ? 'text-emerald-700 font-bold' : ''}>2. OTP</span>
            <span>→</span>
            <span className={step >= 3 ? 'text-emerald-700 font-bold' : ''}>3. New Password</span>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* STEP 1: Enter Email & Role */}
          {step === 1 && (
            <form onSubmit={handleRequestOtp} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Account Role</label>
                <div className="grid grid-cols-3 gap-1 p-1 bg-slate-100 border border-slate-200 rounded-lg text-xs font-medium">
                  {['student', 'interviewer', 'admin'].map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRole(r)}
                      className={`py-1.5 rounded-md capitalize transition-colors ${
                        role === r ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Registered University Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. name@university.edu"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
              >
                <span>{loading ? 'Sending Code...' : 'Send Verification OTP'}</span>
                <ArrowRight className="w-4 h-4 text-emerald-400" />
              </button>
            </form>
          )}

          {/* STEP 2: Enter OTP */}
          {step === 2 && (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs">
                <span>Verification code sent to <strong>{email}</strong>. (Verification OTP: <strong>{generatedOtpHint || '123456'}</strong>)</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Enter 6-Digit Verification OTP
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="123456"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white font-mono tracking-widest text-center"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-1/3 py-2.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg transition-colors flex items-center justify-center space-x-1"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Back</span>
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors"
                >
                  <span>Verify Code</span>
                  <ArrowRight className="w-4 h-4 text-emerald-400" />
                </button>
              </div>
            </form>
          )}

          {/* STEP 3: Enter New Password */}
          {step === 3 && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
              >
                <span>{loading ? 'Updating Password...' : 'Save New Password'}</span>
                <ArrowRight className="w-4 h-4 text-emerald-400" />
              </button>
            </form>
          )}

          {/* STEP 4: Success Message */}
          {step === 4 && (
            <div className="text-center space-y-4 py-3">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Password Reset Complete</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Your password has been updated successfully. You can now sign in with your new credentials.
              </p>
              <Link
                to={`/${role}/login`}
                className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors"
              >
                <span>Sign In to {role.charAt(0).toUpperCase() + role.slice(1)} Portal</span>
                <ArrowRight className="w-4 h-4 text-emerald-400" />
              </Link>
            </div>
          )}

          {/* Bottom Back to Login Link */}
          <div className="pt-4 border-t border-slate-100 text-center text-xs">
            <Link to={`/${role}/login`} className="text-slate-600 hover:text-slate-900 font-medium">
              ← Return to Sign In
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
