import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface ProgressBarProps {
  progress: number;
  height?: string;
  color?: string;
  children?: ReactNode;
}

export const ProgressBar = ({ progress, height = '8px', color = '#3b82f6', children }: ProgressBarProps) => (
  <motion.div
    style={{
      width: '100%',
      height,
      backgroundColor: '#e5e7eb',
      borderRadius: '4px',
      overflow: 'hidden',
    }}
  >
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: `${progress}%` }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      style={{
        height: '100%',
        backgroundColor: color,
        borderRadius: '4px',
      }}
    >
      {children}
    </motion.div>
  </motion.div>
);
