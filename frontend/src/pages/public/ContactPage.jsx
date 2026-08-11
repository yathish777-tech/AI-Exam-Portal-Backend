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
    <div className="max-w-5xl mx-auto px-4 py-12 space-y-10 text-slate-100">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white">Contact University Support Team</h1>
        <p className="text-slate-400 text-sm">Have questions about setting up Exam Portal at your university?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Contact Info Cards */}
        <div className="space-y-4">
          <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-md space-y-2">
            <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
              <Mail className="w-4 h-4" />
              <span>Email Support</span>
            </div>
            <p className="text-xs text-slate-400">support@examportal.edu</p>
            <p className="text-xs text-slate-400">admissions@examportal.edu</p>
          </div>

          <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-md space-y-2">
            <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
              <Phone className="w-4 h-4" />
              <span>Helpline Desk</span>
            </div>
            <p className="text-xs text-slate-400">+1 (800) 555-EXAM</p>
            <p className="text-xs text-slate-400">Mon - Fri: 8 AM - 8 PM IST</p>
          </div>

          <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-md space-y-2">
            <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
              <MapPin className="w-4 h-4" />
              <span>Examination Board HQ</span>
            </div>
            <p className="text-xs text-slate-400">Academic Block 4, University Heights</p>
            <p className="text-xs text-slate-400">Technology Park, Campus City</p>
          </div>
        </div>

        {/* Form */}
        <div className="md:col-span-2 bg-slate-900/90 rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-xl text-slate-100">
          {submitted ? (
            <div className="text-center py-10 space-y-4">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
              <h3 className="text-lg font-bold text-white">Message Sent Successfully!</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Thank you for contacting the Exam Portal support team. Our examination desk will get back to your email within 24 hours.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="px-4 py-2 text-xs font-semibold text-blue-300 bg-blue-950/80 border border-blue-800 rounded-xl hover:bg-blue-900/80 transition-colors"
              >
                Send Another Inquiry
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Your Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3.5 py-2 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-blue-500"
                    placeholder="Dr. Aarav Sharma"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3.5 py-2 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-blue-500"
                    placeholder="aarav@university.edu"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  University / Organization
                </label>
                <input
                  type="text"
                  value={formData.university}
                  onChange={(e) => setFormData({ ...formData, university: e.target.value })}
                  className="w-full px-3.5 py-2 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-blue-500"
                  placeholder="State Technological University"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Message Details
                </label>
                <textarea
                  rows={4}
                  required
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="w-full px-3.5 py-2 text-sm bg-slate-950/80 border border-slate-800 text-slate-100 rounded-xl focus:bg-slate-900 focus:outline-hidden focus:border-blue-500"
                  placeholder="Tell us about your examination requirements or questions..."
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2 transition-all"
              >
                <span>Submit Inquiry</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
