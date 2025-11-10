import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface ShakeProps {
  children: ReactNode;
}

export const Shake = ({ children }: ShakeProps) => (
  <motion.div
    animate={{ x: [0, -10, 10, -10, 10, 0] }}
    transition={{ duration: 0.5 }}
  >
    {children}
  </motion.div>
);
