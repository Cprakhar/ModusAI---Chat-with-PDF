import React, { useState, useEffect } from "react";

interface FadeMessageProps {
  message: string;
  duration?: number; // milliseconds, default 2000
  className?: string;
  onFadeComplete?: () => void;
}

export const FadeMessage: React.FC<FadeMessageProps> = ({ message, duration = 2000, className = "", onFadeComplete }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const fadeTimer = setTimeout(() => setVisible(false), duration);
    // Remove from DOM after fade transition (1s)
    const removeTimer = setTimeout(() => {
      if (onFadeComplete) onFadeComplete();
    }, duration + 1000);
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, [duration, onFadeComplete]);

  return (
    <div
      className={`transition-opacity duration-1000 ${visible ? "opacity-100" : "opacity-0"} ${className} bg-green-600 text-white text-sm px-4 py-2 rounded-lg mt-2`}
      style={{ pointerEvents: "none" }}
    >
      {message}
    </div>
  );
};
