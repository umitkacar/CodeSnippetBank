import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface RubberBandProps {
  children: ReactNode;
}

export const RubberBand = ({ children }: RubberBandProps) => (
  <motion.div
    animate={{
      scaleX: [1, 1.25, 0.75, 1.15, 0.95, 1.05, 1],
      scaleY: [1, 0.75, 1.25, 0.85, 1.05, 0.95, 1]
    }}
    transition={{ duration: 0.8 }}
  >
    {children}
  </motion.div>
);
