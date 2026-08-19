import React from 'react';
import { Shield, Lock, Award } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-white text-slate-600 pt-12 pb-8 border-t border-emerald-100/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-8 border-b border-slate-100">
          
          {/* Brand Info */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold shadow-2xs">
                <Shield className="w-4.5 h-4.5 stroke-[2.2]" />
              </div>
              <span className="text-lg font-bold text-slate-900 tracking-tight">Exam Portal</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Online examination portal providing secure test delivery, candidate assessment, and scoring governance.
            </p>
            <div className="flex items-center space-x-3 text-[11px] text-slate-500 pt-1">
              <span className="flex items-center space-x-1">
                <Lock className="w-3.5 h-3.5 text-emerald-600" />
                <span>Encrypted Sessions</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <Award className="w-3.5 h-3.5 text-emerald-600" />
                <span>Verified Assessment</span>
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">Portal Access</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/student/login" className="hover:text-emerald-800 transition-colors">Student Portal</Link></li>
              <li><Link to="/interviewer/login" className="hover:text-emerald-800 transition-colors">Faculty Examiner Portal</Link></li>
              <li><Link to="/admin/login" className="hover:text-emerald-800 transition-colors">Admin Governance</Link></li>
              <li><Link to="/about" className="hover:text-emerald-800 transition-colors">About Exam Portal</Link></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">System Features</h4>
            <ul className="space-y-2 text-xs text-slate-500">
              <li>Question Paper Management</li>
              <li>Automated Result Generation</li>
              <li>Fullscreen Security Mode</li>
              <li>Candidate Verification</li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">Support</h4>
            <p className="text-xs text-slate-600 mb-1">Examination Controller Office</p>
            <p className="text-xs text-slate-500">support@examportal.edu</p>
            <p className="text-xs text-slate-500">Helpline: +1 (800) 555-EXAM</p>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 space-y-2 sm:space-y-0">
          <div>
            © {new Date().getFullYear()} Exam Portal. Online Examination Platform.
          </div>
          <div className="flex items-center space-x-1 text-slate-500">
            <span>Standardized Assessment Infrastructure</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
