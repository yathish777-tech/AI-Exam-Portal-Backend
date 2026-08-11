import React from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap,
  UserCheck,
  FileCheck2,
  Award,
  Activity,
  BarChart3,
  MessageSquare,
  Sparkles,
} from 'lucide-react';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import { useData } from '../../context/DataContext';

export default function AdminDashboard() {
  const { students, interviewers, completedInterviews, feedbacks } = useData();

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header Card */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-slate-100 border border-slate-200 rounded-md text-xs font-medium text-slate-700">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Central Examination Board Governance</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            University Admin Control Center
          </h2>
          <p className="text-xs text-slate-500 max-w-xl">
            Real-time university examination health, faculty management, and AI proctor security auditing.
          </p>
        </div>

        <div className="shrink-0 flex items-center gap-2">
          <Link
            to="/admin/reports"
            className="px-4 py-2.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs transition-colors flex items-center space-x-2"
          >
            <BarChart3 className="w-4 h-4 text-blue-400" />
            <span>View Analytics Reports</span>
          </Link>
        </div>
      </div>

      {/* Admin Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Registered Candidates"
          value={students.length}
          icon={GraduationCap}
          color="blue"
          description="Active Student Roster"
        />

        <StatCard
          title="Faculty Examiners"
          value={interviewers.length}
          icon={UserCheck}
          color="indigo"
          description="Approved Interviewers"
        />

        <StatCard
          title="Evaluations Logged"
          value={completedInterviews.length}
          icon={FileCheck2}
          color="emerald"
          description="Completed Examinations"
        />

        <StatCard
          title="University Average"
          value="84.2%"
          icon={Award}
          color="amber"
          description="Overall Assessment Grade"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Live System Activity Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-600" />
              <span>Live Governance Audit Feed</span>
            </h3>
            <span className="text-[11px] text-slate-500 font-medium">Auto-refresh active</span>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-3 text-xs">
            {[
              {
                time: '10 Mins ago',
                type: 'Student Submission',
                desc: 'Aarav Sharma completed Advanced Data Structures Exam (Score: 92%)',
                badge: 'emerald',
              },
              {
                time: '35 Mins ago',
                type: 'Material Upload',
                desc: 'Dr. Priya Ramesh uploaded DSA_Unit2_Exam.pdf (Generated 5 MCQs)',
                badge: 'indigo',
              },
              {
                time: '1 Hr ago',
                type: 'Proctoring Warning',
                desc: 'Focus loss warning logged for Candidate Vikram Singh',
                badge: 'amber',
              },
              {
                time: '2 Hrs ago',
                type: 'Faculty Verification',
                desc: 'Prof. Rajesh Khanna approved as Chief Examiner for DSA Domain',
                badge: 'blue',
              },
            ].map((act, idx) => (
              <div key={idx} className="p-3 bg-slate-50 border border-slate-100 rounded-lg flex items-start justify-between space-x-3">
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2">
                    <Badge variant={act.badge}>{act.type}</Badge>
                    <span className="text-[10px] text-slate-400 font-medium">{act.time}</span>
                  </div>
                  <p className="text-slate-800 font-medium pt-1">{act.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Feedback Summary */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-blue-600" />
              <span>Recent Feedback</span>
            </h3>
            <Link to="/admin/feedback" className="text-xs font-semibold text-blue-600 hover:underline">
              View All ({feedbacks.length}) →
            </Link>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-3 text-xs">
            {feedbacks.length === 0 ? (
              <p className="text-slate-500 text-xs py-2">No user feedback submitted yet.</p>
            ) : (
              feedbacks.slice(0, 2).map((fb) => (
                <div key={fb.id} className="p-3 bg-slate-50 border border-slate-100 rounded-lg space-y-1.5">
                  <div className="flex items-center justify-between font-bold text-slate-800">
                    <span>{fb.user}</span>
                    <span className="text-amber-600 font-semibold">★ {fb.rating}/5</span>
                  </div>
                  <p className="text-slate-600 text-[11px] leading-relaxed">{fb.message}</p>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

