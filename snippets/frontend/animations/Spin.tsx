import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface SpinProps {
  children: ReactNode;
}

export const Spin = ({ children }: SpinProps) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{
      duration: 2,
      repeat: Infinity,
      ease: 'linear'
    }}
  >
    {children}
  </motion.div>
);
