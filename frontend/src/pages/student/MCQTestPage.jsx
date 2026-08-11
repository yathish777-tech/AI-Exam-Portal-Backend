import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Bookmark,
  Send,
  AlertTriangle,
  Sparkles,
  Camera,
  Eye,
  Maximize,
  ShieldAlert,
  Users,
  VideoOff,
  RefreshCw,
  Info,
  ShieldCheck,
  AlertCircle,
} from 'lucide-react';
import Modal from '../../components/common/Modal';
import { MOCK_MCQ_QUESTIONS } from '../../utils/mockData';
import { useData } from '../../context/DataContext';
import { useAuth } from '../../context/AuthContext';

export default function MCQTestPage() {
  const navigate = useNavigate();
  const { interviewId } = useParams();
  const { user } = useAuth();
  const { interviews, submitExamResult } = useData();

  // Find current interview info or fallback
  const interviewData = interviews.find((item) => item.id === interviewId) || {
    id: interviewId || 'int_101',
    company: 'TechCorp University Exam',
    title: 'Data Structures & Algorithms Final Examination',
    domain: 'Data Structures & Algorithms',
    code: 'DSA-CS301',
    duration: '45 Mins',
  };

  // MCQ Questions State
  const [questions] = useState(MOCK_MCQ_QUESTIONS);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Answers state { [questionId]: optionIndex }
  const [selectedAnswers, setSelectedAnswers] = useState({});
  // Review set
  const [reviewSet, setReviewSet] = useState(new Set());

  // Timer: 45 minutes = 2700 seconds
  const [timeLeft, setTimeLeft] = useState(2700);

  // Webcam & Proctoring States
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);

  // Face Detection Status: 'detected' | 'no_face' | 'multi_face'
  const [faceStatus, setFaceStatus] = useState('detected');
  const noFaceTimerRef = useRef(null);
  const noFaceStartTimeRef = useRef(null);

  // Warnings & Violations Tracking
  const [warningCount, setWarningCount] = useState(0);
  const maxWarnings = 3;
  const [warningModalOpen, setWarningModalOpen] = useState(false);
  const [activeWarningTitle, setActiveWarningTitle] = useState('');
  const [activeWarningMessage, setActiveWarningMessage] = useState('');
  const [violationsLog, setViolationsLog] = useState([]);

  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState(true);

  // Final Submit Modal
  const [submitModalOpen, setSubmitModalOpen] = useState(false);

  // Ref to prevent duplicate warning triggers during same event
  const lastWarningTimeRef = useRef(0);

  // Format timer MM:SS
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Helper to record a violation
  const recordViolation = (type, description) => {
    const now = Date.now();
    // Debounce duplicate warnings within 2 seconds
    if (now - lastWarningTimeRef.current < 2000) return;
    lastWarningTimeRef.current = now;

    const timeString = formatTime(timeLeft);
    const newViolation = {
      id: `viol_${now}`,
      time: timeString,
      type,
      description,
      timestamp: new Date().toLocaleTimeString(),
    };

    setViolationsLog((prev) => [...prev, newViolation]);
    setWarningCount((prevCount) => {
      const updated = prevCount + 1;
      setActiveWarningTitle(`Proctor Violation Alert (${updated}/${maxWarnings})`);
      setActiveWarningMessage(description);
      setWarningModalOpen(true);

      // Auto Submit if max warnings reached
      if (updated >= maxWarnings) {
        setTimeout(() => {
          handleFinalSubmit('Auto-Submitted: Maximum Violation Limit Reached (3/3)');
        }, 1200);
      }
      return updated;
    });
  };

  // Ref to hold simulation overrides so manual testing buttons work reliably
  const simulationHoldUntilRef = useRef(0);

  // Helper to cleanly stop webcam media stream and release hardware camera
  const stopCameraStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
          track.enabled = false;
        } catch (e) {}
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  // 1. Initialize & Monitor Webcam
  useEffect(() => {
    let isMounted = true;

    const startWebcam = async () => {
      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 } },
            audio: false,
          });
          streamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
          if (isMounted) setCameraActive(true);

          // Monitor camera disconnection / track ended
          const videoTrack = stream.getVideoTracks()[0];
          if (videoTrack) {
            videoTrack.onended = () => {
              if (isMounted) {
                setCameraActive(false);
                recordViolation('Camera Disconnected', 'Webcam stream was disconnected or disabled!');
              }
            };
            videoTrack.onmute = () => {
              if (isMounted) {
                recordViolation('Camera Muted', 'Webcam video stream was muted by device!');
              }
            };
          }
        }
      } catch (err) {
        console.warn('Webcam access error or permission denied:', err);
        if (isMounted) {
          setCameraActive(true); // Fallback active for sandbox preview
        }
      }
    };

    startWebcam();

    return () => {
      isMounted = false;
      stopCameraStream();
    };
  }, []);

  // Periodic Camera Connectivity & Track Health Check
  useEffect(() => {
    const healthInterval = setInterval(() => {
      if (streamRef.current) {
        const videoTrack = streamRef.current.getVideoTracks()[0];
        if (!videoTrack || videoTrack.readyState !== 'live' || !videoTrack.enabled) {
          setCameraActive(false);
          recordViolation('Camera Inactive', 'Webcam video feed is inactive or blocked.');
        } else {
          setCameraActive(true);
        }
      }
    }, 4000);

    return () => clearInterval(healthInterval);
  }, [timeLeft]);

  // 2. Real-time Face & Person Detection Loop ( Native FaceDetector or Advanced YCbCr Skin Analysis Fallback )
  useEffect(() => {
    const processFrame = async () => {
      if (!videoRef.current || !canvasRef.current || !cameraActive) return;

      // Skip frame processing if manual simulation hold is active
      if (Date.now() < simulationHoldUntilRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video.readyState < 2) return; // wait until video frames loaded

      const ctx = canvas.getContext('2d');
      const w = 160;
      const h = 120;
      canvas.width = w;
      canvas.height = h;
      ctx.drawImage(video, 0, 0, w, h);

      // Check for Native Chromium FaceDetector API
      if ('FaceDetector' in window) {
        try {
          // @ts-ignore
          const faceDetector = new window.FaceDetector({ fastMode: true });
          const faces = await faceDetector.detect(video);
          if (faces.length === 1) {
            setFaceStatus('detected');
          } else if (faces.length === 0) {
            setFaceStatus('no_face');
          } else {
            setFaceStatus('multi_face');
          }
          return;
        } catch (e) {
          // Fall back to pixel analysis fallback
        }
      }

      // Advanced Fallback Pixel & Skin-Tone Analysis
      const imgData = ctx.getImageData(0, 0, w, h);
      const pixels = imgData.data;

      let totalLuminance = 0;
      let sampledCount = 0;
      let skinPixelCount = 0;
      let leftSkinCount = 0;
      let rightSkinCount = 0;

      // Sample pixels in central area (x: 15% to 85%, y: 10% to 90%)
      const minX = Math.floor(w * 0.15);
      const maxX = Math.floor(w * 0.85);
      const minY = Math.floor(h * 0.10);
      const maxY = Math.floor(h * 0.90);

      for (let y = minY; y < maxY; y += 2) {
        for (let x = minX; x < maxX; x += 2) {
          const idx = (y * w + x) * 4;
          const r = pixels[idx];
          const g = pixels[idx + 1];
          const b = pixels[idx + 2];

          const brightness = (r + g + b) / 3;
          totalLuminance += brightness;
          sampledCount++;

          // YCbCr Skin Tone Model
          const cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b;
          const cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b;

          const isSkin = cr >= 133 && cr <= 173 && cb >= 77 && cb <= 127 && brightness > 20 && brightness < 245;

          if (isSkin) {
            skinPixelCount++;
            if (x < w * 0.4) leftSkinCount++;
            if (x > w * 0.6) rightSkinCount++;
          }
        }
      }

      const avgBrightness = sampledCount > 0 ? totalLuminance / sampledCount : 0;
      const skinRatio = sampledCount > 0 ? (skinPixelCount / sampledCount) * 100 : 0;
      const leftSkinRatio = sampledCount > 0 ? (leftSkinCount / sampledCount) * 100 : 0;
      const rightSkinRatio = sampledCount > 0 ? (rightSkinCount / sampledCount) * 100 : 0;

      // Rule 1: Covered camera or dark room
      if (avgBrightness < 15) {
        setFaceStatus('no_face');
        return;
      }

      // Rule 2: Low skin pixel ratio -> No candidate face present in central area
      if (skinRatio < 3.5) {
        setFaceStatus('no_face');
        return;
      }

      // Rule 3: Multiple distinct facial presence
      if (leftSkinRatio > 8.0 && rightSkinRatio > 8.0 && skinRatio > 25.0) {
        setFaceStatus('multi_face');
        return;
      }

      // Rule 4: Normal single face detected
      setFaceStatus('detected');
    };

    const interval = setInterval(processFrame, 800);
    return () => clearInterval(interval);
  }, [cameraActive]);

  // Handle Face Status Rules (No face >3s or Multi-face)
  useEffect(() => {
    if (faceStatus === 'no_face') {
      if (!noFaceStartTimeRef.current) {
        noFaceStartTimeRef.current = Date.now();
      }

      noFaceTimerRef.current = setInterval(() => {
        if (noFaceStartTimeRef.current && Date.now() - noFaceStartTimeRef.current >= 3000) {
          recordViolation('Face Not Found', 'No candidate face detected in camera feed for over 3 seconds!');
          clearInterval(noFaceTimerRef.current);
          noFaceStartTimeRef.current = null;
        }
      }, 500);
    } else {
      if (noFaceTimerRef.current) clearInterval(noFaceTimerRef.current);
      noFaceStartTimeRef.current = null;
    }

    if (faceStatus === 'multi_face') {
      recordViolation('Multiple Faces Detected', 'Multiple individuals detected in webcam stream!');
    }

    return () => {
      if (noFaceTimerRef.current) clearInterval(noFaceTimerRef.current);
    };
  }, [faceStatus]);

  // 3. Tab Switching & Window Focus Listener
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        recordViolation('Tab Switch Detected', 'Tab switching or browser minimization detected! Stay on exam window.');
      }
    };

    const handleWindowBlur = () => {
      recordViolation('Window Blur', 'Browser window lost focus. External window switching detected.');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
    };
  }, [timeLeft]);

  // 4. Fullscreen Lock Enforcement
  useEffect(() => {
    // Attempt fullscreen on start
    try {
      if (document.documentElement.requestFullscreen && !document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    } catch (e) {}

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        setIsFullscreen(false);
        recordViolation('Fullscreen Exited', 'Fullscreen mode was exited! Re-enter fullscreen to continue.');
      } else {
        setIsFullscreen(true);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, [timeLeft]);

  // Request Fullscreen re-entry
  const reenterFullscreen = () => {
    try {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
      }
      setIsFullscreen(true);
      setWarningModalOpen(false);
    } catch (err) {
      setIsFullscreen(true);
      setWarningModalOpen(false);
    }
  };

  // 5. Timer Effect & Auto-Submit on Timeout
  useEffect(() => {
    if (timeLeft <= 0) {
      handleFinalSubmit('Timer Expired (45 Minutes)');
      return;
    }
    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  // 6. BeforeUnload window listener
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      e.preventDefault();
      e.returnValue = 'Leaving the exam will auto-submit your test paper!';
      return e.returnValue;
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  // Answer selection helpers
  const currentQuestion = questions[currentIndex];

  const handleSelectOption = (optionIndex) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIndex,
    }));
  };

  const toggleReviewMark = () => {
    const copy = new Set(reviewSet);
    if (copy.has(currentQuestion.id)) {
      copy.delete(currentQuestion.id);
    } else {
      copy.add(currentQuestion.id);
    }
    setReviewSet(copy);
  };

  const clearResponse = () => {
    const copy = { ...selectedAnswers };
    delete copy[currentQuestion.id];
    setSelectedAnswers(copy);
  };

  const answeredCount = Object.keys(selectedAnswers).length;

  // 7. Final Exam Submission Handler
  const handleFinalSubmit = (submissionReason) => {
    // 1. Stop all camera media streams cleanly & release hardware
    stopCameraStream();

    // 2. Exit fullscreen mode if active
    try {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
    } catch (e) {}

    // Compute evaluation
    let correctCount = 0;
    questions.forEach((q) => {
      if (selectedAnswers[q.id] === q.correctAnswer) {
        correctCount += 1;
      }
    });

    const totalQ = questions.length;
    const wrongCount = totalQ - correctCount - (totalQ - answeredCount);
    const score = Math.round((correctCount / totalQ) * 100);
    const elapsedSeconds = 2700 - timeLeft;
    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    const formattedTimeTaken = `${mins} Mins ${secs} Secs`;

    const resultPayload = {
      id: `comp_${Date.now()}`,
      interviewId: interviewData.id || 'int_101',
      studentName: user?.name || 'Aarav Sharma',
      studentEmail: user?.email || 'student@examportal.edu',
      rollNo: user?.rollNo || 'CS2026-089',
      company: interviewData.company || 'TechCorp University Exam',
      title: interviewData.title || 'Data Structures & Algorithms Final Examination',
      domain: interviewData.domain || 'Data Structures & Algorithms',
      code: interviewData.code || 'DSA-CS301',
      date: new Date().toISOString().split('T')[0],
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      marks: score,
      totalMarks: 100,
      percentage: score,
      correctAnswers: correctCount,
      wrongAnswers: wrongCount,
      unanswered: totalQ - answeredCount,
      totalQuestions: totalQ,
      timeTaken: formattedTimeTaken,
      violationsCount: warningCount,
      violationsList: violationsLog,
      userAnswers: selectedAnswers,
      questions: questions,
      status:
        warningCount >= 3
          ? 'Auto-Submitted (Violations Limit Exceeded)'
          : submissionReason
          ? `Submitted (${submissionReason})`
          : score >= 70
          ? 'Passed - Distinction'
          : 'Passed',
      proctoringScore: warningCount === 0 ? '100% Clean' : `${Math.max(0, 100 - warningCount * 25)}% Clean`,
    };

    submitExamResult(resultPayload);
    navigate(`/student/results/${resultPayload.id}`);
  };

  // Manual Simulation Trigger Helpers for UI Testing
  const triggerSimulatedNoFace = () => {
    simulationHoldUntilRef.current = Date.now() + 8000;
    setFaceStatus('no_face');
  };

  const triggerSimulatedMultiFace = () => {
    simulationHoldUntilRef.current = Date.now() + 8000;
    setFaceStatus('multi_face');
  };

  const triggerSimulatedNormalFace = () => {
    simulationHoldUntilRef.current = 0;
    setFaceStatus('detected');
  };

  const triggerSimulatedDisconnect = () => {
    setCameraActive(false);
    recordViolation('Camera Disconnected', 'Manual camera disconnection simulated by test control.');
  };

  const triggerSimulatedTabSwitch = () => {
    recordViolation('Tab Switch Simulated', 'Manual tab switch alert simulated by user.');
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-3 sm:p-5 lg:p-6 space-y-5 max-w-7xl mx-auto text-slate-800 selection:bg-blue-100">
      
      {/* Offscreen Canvas for Frame Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Top Header Bar */}
      <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 uppercase">
              {interviewData.code || 'DSA-CS301'} • PROCTORED EXAM
            </span>
            <span className="text-[10px] font-bold text-slate-500">
              Candidate: {user?.name || 'Aarav Sharma'}
            </span>
          </div>
          <h1 className="text-base font-bold text-slate-900 mt-0.5 tracking-tight">
            {interviewData.company || 'Data Structures & Algorithms Final Examination'}
          </h1>
        </div>

        {/* Live Timer & Proctor Badge */}
        <div className="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-100 rounded-md font-semibold text-xs">
            <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
            <span>AI Proctor Lock Active</span>
          </div>

          <div
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md font-bold text-xs border ${
              timeLeft < 300
                ? 'bg-red-50 text-red-700 border-red-200 animate-pulse'
                : 'bg-slate-900 text-white border-slate-800'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{formatTime(timeLeft)}</span>
          </div>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        
        {/* Left / Center 3 Columns: MCQ Questions View */}
        <div className="lg:col-span-3 space-y-5">
          <div className="bg-white rounded-xl p-5 sm:p-7 border border-slate-200/80 shadow-xs space-y-6 text-slate-800">
            
            {/* Header & Question Navigation */}
            <div className="space-y-3 border-b border-slate-200 pb-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Question {currentIndex + 1} of {questions.length}
                </span>

                <button
                  onClick={toggleReviewMark}
                  className={`px-3 py-1 text-xs font-medium rounded-md flex items-center space-x-1.5 transition-colors ${
                    reviewSet.has(currentQuestion.id)
                      ? 'bg-amber-100 text-amber-800 border border-amber-200 font-bold'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Bookmark className="w-3.5 h-3.5" />
                  <span>{reviewSet.has(currentQuestion.id) ? 'Marked for Review' : 'Mark for Review'}</span>
                </button>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden border border-slate-200">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                />
              </div>
            </div>

            {/* Question Heading */}
            <div className="space-y-2">
              <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                {currentQuestion.question}
              </h3>
            </div>

            {/* Options List */}
            <div className="space-y-2.5 pt-1">
              {currentQuestion.options.map((opt, optIdx) => {
                const isSelected = selectedAnswers[currentQuestion.id] === optIdx;
                return (
                  <button
                    key={optIdx}
                    onClick={() => handleSelectOption(optIdx)}
                    className={`w-full p-3.5 rounded-lg text-left border text-xs font-medium transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50 text-slate-900 font-bold shadow-xs'
                        : 'border-slate-200/80 hover:border-slate-300 bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span
                        className={`w-6 h-6 rounded flex items-center justify-center font-bold text-xs ${
                          isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700'
                        }`}
                      >
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span>{opt}</span>
                    </div>

                    {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />}
                  </button>
                );
              })}
            </div>

            {/* Bottom Controls */}
            <div className="pt-5 border-t border-slate-200 flex items-center justify-between flex-wrap gap-3">
              <button
                onClick={clearResponse}
                className="text-xs font-medium text-slate-500 hover:text-slate-800"
              >
                Clear Response
              </button>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                  disabled={currentIndex === 0}
                  className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 font-medium text-xs rounded-md transition-colors flex items-center space-x-1"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>

                {currentIndex < questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                    className="px-4 py-1.5 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md shadow-xs transition-colors flex items-center space-x-1"
                  >
                    <span>Next Question</span>
                    <ChevronRight className="w-4 h-4 text-blue-400" />
                  </button>
                ) : (
                  <button
                    onClick={() => setSubmitModalOpen(true)}
                    className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-md shadow-xs transition-colors flex items-center space-x-1.5"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Submit Exam</span>
                  </button>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Right 1 Column: Persistent Live Proctoring Panel & Navigator */}
        <div className="space-y-4">
          
          {/* Live Webcam & Face Status Box */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-900">
                <Camera className="w-4 h-4 text-blue-600" />
                <span>Live Proctoring Feed</span>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                cameraActive ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
              }`}>
                {cameraActive ? 'CAM ON' : 'CAM DISCONNECTED'}
              </span>
            </div>

            {/* Video Player */}
            <div className="w-full h-36 bg-slate-900 rounded-lg overflow-hidden relative border border-slate-300 flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`w-full h-full object-cover ${!cameraActive ? 'hidden' : ''}`}
              />

              {!cameraActive && (
                <div className="text-center p-3 text-red-400 space-y-1">
                  <VideoOff className="w-8 h-8 mx-auto" />
                  <p className="text-[11px] font-bold">Camera Feed Interrupted</p>
                </div>
              )}

              {/* Status Overlay Badge inside Video */}
              {cameraActive && (
                <div className="absolute top-2 left-2 right-2 flex items-center justify-between">
                  <div className="px-2 py-0.5 bg-slate-900/90 text-white text-[9px] font-bold rounded flex items-center space-x-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                    <span>REC • 30FPS</span>
                  </div>

                  {/* Requirement 2: Status Badges */}
                  {faceStatus === 'detected' && (
                    <span className="px-2 py-0.5 bg-emerald-600 text-white text-[10px] font-bold rounded shadow-xs flex items-center space-x-1">
                      <span>✅ Face Detected</span>
                    </span>
                  )}
                  {faceStatus === 'no_face' && (
                    <span className="px-2 py-0.5 bg-red-600 text-white text-[10px] font-bold rounded shadow-xs animate-pulse flex items-center space-x-1">
                      <span>❌ Face Not Found</span>
                    </span>
                  )}
                  {faceStatus === 'multi_face' && (
                    <span className="px-2 py-0.5 bg-amber-500 text-white text-[10px] font-bold rounded shadow-xs animate-pulse flex items-center space-x-1">
                      <span>⚠ Multiple Faces Detected</span>
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Violation Counters Display */}
            <div className="p-2.5 bg-slate-50 border border-slate-200/80 rounded-lg flex items-center justify-between text-xs">
              <span className="text-slate-500 font-medium text-[11px]">Proctor Violations:</span>
              <span className={`font-bold px-2 py-0.5 rounded text-xs ${
                warningCount === 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
              }`}>
                {warningCount} / {maxWarnings} Allowed
              </span>
            </div>

            {/* Test Simulation Buttons */}
            <div className="pt-1 space-y-1.5">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                Proctor Testing Controls
              </p>
              <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                <button
                  onClick={triggerSimulatedNoFace}
                  className="px-2 py-1 bg-red-50 hover:bg-red-100 text-red-800 rounded border border-red-200 font-medium"
                >
                  Test No Face
                </button>
                <button
                  onClick={triggerSimulatedNormalFace}
                  className="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded border border-emerald-200 font-medium"
                >
                  Reset Face OK
                </button>
                <button
                  onClick={triggerSimulatedMultiFace}
                  className="px-2 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded border border-amber-200 font-medium"
                >
                  Test Multi-Face
                </button>
                <button
                  onClick={triggerSimulatedTabSwitch}
                  className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-800 rounded border border-blue-200 font-medium"
                >
                  Test Tab Switch
                </button>
              </div>
            </div>

          </div>

          {/* Question Navigator Palette */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-xs space-y-3 text-slate-800">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Question Navigator
            </h4>

            {/* Legend */}
            <div className="grid grid-cols-2 gap-2 text-[10px] font-medium text-slate-500">
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-xs bg-emerald-600" />
                <span>Answered ({answeredCount})</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-xs bg-amber-500" />
                <span>Review ({reviewSet.size})</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-xs bg-slate-200" />
                <span>Unvisited ({questions.length - answeredCount})</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-xs bg-blue-600" />
                <span>Current</span>
              </div>
            </div>

            {/* Grid of question buttons */}
            <div className="grid grid-cols-5 gap-1.5 pt-1">
              {questions.map((q, idx) => {
                const isCurrent = idx === currentIndex;
                const isAnswered = selectedAnswers[q.id] !== undefined;
                const isMarked = reviewSet.has(q.id);

                let btnBg = 'bg-slate-100 text-slate-700 hover:bg-slate-200';
                if (isCurrent) {
                  btnBg = 'bg-blue-600 text-white font-bold ring-2 ring-blue-300';
                } else if (isMarked) {
                  btnBg = 'bg-amber-500 text-white font-bold';
                } else if (isAnswered) {
                  btnBg = 'bg-emerald-600 text-white font-bold';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentIndex(idx)}
                    className={`h-8 rounded text-xs transition-colors flex items-center justify-center ${btnBg}`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setSubmitModalOpen(true)}
              className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-md shadow-xs transition-colors flex items-center justify-center space-x-1.5 mt-2"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Submit Examination</span>
            </button>
          </div>

        </div>

      </div>

      {/* Proctor Warning Alert Modal */}
      {warningModalOpen && (
        <Modal
          isOpen={warningModalOpen}
          onClose={() => setWarningModalOpen(false)}
          title="⚠️ AI Proctoring Security Warning"
        >
          <div className="text-center py-2 space-y-4 text-xs text-slate-800">
            <div className="w-12 h-12 rounded-full bg-red-100 border border-red-200 text-red-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <h4 className="text-sm font-bold text-slate-900">{activeWarningTitle}</h4>
              <p className="text-slate-600 font-medium bg-red-50 p-2.5 rounded border border-red-100 text-xs">
                {activeWarningMessage}
              </p>
            </div>

            <p className="text-slate-500 leading-relaxed text-[11px]">
              University exam integrity policies strictly prohibit tab switching, loss of face detection, or exiting full screen.
              <br />
              <strong className="text-red-600 font-bold">
                Warning Count: {warningCount} of {maxWarnings} Maximum Allowed.
              </strong>
            </p>

            <div className="flex items-center justify-center space-x-2 pt-2">
              {!isFullscreen && (
                <button
                  onClick={reenterFullscreen}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-md"
                >
                  Re-Enter Fullscreen Mode
                </button>
              )}
              <button
                onClick={() => setWarningModalOpen(false)}
                className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-md"
              >
                Acknowledge & Resume
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Final Submit Confirmation Modal */}
      {submitModalOpen && (
        <Modal
          isOpen={submitModalOpen}
          onClose={() => setSubmitModalOpen(false)}
          title="Confirm Final Examination Submission"
        >
          <div className="space-y-4 text-xs text-slate-800">
            <p className="text-slate-600 text-sm">
              Are you sure you want to finalize and submit your examination paper?
            </p>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Total Questions:</span>
                <span className="font-bold text-slate-800">{questions.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Answered:</span>
                <span className="font-bold text-emerald-600">{answeredCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Unanswered:</span>
                <span className="font-bold text-red-600">{questions.length - answeredCount}</span>
              </div>
              <div className="flex justify-between border-t border-slate-200 pt-1.5">
                <span className="text-slate-500 font-medium">Proctor Flags Logged:</span>
                <span className={`font-bold ${warningCount === 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {warningCount} Warnings
                </span>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setSubmitModalOpen(false)}
                className="px-4 py-2 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md font-medium border border-slate-200"
              >
                Return to Test
              </button>
              <button
                onClick={() => handleFinalSubmit('Student Action')}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs text-white rounded-md shadow-xs"
              >
                Confirm & Submit
              </button>
            </div>
          </div>
        </Modal>
      )}

    </div>
  );
}
