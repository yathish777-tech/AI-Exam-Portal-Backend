import React from 'react';
import { Link } from 'react-router-dom';
import {
  Shield,
  Eye,
  Camera,
  Laptop,
  CheckCircle2,
  Lock,
  ArrowRight,
  Sparkles,
  Users,
  Award,
  Zap,
  Globe,
  FileCheck,
  ShieldAlert,
  Smartphone,
  Copy,
  Sliders,
  KeyRound,
  GraduationCap,
  BookOpen,
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-16 pb-16 font-sans text-slate-800 bg-[#F9FAF9]">
      
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-14 pb-16 lg:pt-18 lg:pb-20 border-b border-emerald-100/80 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          
          {/* Subtle Institutional Badge */}
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span>Online Examination Infrastructure</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight max-w-3xl mx-auto leading-tight">
            Online Examination Portal
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            Conduct, manage, and complete examinations through a single platform with structured question management, automated scoring, and built-in session monitoring.
          </p>

          {/* Primary Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Link
              to="/student/login"
              className="w-full sm:w-auto px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2"
            >
              <span>Student Examination Portal</span>
              <ArrowRight className="w-4 h-4 text-emerald-100" />
            </Link>

            <Link
              to="/interviewer/login"
              className="w-full sm:w-auto px-6 py-2.5 bg-white hover:bg-emerald-50/50 text-slate-800 font-semibold text-xs rounded-lg border border-slate-200 transition-colors flex items-center justify-center space-x-2"
            >
              <span>Faculty Examiner Workstation</span>
            </Link>
          </div>

          {/* System Capability Highlights */}
          <div className="mt-10 max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            
            <div className="bg-[#F9FAF9] rounded-xl p-4 border border-emerald-100/80 space-y-1.5">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
                <FileCheck className="w-4 h-4 text-emerald-600" />
                <span>Question Bank Management</span>
              </div>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                Upload question sets and conduct standardized computer-based assessments seamlessly.
              </p>
            </div>

            <div className="bg-[#F9FAF9] rounded-xl p-4 border border-emerald-100/80 space-y-1.5">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
                <Laptop className="w-4 h-4 text-emerald-600" />
                <span>Secure Exam Environment</span>
              </div>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                Full-screen exam sandbox with focus tracking and copy/paste protection.
              </p>
            </div>

            <div className="bg-[#F9FAF9] rounded-xl p-4 border border-emerald-100/80 space-y-1.5">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
                <Camera className="w-4 h-4 text-emerald-600" />
                <span>Session Verification</span>
              </div>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                Optional camera verification to ensure candidate identity and presence during tests.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* 2. THREE ROLE WORKFLOWS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-10 space-y-2">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Role-Based Academic Portals
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Dedicated workflows tailored for students, faculty examiners, and university administrators.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Student Card */}
          <div className="bg-white rounded-xl p-6 border border-emerald-100/80 shadow-xs flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-slate-800 flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Student Portal</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Access assigned examinations, complete device setup, take tests in a secure environment, and view completed scorecards.
              </p>
            </div>
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <Link to="/student/login" className="font-semibold text-emerald-700 hover:text-emerald-800 inline-flex items-center space-x-1">
                <span>Student Sign In</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link to="/student/register" className="text-slate-500 hover:text-slate-700">
                Register →
              </Link>
            </div>
          </div>

          {/* Interviewer Card */}
          <div className="bg-white rounded-xl p-6 border border-emerald-100/80 shadow-xs flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-slate-800 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Faculty Examiner Portal</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Upload question papers, configure exam duration and difficulty, view candidate rosters, and generate performance reports.
              </p>
            </div>
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <Link to="/interviewer/login" className="font-semibold text-emerald-700 hover:text-emerald-800 inline-flex items-center space-x-1">
                <span>Faculty Sign In</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link to="/interviewer/activate" className="text-slate-500 hover:text-slate-700">
                Activate Account →
              </Link>
            </div>
          </div>

          {/* Admin Card */}
          <div className="bg-white rounded-xl p-6 border border-emerald-100/80 shadow-xs flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-slate-800 flex items-center justify-center">
                <Shield className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="text-base font-bold text-slate-900">University Administration</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Manage student directories, provision faculty examiner accounts, review session logs, and oversee university examination governance.
              </p>
            </div>
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <Link to="/admin/login" className="font-semibold text-emerald-700 hover:text-emerald-800 inline-flex items-center space-x-1">
                <span>Admin Sign In</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <span className="text-[11px] text-slate-400">Institutional Governance</span>
            </div>
          </div>

        </div>
      </section>

      {/* 3. CORE PLATFORM FEATURES OVERVIEW */}
      <section className="bg-white py-12 border-y border-emerald-100/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="text-center max-w-2xl mx-auto space-y-1.5">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Integrated Examination Features
            </h2>
            <p className="text-xs text-slate-500">
              Built-in tools supporting accurate delivery, evaluation, and integrity across all test sessions.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { title: 'Question Delivery Engine', desc: 'Fast, responsive question navigator with answer caching and bookmarking.', icon: FileCheck },
              { title: 'Presence Verification', desc: 'Periodic biometric checks confirming continuous student attendance.', icon: Camera },
              { title: 'Browser Security Enforcer', desc: 'Prevents tab switching, screen loss, and unauthorized external window actions.', icon: Laptop },
              { title: 'Full Screen Lock', desc: 'Ensures dedicated focus by enforcing fullscreen mode throughout the test.', icon: Lock },
              { title: 'Copy & Paste Restriction', desc: 'Secures exam integrity by disabling clipboard actions and shortcuts.', icon: Copy },
              { title: 'Instant Scorecards & Analytics', desc: 'Generates detailed score breakdowns and evaluation metrics immediately.', icon: Award },
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-[#F9FAF9] rounded-lg p-4 border border-emerald-100/80 space-y-1.5 shadow-2xs">
                  <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
                    <Icon className="w-4 h-4 text-emerald-600" />
                    <span>{item.title}</span>
                  </div>
                  <p className="text-slate-500 text-[11px] leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

    </div>
  );
}
