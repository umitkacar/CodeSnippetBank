import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface FlipInProps {
  children: ReactNode;
}

export const FlipIn = ({ children }: FlipInProps) => (
  <motion.div
    initial={{ rotateY: 90, opacity: 0 }}
    animate={{ rotateY: 0, opacity: 1 }}
    transition={{ duration: 0.6 }}
    style={{ transformStyle: 'preserve-3d' }}
  >
    {children}
  </motion.div>
);
