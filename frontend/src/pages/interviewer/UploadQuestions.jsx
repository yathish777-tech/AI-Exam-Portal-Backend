import React from 'react';
import QuestionUploadForm from '../../components/forms/QuestionUploadForm';

export default function UploadQuestions() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto text-slate-100">
      <div>
        <h2 className="text-xl font-bold text-white">Upload Examination Question Papers</h2>
        <p className="text-xs text-slate-400 mt-1">
          Convert PDF documents and syllabus outlines into AI-generated multiple choice questions.
        </p>
      </div>

      <QuestionUploadForm />
    </div>
  );
}
