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
  INTERVIEWS: 'exam_portal_interviews_v3',
  COMPLETED: 'exam_portal_completed_v3',
  STUDENTS: 'exam_portal_students_v3',
  INTERVIEWERS: 'exam_portal_interviewers_v3',
  FEEDBACK: 'exam_portal_feedback_v3',
  SETTINGS: 'exam_portal_settings_v3',
  WARNING_LOGS: 'exam_portal_warning_logs_v3',
  ACTIVITY_LOGS: 'exam_portal_activity_logs_v3',
  PENDING_RESETS: 'exam_portal_pending_resets_v3',
};

export const DataProvider = ({ children }) => {
  // 1. Interviews state
  const [interviews, setInterviews] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.INTERVIEWS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return MOCK_UPCOMING_INTERVIEWS.map((item) => ({
      ...item,
      createdBy: 'int_01',
      createdByEmail: 'interviewer@examportal.edu',
      assignedStudents: ['std_01', 'ALL'],
      targetDepartment: 'Computer Science & Engineering',
      targetBatch: '2026',
      questions: MOCK_MCQ_QUESTIONS,
    }));
  });

  // 2. Completed Interviews / Submissions
  const [completedInterviews, setCompletedInterviews] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.COMPLETED);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
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
      try { return JSON.parse(saved); } catch (e) {}
    }
    return MOCK_ADMIN_STUDENTS;
  });

  // 4. Interviewers List (Includes pre-seeded active & invitation states)
  const [interviewers, setInterviewers] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.INTERVIEWERS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return MOCK_ADMIN_INTERVIEWERS.map((i) => ({
      ...i,
      organization: i.organization || 'University Department of Computing',
      status: i.status || 'Active',
      otp: '123456',
      invitationCode: `INV-${i.id.toUpperCase()}`,
      createdDate: '2026-08-01',
    }));
  });

  // 5. Feedbacks
  const [feedbacks, setFeedbacks] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.FEEDBACK);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return MOCK_ADMIN_FEEDBACK;
  });

  // 6. Settings (Configurable Proctoring Thresholds)
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return {
      strictness: 'High',
      maxWarnings: 3, // Configurable proctoring warning limit
      examDuration: 45,
      fullscreenLock: true,
      audioDetectionEnabled: true,
      tabSwitchDetectionEnabled: true,
      faceDetectionStrictness: 'Strict',
    };
  });

  // 7. System Warning & Violation Logs
  const [warningLogs, setWarningLogs] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.WARNING_LOGS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return [
      {
        id: 'warn_101',
        studentId: 'st_01',
        studentName: 'Aarav Sharma',
        examId: 'dsa_final_2026',
        examTitle: 'Advanced Data Structures & Algorithms',
        type: 'Tab Switch Violation',
        severity: 'Medium',
        timestamp: '2026-08-08 10:14 AM',
        actionTaken: 'Warning 1/3 Issued',
      },
      {
        id: 'warn_102',
        studentId: 'st_02',
        studentName: 'Diya Patel',
        examId: 'dsa_final_2026',
        examTitle: 'Advanced Data Structures & Algorithms',
        type: 'Face Not Detected (>3s)',
        severity: 'High',
        timestamp: '2026-08-08 10:22 AM',
        actionTaken: 'Warning 1/3 Issued',
      },
      {
        id: 'warn_103',
        studentId: 'st_03',
        studentName: 'Rohan Verma',
        examId: 'dsa_final_2026',
        examTitle: 'Advanced Data Structures & Algorithms',
        type: 'Multiple Faces Detected in Camera Frame',
        severity: 'Critical',
        timestamp: '2026-08-08 10:35 AM',
        actionTaken: 'Warning 2/3 Issued',
      },
    ];
  });

  // 8. System Activity Audit Logs
  const [activityLogs, setActivityLogs] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.ACTIVITY_LOGS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return [
      {
        id: 'act_1',
        user: 'Administrator',
        role: 'admin',
        type: 'Interviewer Invitation',
        description: 'Dispatched account invitation to Dr. Harish Kumar (harish.k@university.edu)',
        timestamp: '15 Mins ago',
      },
      {
        id: 'act_2',
        user: 'Aarav Sharma',
        role: 'student',
        type: 'Exam Submission',
        description: 'Successfully completed Data Structures Final Assessment (Score: 92%)',
        timestamp: '45 Mins ago',
      },
      {
        id: 'act_3',
        user: 'Prof. Rajesh Khanna',
        role: 'interviewer',
        type: 'Question Set Generation',
        description: 'Uploaded syllabus PDF and generated 20 MCQ questions for Artificial Intelligence',
        timestamp: '2 Hours ago',
      },
      {
        id: 'act_4',
        user: 'AI Proctoring Core',
        role: 'system',
        type: 'System Health Check',
        description: 'All 100+ concurrent exam worker nodes running with nominal latency (<45ms)',
        timestamp: '3 Hours ago',
      },
    ];
  });

  // 9. Pending Password Resets
  const [pendingResets, setPendingResets] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.PENDING_RESETS);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return {};
  });

  // Local Storage Sync Effects
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

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.WARNING_LOGS, JSON.stringify(warningLogs));
  }, [warningLogs]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.ACTIVITY_LOGS, JSON.stringify(activityLogs));
  }, [activityLogs]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.PENDING_RESETS, JSON.stringify(pendingResets));
  }, [pendingResets]);

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
    addActivityLog({
      user: interviewPayload.createdByEmail || 'Interviewer',
      role: 'interviewer',
      type: 'Exam Created',
      description: `Created new examination: ${interviewPayload.title || interviewPayload.company}`,
    });
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
    setInterviews((prev) => prev.filter((item) => item.id !== resultPayload.interviewId));
    addActivityLog({
      user: resultPayload.studentName || 'Student',
      role: 'student',
      type: 'Exam Submitted',
      description: `Submitted exam ${resultPayload.examTitle || 'Assessment'} (Score: ${resultPayload.marks}%)`,
    });
    return newResult;
  };

  // Student Admin Operations
  const addStudent = (studentData) => {
    const newStudent = {
      id: `st_${Date.now()}`,
      status: 'Active',
      examsTaken: 0,
      avgScore: 'N/A',
      createdDate: new Date().toISOString().split('T')[0],
      ...studentData,
    };
    setStudents((prev) => [newStudent, ...prev]);
    addActivityLog({
      user: 'Administrator',
      role: 'admin',
      type: 'Student Created',
      description: `Registered student ${studentData.name} (${studentData.rollNo || studentData.email})`,
    });
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

  /**
   * Admin Interviewer Invitation Workflow
   * Admin enters: Full Name, Email, Domain, Organization/Company.
   * Admin does NOT assign a password. Backend/System generates an activation OTP/Token.
   */
  const createInterviewerInvitation = ({ name, email, domain, organization }) => {
    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    const invitationCode = `INV-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;

    const newInterviewer = {
      id: `int_${Date.now()}`,
      name,
      email: email.trim().toLowerCase(),
      domain: domain || 'Computer Science & Engineering',
      organization: organization || 'University Faculty of Computing',
      status: 'Pending Activation', // Account not yet activated
      examsCreated: 0,
      rating: '5.0/5',
      otp: generatedOtp,
      invitationCode,
      createdDate: new Date().toISOString().split('T')[0],
      password: null, // No permanent password until interviewer activates
    };

    setInterviewers((prev) => [newInterviewer, ...prev]);

    addActivityLog({
      user: 'Administrator',
      role: 'admin',
      type: 'Interviewer Invited',
      description: `Dispatched invitation to ${name} (${email}) for domain: ${domain}`,
    });

    return {
      success: true,
      interviewer: newInterviewer,
      otp: generatedOtp,
      invitationCode,
    };
  };

  /**
   * Interviewer Account Activation
   * Interviewer provides: Email, OTP/Invitation Code, New Password
   */
  const activateInterviewerAccount = ({ email, otp, newPassword }) => {
    const cleanEmail = (email || '').trim().toLowerCase();
    const cleanOtp = (otp || '').trim();

    const interviewerIndex = interviewers.findIndex(
      (i) => (i.email || '').toLowerCase() === cleanEmail
    );

    if (interviewerIndex === -1) {
      throw new Error('No invitation found for this email address. Please contact your administrator.');
    }

    const interviewer = interviewers[interviewerIndex];

    // Check OTP or Invitation Code match (or universal testing fallback '123456' / actual assigned OTP)
    const isValidOtp =
      interviewer.otp === cleanOtp ||
      interviewer.invitationCode === cleanOtp ||
      cleanOtp === '123456';

    if (!isValidOtp) {
      throw new Error('Invalid OTP or Invitation Verification Code. Please check your email or contact Admin.');
    }

    const updatedInterviewer = {
      ...interviewer,
      status: 'Active',
      password: newPassword,
      activatedAt: new Date().toISOString(),
    };

    const updatedList = [...interviewers];
    updatedList[interviewerIndex] = updatedInterviewer;
    setInterviewers(updatedList);

    addActivityLog({
      user: interviewer.name,
      role: 'interviewer',
      type: 'Account Activated',
      description: `Faculty account activated and permanent password established for ${interviewer.name}`,
    });

    return {
      success: true,
      interviewer: updatedInterviewer,
      message: 'Account activated successfully.',
    };
  };

  const deleteInterviewer = (id) => {
    setInterviewers((prev) => prev.filter((i) => i.id !== id));
  };

  const toggleInterviewerStatus = (id) => {
    setInterviewers((prev) =>
      prev.map((i) =>
        i.id === id
          ? {
              ...i,
              status: i.status === 'Active' ? 'On Hold' : i.status === 'On Hold' ? 'Active' : i.status,
            }
          : i
      )
    );
  };

  const updateInterviewer = (id, fields) => {
    setInterviewers((prev) =>
      prev.map((i) => (i.id === id ? { ...i, ...fields } : i))
    );
  };

  // Password Reset Workflow
  const requestPasswordReset = (email, role) => {
    const cleanEmail = (email || '').trim().toLowerCase();
    const otp = Math.floor(100000 + Math.random() * 900000).toString();

    setPendingResets((prev) => ({
      ...prev,
      [cleanEmail]: { otp, role, requestedAt: Date.now() },
    }));

    return { success: true, otp };
  };

  const verifyResetOtp = (email, otp) => {
    const cleanEmail = (email || '').trim().toLowerCase();
    const record = pendingResets[cleanEmail];
    if (!record) {
      // Allow fallback testing OTP '123456'
      if (otp === '123456') return true;
      throw new Error('No password reset request active for this email.');
    }
    if (record.otp !== (otp || '').trim() && otp !== '123456') {
      throw new Error('Invalid verification OTP code.');
    }
    return true;
  };

  const resetPassword = ({ email, otp, newPassword }) => {
    verifyResetOtp(email, otp);
    const cleanEmail = (email || '').trim().toLowerCase();

    // Update in interviewers if applicable
    setInterviewers((prev) =>
      prev.map((i) =>
        (i.email || '').toLowerCase() === cleanEmail ? { ...i, password: newPassword } : i
      )
    );

    // Clean up reset record
    setPendingResets((prev) => {
      const next = { ...prev };
      delete next[cleanEmail];
      return next;
    });

    return { success: true };
  };

  // Warning & Proctoring Logs
  const logWarning = ({ studentId, studentName, examId, examTitle, type, severity, actionTaken }) => {
    const newLog = {
      id: `warn_${Date.now()}`,
      studentId: studentId || 'std_01',
      studentName: studentName || 'Candidate',
      examId: examId || 'exam_01',
      examTitle: examTitle || 'Examination',
      type: type || 'Proctoring Warning',
      severity: severity || 'Medium',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actionTaken: actionTaken || 'Warning Recorded',
    };
    setWarningLogs((prev) => [newLog, ...prev]);
  };

  const addActivityLog = ({ user, role, type, description }) => {
    const newLog = {
      id: `act_${Date.now()}`,
      user: user || 'User',
      role: role || 'system',
      type: type || 'System Activity',
      description: description || '',
      timestamp: 'Just now',
    };
    setActivityLogs((prev) => [newLog, ...prev]);
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
        warningLogs,
        activityLogs,
        createInterview,
        deleteInterview,
        submitExamResult,
        addCompletedInterview: submitExamResult,
        addStudent,
        deleteStudent,
        toggleStudentStatus,
        createInterviewerInvitation,
        addInterviewer: createInterviewerInvitation,
        activateInterviewerAccount,
        deleteInterviewer,
        toggleInterviewerStatus,
        updateInterviewer,
        requestPasswordReset,
        verifyResetOtp,
        resetPassword,
        logWarning,
        addActivityLog,
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
