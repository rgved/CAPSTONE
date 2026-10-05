import { Link } from "react-router-dom";

interface LogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  showIcon?: boolean;
  showSubtitle?: boolean;
  to?: string;
  className?: string;
}

export default function Logo({
  size = "md",
  showIcon = true,
  showSubtitle = true,
  to = "/",
  className = ""
}: LogoProps) {
  const sizeClasses = {
    sm: {
      text: "text-xl",
      icon: "w-7 h-7 text-base rounded-lg",
      subtitle: "text-[9px]"
    },
    md: {
      text: "text-2xl",
      icon: "w-9 h-9 text-lg rounded-xl",
      subtitle: "text-[10px]"
    },
    lg: {
      text: "text-3xl",
      icon: "w-11 h-11 text-xl rounded-xl",
      subtitle: "text-xs"
    },
    xl: {
      text: "text-4xl",
      icon: "w-14 h-14 text-2xl rounded-2xl",
      subtitle: "text-sm"
    }
  };

  const selectedSize = sizeClasses[size];

  const content = (
    <div className={`inline-flex items-center gap-3 select-none group ${className}`}>
      {showIcon && (
        <div className={`${selectedSize.icon} bg-gradient-to-tr from-blue-600 via-indigo-500 to-emerald-400 p-[1.5px] shadow-lg shadow-blue-500/15 shrink-0 transition-transform duration-300 group-hover:scale-105`}>
          <div className="w-full h-full bg-[#0B1220] rounded-[inherit] flex items-center justify-center">
            <span className="font-brand text-white italic pl-0.5 leading-none">
              S.
            </span>
          </div>
        </div>
      )}
      <div className="flex flex-col">
        <span className={`font-brand ${selectedSize.text} tracking-tight text-[#F8FAFC] italic leading-tight group-hover:text-white transition-colors`}>
          Sniff<span className="text-[#3B82F6] group-hover:text-[#60A5FA] transition-colors">.</span>
        </span>
        {showSubtitle && (
          <span className={`${selectedSize.subtitle} font-semibold tracking-[0.2em] text-[#94A3B8] uppercase leading-none mt-0.5`}>
            Security Recon
          </span>
        )}
      </div>
    </div>
  );

  if (to) {
    return (
      <Link to={to} className="inline-block transition-opacity hover:opacity-95 focus:outline-none">
        {content}
      </Link>
    );
  }

  return content;
}
