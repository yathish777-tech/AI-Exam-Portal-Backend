import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import PublicLayout from '../components/layout/PublicLayout';
import StudentLayout from '../components/layout/StudentLayout';
import InterviewerLayout from '../components/layout/InterviewerLayout';
import AdminLayout from '../components/layout/AdminLayout';

// Public Pages
import LandingPage from '../pages/public/LandingPage';
import AboutPage from '../pages/public/AboutPage';
import ContactPage from '../pages/public/ContactPage';
import FAQPage from '../pages/public/FAQPage';

// Auth Pages
import StudentLogin from '../pages/auth/StudentLogin';
import StudentRegister from '../pages/auth/StudentRegister';
import InterviewerLogin from '../pages/auth/InterviewerLogin';
import InterviewerRegister from '../pages/auth/InterviewerRegister';
import AdminLogin from '../pages/auth/AdminLogin';

// Student Pages
import StudentDashboard from '../pages/student/StudentDashboard';
import UpcomingInterviews from '../pages/student/UpcomingInterviews';
import CompletedInterviews from '../pages/student/CompletedInterviews';
import InterviewInstructions from '../pages/student/InterviewInstructions';
import MCQTestPage from '../pages/student/MCQTestPage';
import StudentProfile from '../pages/student/StudentProfile';
import ExamResultPage from '../pages/student/ExamResultPage';

// Interviewer Pages
import InterviewerDashboard from '../pages/interviewer/InterviewerDashboard';
import UploadQuestions from '../pages/interviewer/UploadQuestions';
import CandidatesList from '../pages/interviewer/CandidatesList';
import PastInterviews from '../pages/interviewer/PastInterviews';
import Leaderboard from '../pages/interviewer/Leaderboard';
import InterviewerProfile from '../pages/interviewer/InterviewerProfile';

// Admin Pages
import AdminDashboard from '../pages/admin/AdminDashboard';
import ManageStudents from '../pages/admin/ManageStudents';
import ManageInterviewers from '../pages/admin/ManageInterviewers';
import SystemReports from '../pages/admin/SystemReports';
import FeedbackList from '../pages/admin/FeedbackList';
import SystemSettings from '../pages/admin/SystemSettings';

// Protected Route Guard
import ProtectedRoute from './ProtectedRoute';

export default function AppRoutes() {
  return (
    <Routes>
      
      {/* Public Pages */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/faq" element={<FAQPage />} />
      </Route>

      {/* Auth Pages */}
      <Route path="/student/login" element={<StudentLogin />} />
      <Route path="/student/register" element={<StudentRegister />} />
      <Route path="/interviewer/login" element={<InterviewerLogin />} />
      <Route path="/interviewer/register" element={<InterviewerRegister />} />
      <Route path="/admin/login" element={<AdminLogin />} />

      {/* Student Protected Routes */}
      <Route element={<ProtectedRoute allowedRole="student" />}>
        <Route element={<StudentLayout />}>
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="/student/upcoming" element={<UpcomingInterviews />} />
          <Route path="/student/completed" element={<CompletedInterviews />} />
          <Route path="/student/ready" element={<InterviewInstructions />} />
          <Route path="/student/ready/:interviewId" element={<InterviewInstructions />} />
          <Route path="/student/profile" element={<StudentProfile />} />
          <Route path="/student/results/:resultId" element={<ExamResultPage />} />
        </Route>
        {/* Full screen MCQ Test Interface */}
        <Route path="/student/exam/:interviewId" element={<MCQTestPage />} />
      </Route>

      {/* Interviewer Protected Routes */}
      <Route element={<ProtectedRoute allowedRole="interviewer" />}>
        <Route element={<InterviewerLayout />}>
          <Route path="/interviewer/dashboard" element={<InterviewerDashboard />} />
          <Route path="/interviewer/upload" element={<UploadQuestions />} />
          <Route path="/interviewer/candidates" element={<CandidatesList />} />
          <Route path="/interviewer/past" element={<PastInterviews />} />
          <Route path="/interviewer/leaderboard" element={<Leaderboard />} />
          <Route path="/interviewer/profile" element={<InterviewerProfile />} />
        </Route>
      </Route>

      {/* Admin Protected Routes */}
      <Route element={<ProtectedRoute allowedRole="admin" />}>
        <Route element={<AdminLayout />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/students" element={<ManageStudents />} />
          <Route path="/admin/interviewers" element={<ManageInterviewers />} />
          <Route path="/admin/reports" element={<SystemReports />} />
          <Route path="/admin/feedback" element={<FeedbackList />} />
          <Route path="/admin/settings" element={<SystemSettings />} />
        </Route>
      </Route>

      {/* Fallback Route */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}
