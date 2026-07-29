import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStyle = (val: string) => {
    const v = val.toLowerCase();
    if (v.includes("normal") || v.includes("delivered") || v.includes("sent") || v.includes("completed") || v.includes("taken") || v.includes("resolved") || v.includes("active") || v.includes("sufficient")) {
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    }
    if (v.includes("warning") || v.includes("moderate") || v.includes("pending") || v.includes("upcoming") || v.includes("low stock")) {
      return "bg-amber-50 text-amber-700 border-amber-200";
    }
    if (v.includes("critical") || v.includes("failed") || v.includes("missed") || v.includes("triggered") || v.includes("high")) {
      return "bg-rose-50 text-rose-700 border-rose-200";
    }
    return "bg-slate-50 text-slate-700 border-slate-200";
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold border ${getStyle(status)}`}>
      {status}
    </span>
  );
};
export default StatusBadge;
