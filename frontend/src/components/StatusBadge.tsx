import React from 'react';

const statusConfig: Record<string, { bg: string; text: string; dot: string }> = {
  pending: { bg: 'bg-yellow-50', text: 'text-yellow-700', dot: 'bg-yellow-400' },
  running: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-400' },
  completed: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-400' },
  failed: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
  cancelled: { bg: 'bg-gray-50', text: 'text-gray-700', dot: 'bg-gray-400' },
  high: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-400' },
  medium: { bg: 'bg-yellow-50', text: 'text-yellow-700', dot: 'bg-yellow-400' },
  low: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
};

export default function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || statusConfig.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
