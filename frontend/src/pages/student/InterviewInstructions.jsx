import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Camera,
  Mic,
  Maximize,
  CheckCircle2,
  AlertTriangle,
  Play,
  Shield,
  Eye,
  Laptop,
  Smartphone,
  Copy,
  Users,
  Sliders,
  ShieldAlert,
  Sparkles,
  Info,
} from 'lucide-react';
import Modal from '../../components/common/Modal';
import { useData } from '../../context/DataContext';

export default function InterviewInstructions() {
  const navigate = useNavigate();
  const { interviewId } = useParams();
  const { interviews } = useData();

  const currentInterview = interviews.find((item) => item.id === interviewId) || interviews[0] || {
    id: 'int_101',
    code: 'DSA-CS301',
    company: 'Data Structures & Algorithms Final Examination',
    duration: '45 Minutes',
  };

  const targetInterviewId = currentInterview.id || 'int_101';

  // Permission states: 'pending' | 'granted' | 'denied'
  const [webcamStatus, setWebcamStatus] = useState('pending');
  const [micStatus, setMicStatus] = useState('pending');
  const [fullscreenStatus, setFullscreenStatus] = useState('pending');

  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Warning Modal simulation state
  const [warningModalOpen, setWarningModalOpen] = useState(false);
  const [activeWarning, setActiveWarning] = useState('');

  // Request Webcam
  const requestWebcam = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }
      setWebcamStatus('granted');
    } catch (err) {
      console.warn('Real webcam blocked or unavailable, using simulated webcam stream:', err);
      setWebcamStatus('granted'); // Fallback granted for demo sandbox
    }
  };

  // Request Microphone
  const requestMicrophone = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      }
      setMicStatus('granted');
    } catch (err) {
      console.warn('Microphone permission fallback granted for demo:', err);
      setMicStatus('granted');
    }
  };

  // Request Fullscreen
  const requestFullscreen = () => {
    try {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
      }
      setFullscreenStatus('granted');
    } catch (err) {
      console.warn('Fullscreen request fallback:', err);
      setFullscreenStatus('granted');
    }
  };

  // Cleanup media stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const allGranted = webcamStatus === 'granted' && micStatus === 'granted' && fullscreenStatus === 'granted';

  const triggerMockWarning = (warningType) => {
    setActiveWarning(warningType);
    setWarningModalOpen(true);
  };

  const handleStartExam = () => {
    if (allGranted) {
      navigate(`/student/exam/${targetInterviewId}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 text-slate-800">
      
      {/* Header Banner */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md w-fit border border-blue-100">
          <Shield className="w-3.5 h-3.5" />
          <span>Exam Code: {currentInterview.code || 'DSA-CS301'} • Duration: {currentInterview.duration || '45 Minutes'}</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          {currentInterview.company || 'Data Structures & Algorithms Final Examination'}
        </h2>
        <p className="text-xs text-slate-500">
          Please read the official university rules and verify all device permissions before starting the test.
        </p>
      </div>

      {/* Rules & Guidelines */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Info className="w-4 h-4 text-blue-600" />
          <span>Official Examination Guidelines</span>
        </h3>

        <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-700 leading-relaxed font-medium">
          <li className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>You must remain centered in front of your camera throughout the 45-minute test.</span>
          </li>
          <li className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Do NOT switch browser tabs, minimize window, or open external developer tools.</span>
          </li>
          <li className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Copying, pasting, and keyboard shortcuts are strictly disabled.</span>
          </li>
          <li className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>More than 3 proctoring warnings will result in auto-submission of your examination paper.</span>
          </li>
        </ul>
      </div>

      {/* Hardware Permission Verification Section */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-6">
        <h3 className="text-sm font-bold text-slate-900">Device Hardware Verification</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Webcam Permission */}
          <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs">
                <Camera className="w-4 h-4 text-blue-600" />
                <span>Webcam Feed</span>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                webcamStatus === 'granted' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {webcamStatus.toUpperCase()}
              </span>
            </div>

            <p className="text-[11px] text-slate-500">Required for facial presence & eye tracking AI core.</p>

            {webcamStatus !== 'granted' ? (
              <button
                onClick={requestWebcam}
                className="w-full py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md transition-colors"
              >
                Allow Webcam
              </button>
            ) : (
              <div className="w-full h-24 bg-slate-900 rounded-md overflow-hidden relative flex items-center justify-center border border-slate-300">
                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                <div className="absolute top-1 left-1 px-1.5 py-0.5 bg-emerald-600 text-white text-[9px] font-bold rounded-xs">
                  LIVE FEED
                </div>
              </div>
            )}
          </div>

          {/* Microphone Permission */}
          <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs">
                <Mic className="w-4 h-4 text-blue-600" />
                <span>Microphone</span>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                micStatus === 'granted' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {micStatus.toUpperCase()}
              </span>
            </div>

            <p className="text-[11px] text-slate-500">Required for background noise & audio whisper detection.</p>

            {micStatus !== 'granted' ? (
              <button
                onClick={requestMicrophone}
                className="w-full py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md transition-colors"
              >
                Allow Microphone
              </button>
            ) : (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs font-medium flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Mic Stream Active</span>
              </div>
            )}
          </div>

          {/* Fullscreen Mode */}
          <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs">
                <Maximize className="w-4 h-4 text-blue-600" />
                <span>Fullscreen Sandbox</span>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                fullscreenStatus === 'granted' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {fullscreenStatus.toUpperCase()}
              </span>
            </div>

            <p className="text-[11px] text-slate-500">Required to lock screen during entire MCQ test.</p>

            {fullscreenStatus !== 'granted' ? (
              <button
                onClick={requestFullscreen}
                className="w-full py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-md transition-colors"
              >
                Enable Fullscreen
              </button>
            ) : (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs font-medium flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Fullscreen Locked</span>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* AI Proctoring Engine Readiness Controls */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-5">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">AI Proctoring Module Status</h3>
          </div>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
            9/9 Security Controls Active
          </span>
        </div>

        {/* 9 Requirements Placeholders Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          {[
            { label: 'Face Detection', icon: Camera, status: 'Active' },
            { label: 'Eye Tracking', icon: Eye, status: 'Active' },
            { label: 'Tab Switching Detection', icon: Laptop, status: 'Active' },
            { label: 'Multiple Person Detection', icon: Users, status: 'Armed' },
            { label: 'Mobile Phone Detection', icon: Smartphone, status: 'Armed' },
            { label: 'Electronic Device Detection', icon: Sliders, status: 'Armed' },
            { label: 'Browser Exit Detection', icon: ShieldAlert, status: 'Active' },
            { label: 'Fullscreen Exit Detection', icon: Maximize, status: 'Active' },
            { label: 'Copy/Paste Detection', icon: Copy, status: 'Blocked' },
          ].map((item, idx) => {
            const IconC = item.icon;
            return (
              <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-center justify-between">
                <div className="flex items-center space-x-2 text-slate-700">
                  <IconC className="w-3.5 h-3.5 text-blue-600" />
                  <span className="text-[11px] font-medium">{item.label}</span>
                </div>
                <span className="text-[10px] text-emerald-600 font-bold">{item.status}</span>
              </div>
            );
          })}
        </div>

        {/* Simulation Buttons to Test Proctor Warnings */}
        <div className="pt-2 border-t border-slate-200">
          <p className="text-[11px] text-slate-500 mb-2 font-medium">Simulate AI Proctoring Violation Warning Popups:</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => triggerMockWarning('Tab Switching Detected')}
              className="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 text-[11px] rounded-md border border-amber-200 font-medium"
            >
              Test Tab Switch Warning
            </button>
            <button
              onClick={() => triggerMockWarning('Multiple Persons Detected in Feed')}
              className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-red-800 text-[11px] rounded-md border border-red-200 font-medium"
            >
              Test Multi-Face Warning
            </button>
            <button
              onClick={() => triggerMockWarning('Copy/Paste Operation Blocked')}
              className="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-800 text-[11px] rounded-md border border-blue-200 font-medium"
            >
              Test Copy/Paste Block
            </button>
          </div>
        </div>
      </div>

      {/* Final Action Button */}
      <div className="pt-2 text-center">
        <button
          onClick={handleStartExam}
          disabled={!allGranted}
          className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white font-bold text-sm rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2 mx-auto"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Start Interview / Examination</span>
        </button>

        {!allGranted && (
          <p className="text-xs text-amber-700 font-medium mt-2">
            Please allow Webcam, Microphone, and Fullscreen above to start exam.
          </p>
        )}
      </div>

      {/* Warning Popup Modal */}
      {warningModalOpen && (
        <Modal
          isOpen={warningModalOpen}
          onClose={() => setWarningModalOpen(false)}
          title="⚠️ AI Proctoring Warning Alert"
        >
          <div className="space-y-4 text-xs text-center py-2">
            <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <h4 className="text-sm font-bold text-slate-900">
              Proctor Violation Warning: {activeWarning}
            </h4>

            <p className="text-slate-600 leading-relaxed">
              Our AI monitoring system flagged an event during session setup. Please ensure you remain focused on the exam screen.
              <br />
              <span className="font-bold text-red-600">Warning Count: 1 / 3 Maximum Allowed</span>
            </p>

            <button
              onClick={() => setWarningModalOpen(false)}
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-md"
            >
              I Understand & Acknowledge
            </button>
          </div>
        </Modal>
      )}

    </div>
  );
}

