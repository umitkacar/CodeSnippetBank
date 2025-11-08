import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface WobbleProps {
  children: ReactNode;
}

export const Wobble = ({ children }: WobbleProps) => (
  <motion.div
    animate={{
      rotate: [0, -5, 5, -5, 5, 0],
      x: [0, -25, 25, -25, 25, 0]
    }}
    transition={{ duration: 0.8 }}
  >
    {children}
  </motion.div>
);
