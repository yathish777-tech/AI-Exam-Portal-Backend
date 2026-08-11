import React from 'react';
import { Shield, Lock, Award, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-[#020617] text-slate-400 pt-12 pb-8 border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-8 border-b border-slate-800/80">
          
          {/* Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md">
                <Shield className="w-5 h-5 stroke-[2.5]" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">Exam Portal</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Secure AI-powered interview & examination infrastructure for higher education and university certifications.
            </p>
            <div className="flex items-center space-x-3 text-xs text-slate-400 pt-1">
              <span className="flex items-center space-x-1">
                <Lock className="w-3.5 h-3.5 text-blue-400" />
                <span>256-bit AES</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <Award className="w-3.5 h-3.5 text-emerald-400" />
                <span>AI Proctor Verified</span>
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">Platform</h4>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/student/login" className="hover:text-blue-400 transition-colors">Student Login</Link></li>
              <li><Link to="/interviewer/login" className="hover:text-blue-400 transition-colors">Interviewer Portal</Link></li>
              <li><Link to="/admin/login" className="hover:text-blue-400 transition-colors">Admin Governance</Link></li>
              <li><Link to="/about" className="hover:text-blue-400 transition-colors">About Exam Portal</Link></li>
            </ul>
          </div>

          {/* Security & Features */}
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">AI Security</h4>
            <ul className="space-y-2.5 text-sm text-slate-400">
              <li>Eye Movement & Face Lock</li>
              <li>Browser Fullscreen Enforcer</li>
              <li>Tab Switch & Copy Guard</li>
              <li>Automated MCQ AI Generator</li>
            </ul>
          </div>

          {/* Contact Support */}
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">University Support</h4>
            <p className="text-sm text-slate-400 mb-2">Central Examination Controller Office</p>
            <p className="text-xs text-slate-400">Email: support@examportal.edu</p>
            <p className="text-xs text-slate-400">Helpline: +1 (800) 555-EXAM</p>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 space-y-2 sm:space-y-0">
          <div>
            © {new Date().getFullYear()} Exam Portal. Built for University Examinations.
          </div>
          <div className="flex items-center space-x-1">
            <span>Powered by</span>
            <span className="font-semibold text-slate-300">Secure AI Examination Core</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
