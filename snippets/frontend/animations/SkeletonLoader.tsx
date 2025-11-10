import { motion } from 'framer-motion';

interface SkeletonLoaderProps {
  width?: string;
  height?: string;
  borderRadius?: string;
}

export const SkeletonLoader = ({ width = '100%', height = '20px', borderRadius = '4px' }: SkeletonLoaderProps) => (
  <motion.div
    animate={{
      backgroundColor: ['#e5e7eb', '#f3f4f6', '#e5e7eb'],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    }}
    style={{
      width,
      height,
      borderRadius,
    }}
  />
);
