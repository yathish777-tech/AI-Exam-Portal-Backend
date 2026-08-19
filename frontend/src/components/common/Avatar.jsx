import React from 'react';

/**
 * Reusable Avatar Component
 * Displays a circular initial avatar in the light-green + white theme.
 * Displays the first letter of the user's name, or 'U' as fallback.
 */
export default function Avatar({ name, size = 'sm', className = '' }) {
  const getInitial = (str) => {
    if (!str || typeof str !== 'string') return 'U';
    const trimmed = str.trim();
    if (!trimmed) return 'U';
    const match = trimmed.match(/[a-zA-Z0-9]/);
    return match ? match[0].toUpperCase() : trimmed.charAt(0).toUpperCase() || 'U';
  };

  const initial = getInitial(name);

  const sizeMap = {
    xs: 'w-6 h-6 text-[10px]',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-16 h-16 text-xl',
    xl: 'w-20 h-20 text-2xl',
  };

  const sizeClass = sizeMap[size] || size;

  return (
    <div
      className={`rounded-full bg-emerald-100 border border-emerald-200 text-emerald-900 font-bold flex items-center justify-center shrink-0 select-none shadow-2xs ${sizeClass} ${className}`}
      aria-label={name || 'User Avatar'}
      title={name || 'User'}
    >
      <span>{initial}</span>
    </div>
  );
}
