import { motion } from 'framer-motion';

interface SpinnerAnimationProps {
  size?: number;
  color?: string;
}

export const SpinnerAnimation = ({ size = 40, color = '#3b82f6' }: SpinnerAnimationProps) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    }}
    style={{
      width: size,
      height: size,
      border: `3px solid #e5e7eb`,
      borderTop: `3px solid ${color}`,
      borderRadius: '50%',
    }}
  />
);
