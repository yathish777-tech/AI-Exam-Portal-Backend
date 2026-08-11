import React from 'react';
import { Link } from 'react-router-dom';
import {
  UserCheck,
  BookOpen,
  Calendar,
  Users,
  Award,
  Upload,
  Trophy,
  Sparkles,
} from 'lucide-react';
import StatCard from '../../components/ui/StatCard';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function InterviewerDashboard() {
  const { user } = useAuth();
  const { students, interviews, completedInterviews } = useData();

  const totalCandidates = students.filter(s => s.status === 'Approved' || s.status === 'Active').length;
  const totalExams = interviews.length;

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header Card */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-slate-100 border border-slate-200 rounded-md text-xs font-medium text-slate-700">
            <BookOpen className="w-3.5 h-3.5 text-blue-600" />
            <span>Assigned Domain: {user?.domain || 'Artificial Intelligence & Data Science'}</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Welcome, {user?.name || 'Interviewer'}
          </h2>
          <p className="text-xs text-slate-500 max-w-xl">
            {user?.department || 'Department of Computer Science'} • Examiner Control Workstation
          </p>
        </div>

        <div className="shrink-0">
          <Link
            to="/interviewer/upload"
            className="px-4 py-2.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs flex items-center space-x-2 transition-colors"
          >
            <Upload className="w-4 h-4 text-blue-400" />
            <span>Upload Exam Materials</span>
          </Link>
        </div>
      </div>

      {/* Dashboard Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Examiner Name"
          value={user?.name?.split(' ')[0] || 'Faculty'}
          icon={UserCheck}
          color="blue"
          description={user?.domain || 'AI & DS'}
        />

        <StatCard
          title="Assigned Domain"
          value={user?.domain?.split(' ')[0] || 'Computer Science'}
          icon={BookOpen}
          color="indigo"
          description="CS & AI Dept"
        />

        <StatCard
          title="Active Exams"
          value={`${totalExams} Tests`}
          icon={Calendar}
          color="amber"
          description="Assigned to students"
        />

        <StatCard
          title="Total Candidates"
          value={totalCandidates}
          icon={Users}
          color="emerald"
          description="Registered students"
        />

        <StatCard
          title="Evaluations"
          value={completedInterviews.length}
          icon={Award}
          color="purple"
          description="Completed logs"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Columns: PDF Upload Card & Leaderboard Preview */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">PDF Question Set Generator</h3>
              </div>
              <Link to="/interviewer/upload" className="text-xs font-semibold text-blue-600 hover:underline">
                Upload Workstation →
              </Link>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Upload course syllabus, study guides, or examination PDFs. The generator converts materials into structured 4-option multiple-choice questions (MCQs) and allows assigning them directly to candidate cohorts.
            </p>

            <Link
              to="/interviewer/upload"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg transition-colors shadow-xs"
            >
              <Upload className="w-4 h-4" />
              <span>Launch Question Builder</span>
            </Link>
          </div>

          {/* Quick Leaderboard Preview */}
          <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Trophy className="w-4 h-4 text-amber-500" />
                <span>Domain Rank Leaderboard</span>
              </h3>
              <Link to="/interviewer/leaderboard" className="text-xs font-semibold text-blue-600 hover:underline">
                Full Rankings →
              </Link>
            </div>

            <div className="space-y-2 text-xs">
              {completedInterviews.length === 0 ? (
                <p className="text-slate-500 text-xs py-2">No completed assessments logged yet.</p>
              ) : (
                completedInterviews.slice(0, 3).map((r, index) => (
                  <div key={r.id || index} className="p-3 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="w-6 h-6 rounded bg-amber-100 text-amber-800 font-bold text-[11px] flex items-center justify-center">
                        #{index + 1}
                      </span>
                      <span className="font-bold text-slate-800">{r.studentName || 'Student Candidate'}</span>
                    </div>
                    <span className="font-bold text-blue-700">{r.marks}/100</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Active Exams */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Current Assigned Modules</h3>
          <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-3 text-xs">
            {interviews.length === 0 ? (
              <p className="text-xs text-slate-500 py-2">No active exam modules.</p>
            ) : (
              interviews.slice(0, 4).map((item) => (
                <div key={item.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 space-y-1">
                  <div className="font-bold text-slate-800">{item.company || item.title}</div>
                  <div className="text-[11px] text-slate-500">{item.domain} • {item.date} • {item.status}</div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

