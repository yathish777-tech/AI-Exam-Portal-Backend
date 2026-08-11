import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Trophy,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  AlertTriangle,
  ArrowLeft,
  LayoutDashboard,
  Award,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  User,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function ExamResultPage() {
  const { resultId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { completedInterviews } = useData();

  const [expandedQuestions, setExpandedQuestions] = useState(false);

  // Find result by ID or fallback to the latest completed interview
  const result =
    completedInterviews.find((item) => item.id === resultId) ||
    completedInterviews[0] ||
    null;

  if (!result) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center space-y-4 text-slate-800">
        <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
          <FileText className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">No Examination Result Found</h2>
        <p className="text-xs text-slate-500">
          We couldn't locate the requested scorecard record in your session database.
        </p>
        <Link
          to="/student/dashboard"
          className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-900 text-white font-medium text-xs rounded-md shadow-xs"
        >
          <LayoutDashboard className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  const studentName = result.studentName || user?.name || 'Aarav Sharma';
  const rollNo = result.rollNo || user?.rollNo || 'CS2026-089';
  const interviewName = result.company || result.title || 'Data Structures & Algorithms Final Examination';
  const examCode = result.code || 'DSA-CS301';
  const domain = result.domain || 'Data Structures & Algorithms';

  const marks = result.marks ?? 80;
  const totalMarks = result.totalMarks ?? 100;
  const percentage = result.percentage ?? Math.round((marks / totalMarks) * 100);

  const correctAnswers = result.correctAnswers ?? Math.round((marks / 100) * (result.totalQuestions || 10));
  const totalQuestions = result.totalQuestions ?? 10;
  const wrongAnswers = result.wrongAnswers ?? (totalQuestions - correctAnswers - (result.unanswered || 0));
  const unanswered = result.unanswered ?? 0;

  const timeTaken = result.timeTaken || '14 Mins 20 Secs';
  const violationsList = result.violationsList || [];
  const violationsCount = result.violationsCount ?? violationsList.length;

  const isPassed = marks >= 70 && violationsCount < 3;

  return (
    <div className="max-w-4xl mx-auto space-y-6 text-slate-800 py-2">
      
      {/* Top Banner / Breadcrumb */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/student/completed')}
          className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Completed Exams</span>
        </button>

        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
          Official Scorecard • {result.date || new Date().toISOString().split('T')[0]}
        </span>
      </div>

      {/* Hero Performance Card */}
      <div className="bg-white rounded-xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-6">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-100">
                {examCode}
              </span>
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded ${
                isPassed ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                {result.status || (isPassed ? 'Passed' : 'Needs Retake')}
              </span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight mt-1">{interviewName}</h1>
            <p className="text-xs text-slate-500 flex items-center space-x-2">
              <User className="w-3.5 h-3.5 text-slate-400" />
              <span>Candidate: <strong className="text-slate-700">{studentName}</strong> ({rollNo})</span>
              <span>•</span>
              <span>Domain: <strong className="text-slate-700">{domain}</strong></span>
            </p>
          </div>

          <div className="text-left sm:text-right bg-slate-50 p-4 rounded-xl border border-slate-200/80 shrink-0">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Final Score</span>
            <div className="text-3xl font-extrabold text-blue-600 mt-0.5">
              {marks} <span className="text-sm font-semibold text-slate-400">/ {totalMarks}</span>
            </div>
            <span className="text-xs font-bold text-slate-600">{percentage}% Aggregate</span>
          </div>
        </div>

        {/* 4 Key Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 bg-emerald-50/60 border border-emerald-200/80 rounded-lg space-y-1">
            <div className="flex items-center space-x-1.5 text-emerald-800 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Correct Answers</span>
            </div>
            <p className="text-2xl font-bold text-emerald-700">{correctAnswers} <span className="text-xs font-normal text-emerald-600">/ {totalQuestions}</span></p>
            <p className="text-[10px] text-emerald-700 font-medium">{Math.round((correctAnswers / totalQuestions) * 100)}% Accuracy</p>
          </div>

          <div className="p-4 bg-red-50/60 border border-red-200/80 rounded-lg space-y-1">
            <div className="flex items-center space-x-1.5 text-red-800 text-xs font-bold">
              <XCircle className="w-4 h-4 text-red-600" />
              <span>Incorrect Answers</span>
            </div>
            <p className="text-2xl font-bold text-red-700">{wrongAnswers} <span className="text-xs font-normal text-red-600">/ {totalQuestions}</span></p>
            <p className="text-[10px] text-red-700 font-medium">{unanswered > 0 ? `${unanswered} Unanswered` : 'All Attempted'}</p>
          </div>

          <div className="p-4 bg-blue-50/60 border border-blue-200/80 rounded-lg space-y-1">
            <div className="flex items-center space-x-1.5 text-blue-800 text-xs font-bold">
              <Clock className="w-4 h-4 text-blue-600" />
              <span>Time Taken</span>
            </div>
            <p className="text-xl font-bold text-blue-700 mt-1">{timeTaken}</p>
            <p className="text-[10px] text-blue-700 font-medium">Exam Duration: 45 Mins</p>
          </div>

          <div className={`p-4 rounded-lg space-y-1 border ${
            violationsCount === 0
              ? 'bg-slate-50 border-slate-200'
              : 'bg-amber-50/60 border-amber-200/80'
          }`}>
            <div className="flex items-center space-x-1.5 text-slate-800 text-xs font-bold">
              <ShieldAlert className={`w-4 h-4 ${violationsCount === 0 ? 'text-emerald-600' : 'text-amber-600'}`} />
              <span>Proctor Flags</span>
            </div>
            <p className={`text-2xl font-bold ${violationsCount === 0 ? 'text-emerald-700' : 'text-amber-700'}`}>
              {violationsCount} <span className="text-xs font-normal text-slate-500">Violations</span>
            </p>
            <p className="text-[10px] text-slate-600 font-medium">
              {violationsCount === 0 ? '100% Clean Session' : `${result.proctoringScore || 'Warnings logged'}`}
            </p>
          </div>
        </div>

      </div>

      {/* Detailed Violations Log */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">AI Proctoring Audit Log</h3>
          </div>
          <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
            violationsCount === 0
              ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
              : 'bg-amber-50 text-amber-800 border border-amber-200'
          }`}>
            {violationsCount === 0 ? '0 Security Flags' : `${violationsCount} Security Alerts Recorded`}
          </span>
        </div>

        {violationsList.length === 0 ? (
          <div className="p-4 bg-emerald-50/60 border border-emerald-200/80 rounded-lg flex items-center space-x-3 text-emerald-800 text-xs">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <div>
              <p className="font-bold">Verified Clean Examination Session</p>
              <p className="text-[11px] text-emerald-700">
                No tab switching, camera disconnection, multi-person presence, or fullscreen exit events were detected during the assessment.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-xs text-slate-500 font-medium">
              The following proctoring events were captured during your session:
            </p>
            <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
              {violationsList.map((v, idx) => (
                <div key={idx} className="p-3 bg-slate-50/80 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2.5 text-slate-800 font-medium">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>{v.description || v.type || v.reason || 'Security Warning'}</span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                    {v.time || 'Logged'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Optional Detailed Question Breakdown Accordion */}
      {result.questions && result.questions.length > 0 && (
        <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
          <button
            onClick={() => setExpandedQuestions(!expandedQuestions)}
            className="w-full flex items-center justify-between text-left text-sm font-bold text-slate-900"
          >
            <div className="flex items-center space-x-2">
              <HelpCircle className="w-4 h-4 text-blue-600" />
              <span>Review Questions & Correct Explanations</span>
            </div>
            {expandedQuestions ? (
              <ChevronUp className="w-4 h-4 text-slate-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-500" />
            )}
          </button>

          {expandedQuestions && (
            <div className="space-y-4 pt-2">
              {result.questions.map((q, idx) => {
                const studentAns = result.userAnswers ? result.userAnswers[q.id] : undefined;
                const isCorrect = studentAns === q.correctAnswer;
                return (
                  <div key={q.id} className="p-4 bg-slate-50 border border-slate-200/80 rounded-lg space-y-3 text-xs">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-bold text-slate-900">
                        {idx + 1}. {q.question}
                      </h4>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                        isCorrect ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {isCorrect ? 'Correct' : 'Incorrect'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-700">
                      {q.options.map((opt, optIdx) => {
                        let optStyle = 'bg-white border-slate-200 text-slate-700';
                        if (optIdx === q.correctAnswer) {
                          optStyle = 'bg-emerald-50 border-emerald-300 text-emerald-900 font-bold';
                        } else if (optIdx === studentAns && !isCorrect) {
                          optStyle = 'bg-red-50 border-red-300 text-red-900 font-bold';
                        }

                        return (
                          <div key={optIdx} className={`p-2 rounded border text-[11px] ${optStyle}`}>
                            <span className="font-bold mr-1.5">{String.fromCharCode(65 + optIdx)}.</span>
                            <span>{opt}</span>
                          </div>
                        );
                      })}
                    </div>

                    {q.explanation && (
                      <p className="text-[11px] text-slate-600 bg-blue-50/70 p-2.5 rounded border border-blue-100 leading-relaxed">
                        <strong className="text-blue-900">Explanation:</strong> {q.explanation}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <Link
          to="/student/dashboard"
          className="px-5 py-2.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md shadow-xs transition-colors inline-flex items-center space-x-2"
        >
          <LayoutDashboard className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>

        <Link
          to="/student/completed"
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-md shadow-xs transition-colors inline-flex items-center space-x-2"
        >
          <Award className="w-4 h-4" />
          <span>View All Scorecards</span>
        </Link>
      </div>

    </div>
  );
}
