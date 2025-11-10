import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface JelloProps {
  children: ReactNode;
}

export const Jello = ({ children }: JelloProps) => (
  <motion.div
    animate={{
      skewX: [0, -12.5, 6.25, -3.125, 1.5625, -0.78125, 0],
      skewY: [0, -12.5, 6.25, -3.125, 1.5625, -0.78125, 0]
    }}
    transition={{ duration: 0.8 }}
  >
    {children}
  </motion.div>
);
