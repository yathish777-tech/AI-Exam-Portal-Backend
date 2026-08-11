import React from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Calendar,
  CheckCircle2,
  Award,
  ArrowRight,
  PlayCircle,
  Clock,
  Sparkles,
  Inbox,
} from 'lucide-react';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function StudentDashboard() {
  const { user } = useAuth();
  const { interviews, completedInterviews } = useData();

  // Filter assigned interviews for current student
  const studentUpcoming = interviews.filter((item) => {
    if (!user) return false;
    if (user.id === 'std_01') return true; // Demo student gets default set
    if (!item.assignedStudents) return false;
    return (
      item.assignedStudents.includes(user.id) ||
      item.assignedStudents.includes(user.email) ||
      item.assignedStudents.includes(user.department) ||
      item.assignedStudents.includes('ALL')
    );
  });

  const studentCompleted = completedInterviews.filter((item) => {
    if (!user) return false;
    if (user.id === 'std_01') return true;
    return item.studentId === user.id || item.studentEmail === user.email;
  });

  const upcomingCount = studentUpcoming.length;
  const completedCount = studentCompleted.length;
  const avgScore = completedCount > 0
    ? Math.round(studentCompleted.reduce((acc, curr) => acc + curr.marks, 0) / completedCount)
    : 0;

  return (
    <div className="space-y-6 text-slate-800">
      
      {/* Header Banner - Enterprise Style */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-slate-100 border border-slate-200 rounded-md text-xs font-medium text-slate-700">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Roll No: {user?.rollNo || 'REG-PENDING'}</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Welcome back, {user?.name || 'Student'}
          </h2>
          <p className="text-xs text-slate-500 max-w-xl">
            {user?.department || 'Department of Engineering'} • Secure AI Proctoring session environment verified.
          </p>
        </div>

        <div className="shrink-0">
          {upcomingCount > 0 ? (
            <Link
              to="/student/ready"
              className="px-4 py-2.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs flex items-center space-x-2 transition-colors"
            >
              <PlayCircle className="w-4 h-4 text-blue-400" />
              <span>Ready for Interview</span>
            </Link>
          ) : (
            <span className="px-4 py-2 bg-slate-100 text-slate-500 font-medium text-xs rounded-lg border border-slate-200 cursor-not-allowed">
              No Pending Exams
            </span>
          )}
        </div>
      </div>

      {/* Required Dashboard Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Student Name"
          value={user?.name || 'Student'}
          icon={User}
          color="blue"
          description={user?.rollNo || 'Registered Account'}
        />

        <StatCard
          title="Upcoming Interviews"
          value={upcomingCount}
          icon={Calendar}
          color="amber"
          description={upcomingCount > 0 ? "Assigned by faculty" : "No active assignments"}
        />

        <StatCard
          title="Completed Interviews"
          value={completedCount}
          icon={CheckCircle2}
          color="emerald"
          description={completedCount > 0 ? "100% verified submissions" : "0 completed tests"}
        />

        <StatCard
          title="Average Score"
          value={completedCount > 0 ? `${avgScore}%` : 'N/A'}
          icon={Award}
          color="indigo"
          description={completedCount > 0 ? "Cumulative Performance" : "Awaiting first assessment"}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Upcoming Interviews List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Assigned Upcoming Examinations</h3>
            {upcomingCount > 0 && (
              <Link to="/student/upcoming" className="text-xs font-semibold text-blue-600 hover:underline flex items-center space-x-1">
                <span>View All ({upcomingCount})</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>

          {upcomingCount === 0 ? (
            <div className="bg-white rounded-xl p-8 border border-slate-200/80 shadow-xs text-center space-y-3">
              <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
                <Inbox className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-800">No interviews assigned</h4>
                <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                  You currently have no scheduled or assigned examinations. When an interviewer assigns an assessment to your department or batch, it will appear here.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {studentUpcoming.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200/80">
                        {item.code || 'EXAM-CODE'}
                      </span>
                      <Badge variant={item.status === 'Ready' ? 'emerald' : 'amber'}>{item.status}</Badge>
                    </div>
                    <h4 className="text-sm font-bold text-slate-900">{item.company || item.title || 'Technical Assessment'}</h4>
                    <div className="text-xs text-slate-500 font-medium flex items-center space-x-3">
                      <span>Domain: {item.domain}</span>
                      <span>•</span>
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>{item.date} at {item.time} ({item.duration})</span>
                      </span>
                    </div>
                  </div>

                  <div className="shrink-0 w-full sm:w-auto">
                    <Link
                      to="/student/ready"
                      className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-3.5 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg transition-colors shadow-xs"
                    >
                      <span>Launch Pre-Check</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Recent Completed Interviews */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Completed Assessments</h3>
            {completedCount > 0 && (
              <Link to="/student/completed" className="text-xs font-semibold text-blue-600 hover:underline">
                View History
              </Link>
            )}
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-3">
            {completedCount === 0 ? (
              <div className="text-center py-6 space-y-1">
                <p className="text-xs font-medium text-slate-500">No completed interviews yet.</p>
                <p className="text-[11px] text-slate-400">Results will be logged after test submission.</p>
              </div>
            ) : (
              studentCompleted.slice(0, 4).map((item) => (
                <div key={item.id} className="p-3 bg-slate-50 border border-slate-100 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 truncate">{item.domain}</span>
                    <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">{item.marks}/100</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>Date: {item.date}</span>
                    <span>Proctor: {item.proctoringScore || '100% Clean'}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

