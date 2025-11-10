import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface HeartBeatProps {
  children: ReactNode;
}

export const HeartBeat = ({ children }: HeartBeatProps) => (
  <motion.div
    animate={{ scale: [1, 1.3, 1, 1.3, 1] }}
    transition={{ duration: 1.3, repeat: Infinity }}
  >
    {children}
  </motion.div>
);
