import React from 'react';

interface SivoraLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showSubtitle?: boolean;
}

export const SivoraLogo: React.FC<SivoraLogoProps> = ({
  className = '',
  size = 'md',
  showSubtitle = true,
}) => {
  const sizeClasses = {
    sm: { img: 'h-8 w-8', text: 'text-lg', sub: 'text-[9px]' },
    md: { img: 'h-10 w-10', text: 'text-xl', sub: 'text-[10px]' },
    lg: { img: 'h-14 w-14', text: 'text-3xl', sub: 'text-xs' },
  }[size];

  return (
    <div className={`flex items-center gap-2.5 group select-none ${className}`}>
      {/* Brand Monogram Icon */}
      <div className="relative overflow-hidden rounded-xl shadow-md border border-amber-300/30 group-hover:scale-105 transition-transform duration-300">
        <img
          src="/sivora_logo.jpg"
          alt="SIVORA Logo"
          className={`${sizeClasses.img} object-cover`}
        />
        <div className="absolute inset-0 bg-gradient-to-tr from-pink-600/10 to-transparent pointer-events-none" />
      </div>

      {/* Brand Name Typography */}
      <div className="flex flex-col">
        <div className="flex items-center gap-1.5 leading-none">
          <span className={`font-black tracking-[0.2em] uppercase bg-gradient-to-r from-pink-600 via-rose-500 to-amber-600 bg-clip-text text-transparent ${sizeClasses.text}`}>
            S I V O R A
          </span>
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-pink-500 animate-pulse" />
        </div>
        {showSubtitle && (
          <span className={`tracking-[0.3em] uppercase text-muted-foreground font-semibold mt-0.5 ${sizeClasses.sub}`}>
            LUXE FASHION & AI
          </span>
        )}
      </div>
    </div>
  );
};

export default SivoraLogo;
