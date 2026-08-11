import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { BarChart3, TrendingUp, ShieldCheck } from 'lucide-react';
import { MOCK_GRAPH_DATA } from '../../utils/mockData';

export default function SystemReports() {
  return (
    <div className="space-y-6 text-slate-800">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">University Analytics & System Reports</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Visual performance indicators across student subject scores, examination traffic, and AI proctoring audits.
        </p>
      </div>

      {/* Grid of Recharts Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 1. Student Performance Graph */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span>Student Performance by Subject</span>
            </h3>
            <span className="text-[11px] font-semibold text-blue-600">Avg vs Top Marks</span>
          </div>

          <div className="h-64 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_GRAPH_DATA.studentPerformance}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="subject" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '11px', color: '#0f172a' }} />
                <Legend wrapperStyle={{ fontSize: '11px', color: '#475569' }} />
                <Bar dataKey="avgScore" name="Average Score %" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="topScore" name="Top Mark %" fill="#059669" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. System Usage & Hourly Exam Traffic */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              <span>Monthly Examinations Traffic</span>
            </h3>
            <span className="text-[11px] font-semibold text-emerald-600">+28% Growth</span>
          </div>

          <div className="h-64 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={MOCK_GRAPH_DATA.systemUsage}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '11px', color: '#0f172a' }} />
                <Area type="monotone" dataKey="examsConducted" name="Exams Conducted" stroke="#4f46e5" fill="#e0e7ff" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. AI Proctoring Violation Breakdown */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>AI Proctoring Session Audit Breakdown</span>
            </h3>
            <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200">
              92% Clean Sessions
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={MOCK_GRAPH_DATA.proctoringDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {MOCK_GRAPH_DATA.proctoringDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '11px', color: '#0f172a' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-2 text-xs">
              {MOCK_GRAPH_DATA.proctoringDistribution.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-100 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.fill }} />
                    <span className="font-bold text-slate-800">{item.name}</span>
                  </div>
                  <span className="font-extrabold text-slate-900">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

