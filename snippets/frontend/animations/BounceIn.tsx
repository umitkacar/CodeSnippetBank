import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface BounceInProps {
  children: ReactNode;
}

export const BounceIn = ({ children }: BounceInProps) => (
  <motion.div
    initial={{ scale: 0, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{
      type: 'spring',
      stiffness: 500,
      damping: 15,
      duration: 0.6
    }}
  >
    {children}
  </motion.div>
);
