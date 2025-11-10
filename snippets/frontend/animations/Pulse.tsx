import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface PulseProps {
  children: ReactNode;
}

export const Pulse = ({ children }: PulseProps) => (
  <motion.div
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ duration: 1, repeat: Infinity }}
  >
    {children}
  </motion.div>
);
