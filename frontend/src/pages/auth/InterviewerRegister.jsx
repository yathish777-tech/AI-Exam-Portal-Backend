import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, KeyRound, ArrowRight, ShieldCheck, Mail } from 'lucide-react';

export default function InterviewerRegister() {
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
          Faculty Interviewer Access
        </h1>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 sm:px-8 rounded-xl border border-slate-200/80 shadow-xs space-y-6">
          
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2 text-xs text-slate-700 leading-relaxed">
            <div className="flex items-center space-x-2 text-slate-900 font-bold">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Admin-Managed Faculty Accounts</span>
            </div>
            <p>
              To maintain academic integrity, examiner and interviewer accounts are provisioned exclusively by University Administrators and Department Chairs.
            </p>
            <p>
              If your department has initiated an invitation, you will have received a 6-digit activation OTP or invitation code at your university email address.
            </p>
          </div>

          <div className="space-y-3">
            <Link
              to="/interviewer/activate"
              className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors"
            >
              <KeyRound className="w-4 h-4 text-emerald-400" />
              <span>Activate Your Interviewer Account</span>
              <ArrowRight className="w-4 h-4 text-emerald-400" />
            </Link>

            <Link
              to="/interviewer/login"
              className="w-full py-2 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs rounded-lg flex items-center justify-center space-x-2 transition-colors"
            >
              <span>Sign In to Existing Account</span>
            </Link>
          </div>

          <div className="pt-4 border-t border-slate-100 text-center text-xs">
            <Link to="/" className="text-slate-400 hover:text-slate-600">
              ← Return to Homepage
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
