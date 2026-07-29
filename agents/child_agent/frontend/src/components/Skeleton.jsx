import React from 'react';

export function SkeletonLine({ w = 'w-full', h = 'h-4' }) {
  return <div className={`skeleton ${w} ${h} rounded-lg`} />;
}

export function SkeletonCard({ className = '' }) {
  return (
    <div className={`glass rounded-2xl p-5 space-y-3 ${className}`}>
      <div className="flex items-center gap-3">
        <div className="skeleton w-10 h-10 rounded-xl shrink-0" />
        <div className="flex-1 space-y-2">
          <SkeletonLine w="w-1/3" h="h-3" />
          <SkeletonLine w="w-2/3" h="h-5" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonText({ lines = 3 }) {
  const widths = ['w-full', 'w-5/6', 'w-4/5', 'w-3/4', 'w-2/3'];
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLine key={i} w={widths[i % widths.length]} h="h-3.5" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="w-full h-48 skeleton rounded-2xl" />
  );
}

export default function Skeleton({ children }) {
  return <>{children}</>;
}
