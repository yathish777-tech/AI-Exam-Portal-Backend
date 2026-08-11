import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  MOCK_UPCOMING_INTERVIEWS,
  MOCK_COMPLETED_INTERVIEWS,
  MOCK_ADMIN_STUDENTS,
  MOCK_ADMIN_INTERVIEWERS,
  MOCK_ADMIN_FEEDBACK,
  MOCK_MCQ_QUESTIONS,
} from '../utils/mockData';

const DataContext = createContext(null);

const STORAGE_KEYS = {
  INTERVIEWS: 'exam_portal_interviews_v2',
  COMPLETED: 'exam_portal_completed_v2',
  STUDENTS: 'exam_portal_students_v2',
  INTERVIEWERS: 'exam_portal_interviewers_v2',
  FEEDBACK: 'exam_portal_feedback_v2',
  SETTINGS: 'exam_portal_settings_v2',
};

export const DataProvider = ({ children }) => {
  // 1. Interviews state
  const [interviews, setInterviews] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.INTERVIEWS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    // Seed default demo interviews
    return MOCK_UPCOMING_INTERVIEWS.map((item) => ({
      ...item,
      createdBy: 'int_01',
      createdByEmail: 'interviewer@examportal.edu',
      assignedStudents: ['std_01', 'ALL'], // std_01 is demo student
      targetDepartment: 'Computer Science & Engineering',
      targetBatch: '2026',
      questions: MOCK_MCQ_QUESTIONS,
    }));
  });

  // 2. Completed Interviews / Submissions
  const [completedInterviews, setCompletedInterviews] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.COMPLETED);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return MOCK_COMPLETED_INTERVIEWS.map((item) => ({
      ...item,
      studentId: 'std_01',
      studentEmail: 'student@examportal.edu',
    }));
  });

  // 3. Students List
  const [students, setStudents] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.STUDENTS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return MOCK_ADMIN_STUDENTS;
  });

  // 4. Interviewers List
  const [interviewers, setInterviewers] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.INTERVIEWERS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return MOCK_ADMIN_INTERVIEWERS;
  });

  // 5. Feedbacks
  const [feedbacks, setFeedbacks] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.FEEDBACK);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return MOCK_ADMIN_FEEDBACK;
  });

  // 6. Settings
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return {
      strictness: 'High',
      maxWarnings: 3,
      examDuration: 45,
      fullscreenLock: true,
    };
  });

  // Sync state to local storage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.INTERVIEWS, JSON.stringify(interviews));
  }, [interviews]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.COMPLETED, JSON.stringify(completedInterviews));
  }, [completedInterviews]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(students));
  }, [students]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.INTERVIEWERS, JSON.stringify(interviewers));
  }, [interviewers]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.FEEDBACK, JSON.stringify(feedbacks));
  }, [feedbacks]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
  }, [settings]);

  // Actions
  const createInterview = (interviewPayload) => {
    const newInterview = {
      id: `int_pdf_${Date.now()}`,
      status: 'Ready',
      date: new Date().toISOString().split('T')[0],
      time: '10:00 AM IST',
      ...interviewPayload,
    };
    setInterviews((prev) => [newInterview, ...prev]);
    return newInterview;
  };

  const deleteInterview = (id) => {
    setInterviews((prev) => prev.filter((item) => item.id !== id));
  };

  const submitExamResult = (resultPayload) => {
    const newResult = {
      id: `comp_${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      totalMarks: 100,
      status: resultPayload.marks >= 70 ? 'Passed' : 'Needs Retake',
      ...resultPayload,
    };
    setCompletedInterviews((prev) => [newResult, ...prev]);
    // Remove completed interview from upcoming for this student
    setInterviews((prev) => prev.filter((item) => item.id !== resultPayload.interviewId));
    return newResult;
  };

  // Student Admin Operations
  const addStudent = (studentData) => {
    const newStudent = {
      id: `st_${Date.now()}`,
      status: 'Active',
      examsTaken: 0,
      avgScore: 'N/A',
      ...studentData,
    };
    setStudents((prev) => [newStudent, ...prev]);
    return newStudent;
  };

  const deleteStudent = (id) => {
    setStudents((prev) => prev.filter((s) => s.id !== id));
  };

  const toggleStudentStatus = (id) => {
    setStudents((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: s.status === 'Active' ? 'Suspended' : 'Active' } : s))
    );
  };

  // Interviewer Admin Operations
  const addInterviewer = (interviewerData) => {
    const newInterviewer = {
      id: `int_${Date.now()}`,
      status: 'Active',
      examsCreated: 0,
      rating: '5.0/5',
      ...interviewerData,
    };
    setInterviewers((prev) => [newInterviewer, ...prev]);
    return newInterviewer;
  };

  const deleteInterviewer = (id) => {
    setInterviewers((prev) => prev.filter((i) => i.id !== id));
  };

  const toggleInterviewerStatus = (id) => {
    setInterviewers((prev) =>
      prev.map((i) => (i.id === id ? { ...i, status: i.status === 'Active' ? 'Pending Approval' : 'Active' } : i))
    );
  };

  // Feedback Operations
  const addFeedback = (feedbackPayload) => {
    const newFb = {
      id: `fb_${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      status: 'Reviewed',
      ...feedbackPayload,
    };
    setFeedbacks((prev) => [newFb, ...prev]);
  };

  const resolveFeedback = (id) => {
    setFeedbacks((prev) =>
      prev.map((fb) => (fb.id === id ? { ...fb, status: 'Resolved' } : fb))
    );
  };

  // Settings
  const updateSettings = (newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  return (
    <DataContext.Provider
      value={{
        interviews,
        completedInterviews,
        students,
        interviewers,
        feedbacks,
        settings,
        createInterview,
        deleteInterview,
        submitExamResult,
        addCompletedInterview: submitExamResult,
        addStudent,
        deleteStudent,
        toggleStudentStatus,
        addInterviewer,
        deleteInterviewer,
        toggleInterviewerStatus,
        addFeedback,
        resolveFeedback,
        updateSettings,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};
