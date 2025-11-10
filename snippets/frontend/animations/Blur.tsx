import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface BlurProps {
  children: ReactNode;
}

export const Blur = ({ children }: BlurProps) => (
  <motion.div
    initial={{ filter: 'blur(10px)', opacity: 0 }}
    animate={{ filter: 'blur(0px)', opacity: 1 }}
    transition={{ duration: 0.6 }}
  >
    {children}
  </motion.div>
);
