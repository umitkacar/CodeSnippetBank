import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface RotateInProps {
  children: ReactNode;
}

export const RotateIn = ({ children }: RotateInProps) => (
  <motion.div
    initial={{ rotate: -180, opacity: 0 }}
    animate={{ rotate: 0, opacity: 1 }}
    transition={{ duration: 0.5 }}
  >
    {children}
  </motion.div>
);
