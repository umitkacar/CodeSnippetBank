import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface TadaProps {
  children: ReactNode;
}

export const Tada = ({ children }: TadaProps) => (
  <motion.div
    animate={{
      scale: [1, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1],
      rotate: [0, -3, -3, 3, -3, 3, -3, 3, -3, 0]
    }}
    transition={{ duration: 1 }}
  >
    {children}
  </motion.div>
);
