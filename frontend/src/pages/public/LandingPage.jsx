import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function LandingPage() {
  const { switchRoleDemo } = useAuth();
  const navigate = useNavigate();

  const handleDemoLaunch = (role) => {
    switchRoleDemo(role);
    navigate(`/${role}/dashboard`);
  };

  return (
    <div className="space-y-20 pb-16 text-slate-100">
      
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-20 lg:pb-28">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/80 via-[#020617] to-[#020617] -z-10" />
        
        {/* Glow ambient accent */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/15 blur-3xl rounded-full pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          
          {/* Top Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-950/80 border border-blue-800/80 text-blue-300 text-xs font-semibold shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
            <span>Next-Gen University Examination & AI Proctoring Core</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight max-w-4xl mx-auto leading-[1.15]">
            Streamline University Examinations with <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">Secure AI Proctoring</span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
            Exam Portal combines automated MCQ generation from PDF question papers, multi-layered AI anti-cheating enforcement, and real-time university analytics.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => handleDemoLaunch('student')}
              className="w-full sm:w-auto px-7 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-600/30 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <span>Explore Student Exam Demo</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => handleDemoLaunch('interviewer')}
              className="w-full sm:w-auto px-7 py-3.5 bg-slate-900 hover:bg-slate-800 text-slate-200 font-semibold text-sm rounded-xl border border-slate-800 transition-all flex items-center justify-center space-x-2"
            >
              <span>Interviewer PDF Upload Demo</span>
            </button>
          </div>

          {/* Interactive Hero Preview Frame */}
          <div className="mt-12 max-w-5xl mx-auto bg-slate-900/90 rounded-2xl shadow-2xl border border-slate-800 p-4 sm:p-6 text-left relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-rose-500" />
                <span className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-xs font-bold text-slate-300 ml-2">Exam Portal - Live Proctoring Sandbox</span>
              </div>
              <span className="px-2.5 py-0.5 bg-emerald-950/80 text-emerald-300 text-[10px] font-bold rounded-md uppercase border border-emerald-800/80">
                AI Lock active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              
              {/* Feature Box 1 */}
              <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 space-y-2">
                <div className="flex items-center space-x-2 text-blue-400 font-bold">
                  <Eye className="w-4 h-4" />
                  <span>360° Eye & Face Tracking</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Real-time pupil position detection alerts when candidate turns head or looks away from screen.
                </p>
              </div>

              {/* Feature Box 2 */}
              <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 space-y-2">
                <div className="flex items-center space-x-2 text-indigo-400 font-bold">
                  <Laptop className="w-4 h-4" />
                  <span>Full Screen Lock & Guard</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Prevents tab switching, copy-pasting, multi-monitor extensions, and background application execution.
                </p>
              </div>

              {/* Feature Box 3 */}
              <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 space-y-2">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                  <Zap className="w-4 h-4" />
                  <span>Automated AI MCQ Conversion</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Professors drag and drop PDF question sets and AI instantly converts syllabus into calibrated MCQs.
                </p>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* 2. PLATFORM OVERVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Designed for University Rigor & Complete Integrity
          </h2>
          <p className="text-sm text-slate-400">
            Exam Portal unifies candidates, professors, and university administrators into one frictionless workflow.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-md hover:border-slate-700 transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-blue-950/80 border border-blue-800/80 text-blue-400 flex items-center justify-center font-bold">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Student Portal</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Clear exam schedules, pre-test webcam & mic permission checks, interactive MCQ test interface, and instant score rank reports.
            </p>
            <button
              onClick={() => handleDemoLaunch('student')}
              className="text-xs font-semibold text-blue-400 flex items-center space-x-1 hover:underline pt-2"
            >
              <span>Launch Student View</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-md hover:border-slate-700 transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-950/80 border border-indigo-800/80 text-indigo-400 flex items-center justify-center font-bold">
              <FileCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Interviewer & Examiner Workstation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Drag-and-drop PDF question paper upload, AI MCQ compilation, candidate proctor log inspection, and real-time leaderboards.
            </p>
            <button
              onClick={() => handleDemoLaunch('interviewer')}
              className="text-xs font-semibold text-indigo-400 flex items-center space-x-1 hover:underline pt-2"
            >
              <span>Launch Examiner View</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-md hover:border-slate-700 transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 flex items-center justify-center font-bold">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Admin Control Center</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              University-wide exam metrics, student & faculty governance, Recharts interactive data graphs, and feedback management.
            </p>
            <button
              onClick={() => handleDemoLaunch('admin')}
              className="text-xs font-semibold text-slate-200 flex items-center space-x-1 hover:underline pt-2"
            >
              <span>Launch Admin Control</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      </section>

      {/* 3. AI PROCTORING SECTION */}
      <section className="bg-slate-900 text-white py-16 sm:py-20 rounded-3xl mx-4 sm:mx-6 lg:mx-8 px-6 lg:px-12 border border-slate-800 relative overflow-hidden">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <span className="px-3 py-1 bg-blue-950/80 text-blue-300 border border-blue-800/80 text-xs font-semibold rounded-full uppercase tracking-wider">
              AI Security Shield
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Multi-Layered AI Proctoring Engine
            </h2>
            <p className="text-slate-400 text-sm">
              Comprehensive threat detection safeguarding academic integrity during remote & campus digital examinations.
            </p>
          </div>

          {/* Grid of 9 AI Proctoring Features */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: 'Face Detection', desc: 'Verifies continuous biometric presence throughout the exam session.', icon: Camera },
              { title: 'Eye Tracking', desc: 'Detects gaze deviation from the screen to detect off-screen reading.', icon: Eye },
              { title: 'Tab Switch Detection', desc: 'Logs immediate warnings if candidate switches browser tabs or windows.', icon: Laptop },
              { title: 'Multiple Person Detection', desc: 'Flags additional individuals appearing in candidate camera feed.', icon: Users },
              { title: 'Mobile Phone Detection', desc: 'Computer vision identifies mobile devices or smart cameras in view.', icon: Smartphone },
              { title: 'Electronic Device Detection', desc: 'Scans for unauthorized secondary screens, headsets, or devices.', icon: Sliders },
              { title: 'Browser Exit Detection', desc: 'Alerts if lock-down browser window loses focus.', icon: ShieldAlert },
              { title: 'Fullscreen Exit Detection', desc: 'Enforces strictly locked fullscreen mode throughout exam duration.', icon: Lock },
              { title: 'Copy / Paste Detection', desc: 'Blocks keyboard clipboard operations, right-clicks, and text selection.', icon: Copy },
            ].map((p, idx) => {
              const IconComp = p.icon;
              return (
                <div key={idx} className="bg-slate-950/80 border border-slate-800 rounded-2xl p-5 space-y-2 hover:border-blue-500/50 transition-colors">
                  <div className="flex items-center space-x-3 text-blue-400">
                    <IconComp className="w-5 h-5" />
                    <h4 className="font-bold text-white text-sm">{p.title}</h4>
                  </div>
                  <p className="text-slate-400 text-xs leading-relaxed">{p.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. STATISTICS COUNTER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 shadow-md p-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center divide-y lg:divide-y-0 lg:divide-x divide-slate-800">
            <div className="p-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-blue-400">250,000+</div>
              <div className="text-xs font-semibold text-slate-400 uppercase mt-1">Exams Administered</div>
            </div>
            <div className="p-2 pt-6 lg:pt-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-white">99.8%</div>
              <div className="text-xs font-semibold text-slate-400 uppercase mt-1">Proctor Accuracy Rate</div>
            </div>
            <div className="p-2 pt-6 lg:pt-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-blue-400">65+</div>
              <div className="text-xs font-semibold text-slate-400 uppercase mt-1">Partner Universities</div>
            </div>
            <div className="p-2 pt-6 lg:pt-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400">&lt; 1 sec</div>
              <div className="text-xs font-semibold text-slate-400 uppercase mt-1">Violation Log Latency</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. CONTACT CTA */}
      <section className="max-w-5xl mx-auto px-4 text-center">
        <div className="bg-gradient-to-r from-blue-900 via-blue-950 to-indigo-950 border border-blue-800/80 text-white rounded-3xl p-8 sm:p-12 shadow-2xl space-y-6">
          <h2 className="text-2xl sm:text-3xl font-extrabold">Ready to Modernize University Examinations?</h2>
          <p className="text-blue-200 text-sm max-w-xl mx-auto">
            Schedule a demo with our university IT onboarding team or test the portal instantly.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/contact"
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm rounded-xl transition-colors shadow-md"
            >
              Contact University Board
            </Link>
            <button
              onClick={() => handleDemoLaunch('student')}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm rounded-xl border border-slate-700 transition-colors"
            >
              Launch Instant Demo
            </button>
          </div>
        </div>
      </section>

    </div>
  );
}
