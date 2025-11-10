import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface WaveProps {
  children: ReactNode;
}

export const Wave = ({ children }: WaveProps) => (
  <motion.div
    animate={{ y: [0, -20, 0] }}
    transition={{
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }}
  >
    {children}
  </motion.div>
);
