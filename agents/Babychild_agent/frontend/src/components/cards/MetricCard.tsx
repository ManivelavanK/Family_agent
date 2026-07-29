import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  label: string;
  primary: string;
  secondaryLabel?: string;
  secondaryValue?: string;
  badge?: string;
  badgeColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  icon: Icon,
  iconBg,
  iconColor,
  label,
  primary,
  secondaryLabel,
  secondaryValue,
  badge,
  badgeColor = 'bg-slate-100 text-slate-600',
}) => (
  <div className="group relative overflow-hidden rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
    <div className="flex items-start justify-between">
      <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconBg}`}>
        <Icon className={`h-5 w-5 ${iconColor}`} />
      </div>
      {badge && (
        <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${badgeColor}`}>
          {badge}
        </span>
      )}
    </div>
    <div className="mt-4">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900 leading-none">{primary}</p>
      {secondaryLabel && (
        <p className="mt-2 text-xs text-slate-400">
          <span className="font-medium text-slate-600">{secondaryValue}</span> {secondaryLabel}
        </p>
      )}
    </div>
  </div>
);

export default MetricCard;
