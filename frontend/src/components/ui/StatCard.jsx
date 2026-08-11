import React from 'react';

export default function StatCard({ title, value, icon: Icon, color = 'blue', description, trend }) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-100',
    },
    indigo: {
      bg: 'bg-indigo-50',
      text: 'text-indigo-600',
      border: 'border-indigo-100',
    },
    emerald: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-600',
      border: 'border-emerald-100',
    },
    amber: {
      bg: 'bg-amber-50',
      text: 'text-amber-600',
      border: 'border-amber-100',
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      border: 'border-purple-100',
    },
    rose: {
      bg: 'bg-rose-50',
      text: 'text-rose-600',
      border: 'border-rose-100',
    },
  };

  const theme = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all duration-200 flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-slate-900 mt-1.5 tracking-tight">{value}</h3>
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg ${theme.bg} ${theme.text} ${theme.border} border`}>
            <Icon className="w-5 h-5 stroke-[2]" />
          </div>
        )}
      </div>

      {(description || trend) && (
        <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
          {description && <span className="text-slate-500 font-medium">{description}</span>}
          {trend && <span className="font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">{trend}</span>}
        </div>
      )}
    </div>
  );
}

