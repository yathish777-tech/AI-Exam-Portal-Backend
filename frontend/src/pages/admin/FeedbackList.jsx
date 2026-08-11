import React from 'react';
import { Star, CheckCircle2, User, Inbox } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import { useData } from '../../context/DataContext';

export default function FeedbackList() {
  const { feedbacks, updateFeedback } = useData();

  const handleResolve = (id) => {
    updateFeedback(id, { status: 'Resolved' });
  };

  return (
    <div className="space-y-6 text-slate-800">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">University Portal Feedback & Reviews</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Submissions from students, professors, and examination invigilators.
        </p>
      </div>

      {feedbacks.length === 0 ? (
        <div className="bg-white rounded-xl p-10 text-center border border-slate-200/80 shadow-xs space-y-2">
          <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full mx-auto flex items-center justify-center">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">No Feedback Submitted</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            User feedback will appear here as candidates submit ratings post-assessment.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {feedbacks.map((fb) => (
            <div key={fb.id} className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-blue-600" />
                    <span className="font-bold text-slate-900 text-sm">{fb.user}</span>
                  </div>
                  <Badge variant={fb.status === 'Resolved' ? 'emerald' : 'amber'}>{fb.status}</Badge>
                </div>

                <div className="flex items-center space-x-2 text-xs">
                  <span className="px-2 py-0.5 bg-slate-100 text-slate-700 border border-slate-200 rounded font-medium">{fb.category}</span>
                  <span className="text-amber-600 font-bold flex items-center">
                    <Star className="w-3.5 h-3.5 fill-amber-500 stroke-amber-500 inline mr-1" />
                    {fb.rating}/5
                  </span>
                  <span className="text-slate-400 text-[11px]">• {fb.date}</span>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                  "{fb.message}"
                </p>
              </div>

              {fb.status !== 'Resolved' && (
                <div className="pt-2">
                  <button
                    onClick={() => handleResolve(fb.id)}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded-md shadow-xs transition-colors flex items-center space-x-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Mark as Resolved</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

