import React, { useState } from 'react';
import { ChevronDown, HelpCircle, Search } from 'lucide-react';

export default function FAQPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [openIndex, setOpenIndex] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const faqs = [
    {
      category: 'student',
      question: 'What hardware and software is required to take an examination?',
      answer: 'You require a laptop or desktop computer with a functional webcam, microphone, Google Chrome or Microsoft Edge browser, and a stable internet connection. No external application installations or plugins are required.',
    },
    {
      category: 'student',
      question: 'What happens if my network drops during an active test session?',
      answer: 'Your responses are automatically synced to local session storage continuously. If disconnected, simply re-open or reload the examination page—your selected answers and remaining timer state will resume automatically.',
    },
    {
      category: 'student',
      question: 'What events trigger an AI proctoring warning?',
      answer: 'Warnings are recorded if the candidate switches browser tabs, exits full-screen mode, looks away from the screen for prolonged intervals, if no face is detected, or if multiple people enter the camera frame.',
    },
    {
      category: 'interviewer',
      question: 'How do faculty examiners create and activate their accounts?',
      answer: 'Interviewer accounts are provisioned exclusively by University Administrators. When an invitation is issued, the faculty member receives an OTP to activate their account and set their password.',
    },
    {
      category: 'interviewer',
      question: 'How does automated question paper conversion work?',
      answer: 'Faculty examiners can upload syllabus or question PDF documents. The system parses question stems, options, and key concepts to generate standardized multiple-choice assessments.',
    },
    {
      category: 'admin',
      question: 'How are institution-wide strictness and security limits configured?',
      answer: 'Administrators can configure warning thresholds, enforce full-screen locks, manage student enrollments, issue interviewer invitations, and review complete violation telemetry logs from the Admin Governance console.',
    },
  ];

  const filteredFaqs = faqs.filter((item) => {
    const matchesCategory = activeCategory === 'all' || item.category === activeCategory;
    const matchesSearch = item.question.toLowerCase().includes(searchQuery.toLowerCase()) || item.answer.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-8 text-slate-800 font-sans">
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Frequently Asked Questions</h1>
        <p className="text-slate-500 text-xs sm:text-sm">Information regarding proctored examinations, faculty workflows, and system governance.</p>
      </div>

      {/* Search & Category Filter */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search keywords (e.g. webcam, full-screen, invitation)..."
            className="w-full pl-9 pr-4 py-2.5 text-xs bg-white border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-hidden focus:border-emerald-600 shadow-xs"
          />
        </div>

        <div className="flex space-x-2 text-xs font-semibold">
          {['all', 'student', 'interviewer', 'admin'].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1.5 rounded-lg border text-xs capitalize transition-colors ${
                activeCategory === cat ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {cat === 'all' ? 'All Questions' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* FAQ Accordion List */}
      <div className="space-y-2.5">
        {filteredFaqs.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden transition-all">
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full flex items-center justify-between p-4 text-left font-semibold text-slate-900 text-xs sm:text-sm hover:bg-slate-50 transition-colors"
              >
                <span className="flex items-center space-x-2.5">
                  <HelpCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{faq.question}</span>
                </span>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
              </button>

              {isOpen && (
                <div className="px-4 pb-4 pt-1 text-xs text-slate-600 leading-relaxed border-t border-slate-100 bg-slate-50/50">
                  {faq.answer}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
