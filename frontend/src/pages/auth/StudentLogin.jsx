import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import LoginForm from '../../components/forms/LoginForm';

export default function StudentLogin() {
  return (
    <div className="min-h-screen py-12 px-4 flex flex-col justify-center items-center bg-[#F9FAF9]">
      <div className="mb-6 text-center">
        <Link to="/" className="inline-flex items-center space-x-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-2xs group-hover:bg-emerald-700 transition-colors">
            <Shield className="w-5 h-5 text-white stroke-[2.2]" />
          </div>
          <span className="text-xl font-bold text-slate-900 tracking-tight">Exam Portal</span>
        </Link>
      </div>
      <LoginForm initialRole="student" />
    </div>
  );
}
