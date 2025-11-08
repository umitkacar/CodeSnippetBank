import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface FlashProps {
  children: ReactNode;
}

export const Flash = ({ children }: FlashProps) => (
  <motion.div
    animate={{ opacity: [1, 0, 1, 0, 1] }}
    transition={{ duration: 1 }}
  >
    {children}
  </motion.div>
);
