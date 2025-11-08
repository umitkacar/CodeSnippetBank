import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface SwingProps {
  children: ReactNode;
}

export const Swing = ({ children }: SwingProps) => (
  <motion.div
    animate={{ rotate: [0, 15, -10, 5, -5, 0] }}
    transition={{ duration: 1 }}
    style={{ transformOrigin: 'top center' }}
  >
    {children}
  </motion.div>
);
