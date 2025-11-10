import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface StaggeredFadeInProps {
  children: ReactNode[];
}

export const StaggeredFadeIn = ({ children }: StaggeredFadeInProps) => (
  <motion.div
    initial="hidden"
    animate="visible"
    variants={{
      visible: {
        transition: {
          staggerChildren: 0.1,
        },
      },
    }}
  >
    {children.map((child, index) => (
      <motion.div
        key={index}
        variants={{
          hidden: { opacity: 0, y: 20 },
          visible: { opacity: 1, y: 0 },
        }}
      >
        {child}
      </motion.div>
    ))}
  </motion.div>
);
