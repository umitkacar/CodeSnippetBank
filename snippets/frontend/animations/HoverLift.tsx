import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface HoverLiftProps {
  children: ReactNode;
}

export const HoverLift = ({ children }: HoverLiftProps) => (
  <motion.div
    whileHover={{ y: -5, boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)' }}
    transition={{ duration: 0.2 }}
  >
    {children}
  </motion.div>
);
