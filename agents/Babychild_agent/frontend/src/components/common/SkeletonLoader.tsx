import React from 'react';

// Generic skeleton shimmer block
export const SkeletonBlock: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`animate-pulse bg-slate-200 rounded-lg ${className}`} />
);

// Card-level skeleton
export const SkeletonCard: React.FC = () => (
  <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm space-y-3">
    <SkeletonBlock className="h-4 w-1/3" />
    <SkeletonBlock className="h-8 w-1/2" />
    <SkeletonBlock className="h-3 w-2/3" />
  </div>
);

// Full AI insight loading state
export const AILoader: React.FC = () => (
  <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-violet-100 bg-gradient-to-br from-violet-50 to-indigo-50 p-10 text-center">
    <div className="relative flex h-16 w-16 items-center justify-center">
      <div className="absolute h-16 w-16 animate-ping rounded-full bg-violet-300 opacity-20" />
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-100 text-violet-600">
        <svg className="h-6 w-6 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    </div>
    <div>
      <p className="text-sm font-semibold text-violet-700">✨ Baby Care Agent is analyzing your baby's health...</p>
      <p className="text-xs text-slate-500 mt-1">Checking sleep, feeding, growth, and health logs.</p>
    </div>
  </div>
);

// Dashboard metric grid skeleton
export const DashboardSkeleton: React.FC = () => (
  <div className="space-y-6">
    <div className="animate-pulse rounded-2xl border border-violet-100 bg-gradient-to-br from-violet-50 to-indigo-50 p-6 h-36" />
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
      {Array.from({ length: 5 }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
    <div className="animate-pulse rounded-2xl bg-white border border-slate-100 p-6 h-48" />
  </div>
);

export default AILoader;
