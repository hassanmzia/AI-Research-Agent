import React from 'react';

interface Props {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export default function ScoreGauge({ score, size = 'md' }: Props) {
  const sizeMap = { sm: 'h-10 w-10 text-xs', md: 'h-16 w-16 text-sm', lg: 'h-24 w-24 text-lg' };
  const color =
    score >= 70 ? 'text-green-600 border-green-400' :
    score >= 40 ? 'text-yellow-600 border-yellow-400' :
    'text-red-600 border-red-400';

  return (
    <div
      className={`${sizeMap[size]} rounded-full border-4 ${color} flex items-center justify-center font-bold`}
    >
      {score.toFixed(0)}
    </div>
  );
}
