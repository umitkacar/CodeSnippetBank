import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface ZoomInProps {
  children: ReactNode;
}

export const ZoomIn = ({ children }: ZoomInProps) => (
  <motion.div
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{ duration: 0.4 }}
  >
    {children}
  </motion.div>
);
