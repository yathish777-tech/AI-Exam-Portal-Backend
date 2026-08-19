import React, { useState } from 'react';
import { Mail, Phone, MapPin, Send, CheckCircle2 } from 'lucide-react';
import { storage } from '../../utils/storage';

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    university: '',
    subject: 'University Onboarding Inquiry',
    message: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    storage.addFeedback({
      id: 'fb_' + Date.now(),
      user: `${formData.name} (${formData.university || 'Visitor'})`,
      role: 'Inquiry',
      category: formData.subject,
      rating: 5,
      message: formData.message,
      date: new Date().toISOString().split('T')[0],
      status: 'Reviewed',
    });
    setSubmitted(true);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-10 text-slate-800 font-sans">
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">University Support & Technical Desk</h1>
        <p className="text-slate-500 text-xs sm:text-sm">Reach out regarding institutional deployment, exam policies, or student assistance.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Contact Info Cards */}
        <div className="space-y-3">
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs space-y-1">
            <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
              <Mail className="w-4 h-4 text-emerald-600" />
              <span>Email Support</span>
            </div>
            <p className="text-xs text-slate-600">support@examportal.edu</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs space-y-1">
            <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
              <Phone className="w-4 h-4 text-emerald-600" />
              <span>Institutional Desk</span>
            </div>
            <p className="text-xs text-slate-600">+1 (800) 555-EXAM</p>
            <p className="text-[11px] text-slate-400">Mon - Fri: 8 AM - 6 PM IST</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs space-y-1">
            <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
              <MapPin className="w-4 h-4 text-emerald-600" />
              <span>Academic Computing</span>
            </div>
            <p className="text-xs text-slate-600">Department of Computer Science & Engineering</p>
          </div>
        </div>

        {/* Form */}
        <div className="md:col-span-2 bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs">
          {submitted ? (
            <div className="text-center py-8 space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
              <h3 className="text-base font-bold text-slate-900">Inquiry Submitted</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Thank you for contacting the examination governance team. We will review your request and respond to your email shortly.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-200 rounded-lg hover:bg-slate-200 transition-colors"
              >
                Send Another Inquiry
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Your Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                    placeholder="e.g. Prof. R. Ramanujan"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                    placeholder="ramanujan@university.edu"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Department / University
                </label>
                <input
                  type="text"
                  value={formData.university}
                  onChange={(e) => setFormData({ ...formData, university: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                  placeholder="State Engineering College"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Inquiry Details
                </label>
                <textarea
                  rows={4}
                  required
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:outline-hidden focus:border-emerald-600 focus:bg-white"
                  placeholder="Describe your inquiry..."
                />
              </div>

              <div className="flex justify-end pt-1">
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg shadow-xs flex items-center space-x-1.5 transition-colors"
                >
                  <span>Submit Inquiry</span>
                  <Send className="w-3.5 h-3.5 text-emerald-400" />
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
