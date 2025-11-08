import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface GlowInProps {
  children: ReactNode;
  color?: string;
}

export const GlowIn = ({ children, color = '#3b82f6' }: GlowInProps) => (
  <motion.div
    initial={{
      opacity: 0,
      boxShadow: '0 0 0px rgba(59, 130, 246, 0)'
    }}
    animate={{
      opacity: 1,
      boxShadow: `0 0 20px ${color}`
    }}
    transition={{ duration: 0.5 }}
  >
    {children}
  </motion.div>
);
