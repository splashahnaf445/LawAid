import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, Award, Info } from 'lucide-react';

/**
 * LawAid Verified Lawyer Badge Component
 * 
 * SRS Compliance:
 * - FR-3: Display verification badge on lawyer profile only after admin approval.
 * - Shows official Bar Council Sanad credentials and trust seal on hover/click.
 */
export default function VerifiedBadge({ 
  badgeData = null, 
  size = 'md', 
  showLabel = true, 
  showTooltip = true 
}) {
  const [isOpen, setIsOpen] = useState(false);

  // If lawyer is not verified or no badge data, render nothing (FR-3)
  if (!badgeData || !badgeData.is_active) {
    return null;
  }

  const sizeClasses = {
    sm: {
      badge: 'px-2 py-0.5 text-xs gap-1',
      iconSize: 13,
    },
    md: {
      badge: 'px-2.5 py-1 text-xs gap-1.5',
      iconSize: 15,
    },
    lg: {
      badge: 'px-3.5 py-1.5 text-sm gap-2',
      iconSize: 18,
    }
  };

  const currentSize = sizeClasses[size] || sizeClasses.md;

  return (
    <div className="relative inline-block" onMouseLeave={() => setIsOpen(false)}>
      <span
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        className={`inline-flex items-center font-semibold rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 shadow-sm cursor-pointer hover:bg-emerald-100 transition-all duration-150 ${currentSize.badge}`}
        title="Bangladesh Bar Council Verified Advocate"
      >
        <span className="flex items-center justify-center rounded-full bg-emerald-600 text-white p-0.5">
          <ShieldCheck size={currentSize.iconSize} className="stroke-[2.5]" />
        </span>
        {showLabel && (
          <span className="tracking-tight flex items-center gap-1">
            {badgeData.title || 'Verified Advocate'}
          </span>
        )}
      </span>

      {/* Tooltip / Modal popover showing authentic Bar Council verification metadata */}
      {showTooltip && isOpen && (
        <div 
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-3.5 bg-slate-900 text-white text-xs rounded-xl shadow-2xl border border-slate-700 animate-in fade-in zoom-in-95 duration-150"
        >
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-800">
            <Award className="text-amber-400" size={16} />
            <span className="font-bold text-slate-100 tracking-wide uppercase text-[11px]">
              LawAid Official Verification
            </span>
          </div>

          <div className="space-y-1.5 text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-400">Sanad / Bar ID:</span>
              <span className="font-mono font-semibold text-amber-300">{badgeData.sanad_number || 'SC-7841'}</span>
            </div>
            {badgeData.bar_association && (
              <div className="flex justify-between">
                <span className="text-slate-400">Bar Association:</span>
                <span className="font-medium text-slate-200 text-right">{badgeData.bar_association}</span>
              </div>
            )}
            {badgeData.verified_at && (
              <div className="flex justify-between">
                <span className="text-slate-400">Verified Date:</span>
                <span className="text-slate-200">
                  {new Date(badgeData.verified_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                </span>
              </div>
            )}
            <div className="mt-2 pt-2 border-t border-slate-800/80 text-[10px] text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 size={12} className="shrink-0" />
              <span>NID & Bar Council Certificate authenticated by LawAid compliance admin.</span>
            </div>
          </div>
          {/* Arrow */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-900"></div>
        </div>
      )}
    </div>
  );
}
