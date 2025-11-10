import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface SlideDownProps {
  children: ReactNode;
  delay?: number;
}

export const SlideDown = ({ children, delay = 0 }: SlideDownProps) => (
  <motion.div
    initial={{ opacity: 0, y: -50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay, ease: 'easeOut' }}
  >
    {children}
  </motion.div>
);
