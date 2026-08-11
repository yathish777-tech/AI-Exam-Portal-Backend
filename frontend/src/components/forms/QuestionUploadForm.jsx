import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Sparkles, RefreshCw, Users } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function QuestionUploadForm() {
  const { addInterview, students } = useData();
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [examTitle, setExamTitle] = useState('Advanced Data Structures & Algorithms Exam');
  const [domain, setDomain] = useState('Data Structures & Algorithms');
  const [assignmentTarget, setAssignmentTarget] = useState('ALL');
  const [createdExamId, setCreatedExamId] = useState('');

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.pdf')) {
        setFile(droppedFile);
        setUploadSuccess(false);
      } else {
        alert('Please upload a PDF file (.pdf)');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setUploadSuccess(false);
    }
  };

  const handleUploadSubmit = (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);

    setTimeout(() => {
      // Mock generate 5 MCQs from the PDF
      const generatedQuestions = [
        {
          id: 1,
          question: "What is the worst-case time complexity of quicksort algorithm?",
          options: ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
          correctOption: 1,
          explanation: "Quicksort has a worst-case time complexity of O(n²) when the pivot selection consistently chooses the smallest or largest element."
        },
        {
          id: 2,
          question: "Which data structure operates on a LIFO (Last In First Out) principle?",
          options: ["Queue", "Stack", "Linked List", "Binary Search Tree"],
          correctOption: 1,
          explanation: "Stack operates on LIFO structure where elements pushed last are popped first."
        },
        {
          id: 3,
          question: "In a min-heap, where is the minimum element located?",
          options: ["At any leaf node", "At the root node", "In the left subtree", "At the bottom right"],
          correctOption: 1,
          explanation: "The min-heap property ensures the root node contains the minimum value of the heap."
        },
        {
          id: 4,
          question: "What is the balance factor of an AVL tree node?",
          options: ["Height(Left) - Height(Right)", "Total Nodes Left", "Depth of Root", "Number of Leaf Nodes"],
          correctOption: 0,
          explanation: "Balance factor is defined as height of left subtree minus height of right subtree."
        },
        {
          id: 5,
          question: "Dijkstra's algorithm is used to solve which problem?",
          options: ["Minimum Spanning Tree", "Single-source shortest path", "Topological sorting", "String matching"],
          correctOption: 1,
          explanation: "Dijkstra's algorithm calculates the shortest path from a single source node to all other nodes in a weighted graph with non-negative edges."
        }
      ];

      // Build assigned students list based on selection
      let assignedList = [];
      if (assignmentTarget === 'ALL') {
        assignedList = ['ALL'];
      } else if (assignmentTarget === 'CSE') {
        assignedList = ['Computer Science & Engineering', 'CSE'];
      } else if (assignmentTarget === 'AIDS') {
        assignedList = ['Artificial Intelligence & Data Science', 'AIDS'];
      } else {
        assignedList = [assignmentTarget];
      }

      const newExam = {
        title: examTitle,
        company: examTitle,
        code: `EXAM-${Math.floor(1000 + Math.random() * 9000)}`,
        domain: domain,
        date: new Date().toISOString().split('T')[0],
        time: '10:00 AM',
        duration: '45 mins',
        status: 'Ready',
        instructions: 'AI Proctoring active. Camera, Microphone, and Fullscreen lock required.',
        assignedStudents: assignedList,
        questions: generatedQuestions
      };

      const created = addInterview(newExam);
      setCreatedExamId(created.id);
      setUploading(false);
      setUploadSuccess(true);
    }, 1000);
  };

  const handleReset = () => {
    setFile(null);
    setUploadSuccess(false);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-6 sm:p-8 space-y-6 text-slate-800">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">Upload Question Paper (PDF)</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            AI Service automatically generates MCQs from uploaded syllabus & question documents.
          </p>
        </div>
        <span className="px-3 py-1 bg-slate-100 border border-slate-200 text-slate-700 text-xs font-medium rounded-md flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>AI Engine Armed</span>
        </span>
      </div>

      {/* Form Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-700 uppercase tracking-wider mb-1">
            Exam Name
          </label>
          <input
            type="text"
            value={examTitle}
            onChange={(e) => setExamTitle(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-700 uppercase tracking-wider mb-1">
            Subject Domain
          </label>
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
          >
            <option value="Data Structures & Algorithms">Data Structures & Algorithms</option>
            <option value="Machine Learning">Machine Learning</option>
            <option value="Database Systems">Database Systems</option>
            <option value="Computer Networks">Computer Networks</option>
            <option value="Cyber Security">Cyber Security</option>
          </select>
        </div>
      </div>

      {/* Target Student Cohort Assignment */}
      <div>
        <label className="block text-xs font-medium text-slate-700 uppercase tracking-wider mb-1 flex items-center space-x-1">
          <Users className="w-3.5 h-3.5 text-slate-500" />
          <span>Assign Exam to Candidates / Cohort</span>
        </label>
        <select
          value={assignmentTarget}
          onChange={(e) => setAssignmentTarget(e.target.value)}
          className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 text-slate-800 rounded-md focus:outline-hidden focus:border-blue-500"
        >
          <option value="ALL">All Students (All Batches)</option>
          <option value="CSE">Computer Science & Engineering (CSE Dept)</option>
          <option value="AIDS">Artificial Intelligence & Data Science (AIDS Dept)</option>
          {students.map((s) => (
            <option key={s.id} value={s.id}>
              Specific Student: {s.name} ({s.rollNo || s.email})
            </option>
          ))}
        </select>
        <p className="text-[11px] text-slate-500 mt-1">
          Only candidates in the selected group will see this exam on their dashboard.
        </p>
      </div>

      {/* Drag & Drop Upload Zone */}
      {!uploadSuccess ? (
        <form onSubmit={handleUploadSubmit} className="space-y-4">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : file
                ? 'border-emerald-500 bg-emerald-50'
                : 'border-slate-200 bg-slate-50 hover:bg-slate-100 hover:border-slate-300'
            }`}
          >
            <input
              type="file"
              accept=".pdf"
              id="pdf-upload-input"
              className="hidden"
              onChange={handleFileChange}
            />

            <label htmlFor="pdf-upload-input" className="cursor-pointer block space-y-3">
              <div className="w-12 h-12 mx-auto rounded-lg bg-white border border-slate-200 text-slate-600 flex items-center justify-center shadow-xs">
                {file ? <FileText className="w-6 h-6 text-emerald-600" /> : <Upload className="w-6 h-6 text-slate-500" />}
              </div>

              {file ? (
                <div>
                  <p className="text-xs font-bold text-slate-900">{file.name}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB • PDF Document Verified
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-xs font-semibold text-slate-800">
                    Drag and drop your question paper PDF here
                  </p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    or <span className="text-blue-600 font-semibold underline">browse file from device</span> (PDF up to 20MB)
                  </p>
                </div>
              )}
            </label>
          </div>

          <div className="flex items-center justify-end space-x-3">
            {file && (
              <button
                type="button"
                onClick={() => setFile(null)}
                className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 rounded-md"
              >
                Clear
              </button>
            )}
            <button
              type="submit"
              disabled={!file || uploading}
              className="px-5 py-2 bg-[#374151] hover:bg-[#1F2937] text-white font-medium text-xs rounded-lg shadow-xs disabled:opacity-50 transition-colors flex items-center space-x-2"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
                  <span>Generating MCQs & Assigning...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload & Generate MCQs</span>
                </>
              )}
            </button>
          </div>
        </form>
      ) : (
        /* Success Message & Confirmation */
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 space-y-3">
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-emerald-600 text-white rounded-lg shadow-xs">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-emerald-900">Exam created and assigned successfully!</h3>
              <p className="text-xs text-emerald-700 mt-0.5">
                5 Multiple Choice Questions generated from <span className="font-semibold">{file?.name || 'QuestionPaper.pdf'}</span>.
              </p>
            </div>
          </div>

          <div className="bg-white border border-emerald-200 rounded-lg p-3 text-xs text-slate-700 space-y-1">
            <p><span className="font-semibold text-slate-900">Exam Name:</span> {examTitle}</p>
            <p><span className="font-semibold text-slate-900">Assigned Cohort:</span> {assignmentTarget === 'ALL' ? 'All Registered Students' : assignmentTarget}</p>
            <p className="text-[11px] text-slate-500">Students in this cohort can now launch the examination from their dashboard.</p>
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={handleReset}
              className="px-4 py-1.5 text-xs font-medium text-emerald-800 bg-emerald-100 hover:bg-emerald-200 rounded-md transition-colors"
            >
              Upload Another Paper
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

