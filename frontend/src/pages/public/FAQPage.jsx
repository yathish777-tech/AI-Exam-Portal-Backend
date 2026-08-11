import React, { useState } from 'react';
import { ChevronDown, HelpCircle, Search } from 'lucide-react';

export default function FAQPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [openIndex, setOpenIndex] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const faqs = [
    {
      category: 'student',
      question: 'What hardware/software is required to take an exam on Exam Portal?',
      answer: 'You need a standard laptop or desktop computer with a functional webcam, microphone, Google Chrome or Edge browser, and a stable internet connection. No separate software download is required.',
    },
    {
      category: 'student',
      question: 'What happens if my internet disconnects during an active exam?',
      answer: 'Your responses are automatically saved in local browser cache every 5 seconds. If the connection drops, simply refresh the page or reconnect—your answers and remaining timer state will be restored automatically.',
    },
    {
      category: 'student',
      question: 'What triggers an AI proctoring warning during the test?',
      answer: 'Warnings are triggered by tab switching, exiting fullscreen mode, turning your face away from the camera, multiple faces appearing in the webcam feed, or attempting keyboard shortcuts like Copy/Paste.',
    },
    {
      category: 'interviewer',
      question: 'How does the PDF to MCQ conversion work for examiners?',
      answer: 'Professors simply upload their question set in PDF format. The backend AI service analyzes syllabus sections, formats question stems, creates 4 distinct plausible options, and compiles the final test paper.',
    },
    {
      category: 'interviewer',
      question: 'Can I review candidate proctoring logs and flags after an exam?',
      answer: 'Yes! Interviewers have access to candidate report sheets showing violation timelines, snapshot flags, overall proctor cleanliness percentages, and detailed test breakdown.',
    },
    {
      category: 'admin',
      question: 'How are student accounts and permissions managed?',
      answer: 'Admins can manage students and interviewers via the Admin Control Panel, filter by department, review system health metrics, and suspend or approve accounts in real-time.',
    },
  ];

  const filteredFaqs = faqs.filter((item) => {
    const matchesCategory = activeCategory === 'all' || item.category === activeCategory;
    const matchesSearch = item.question.toLowerCase().includes(searchQuery.toLowerCase()) || item.answer.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8 text-slate-100">
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-extrabold text-white">Frequently Asked Questions</h1>
        <p className="text-slate-400 text-sm">Find answers to common questions about student exams, PDF uploads, and AI proctoring.</p>
      </div>

      {/* Search & Category Filter */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search FAQ keywords (e.g. webcam, tab switch, PDF upload)..."
            className="w-full pl-10 pr-4 py-3 text-sm bg-slate-900/90 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-xl focus:outline-hidden focus:border-blue-500 shadow-xs"
          />
        </div>

        <div className="flex space-x-2 text-xs font-semibold">
          {['all', 'student', 'interviewer', 'admin'].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3.5 py-1.5 rounded-lg border uppercase tracking-wider transition-colors ${
                activeCategory === cat ? 'bg-blue-600 text-white border-blue-600' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* FAQ Accordion List */}
      <div className="space-y-3">
        {filteredFaqs.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="bg-slate-900/90 rounded-2xl border border-slate-800 overflow-hidden transition-all text-slate-100">
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full flex items-center justify-between p-5 text-left font-semibold text-slate-100 text-sm hover:bg-slate-800/60 transition-colors"
              >
                <span className="flex items-center space-x-3">
                  <HelpCircle className="w-4 h-4 text-blue-400 shrink-0" />
                  <span>{faq.question}</span>
                </span>
                <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
              </button>

              {isOpen && (
                <div className="px-5 pb-5 pt-1 text-xs text-slate-400 leading-relaxed border-t border-slate-800 bg-slate-950/50">
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
