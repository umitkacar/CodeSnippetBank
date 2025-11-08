import { useState } from 'react';
import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface MouseFollowProps {
  children: ReactNode;
}

export const MouseFollow = ({ children }: MouseFollowProps) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  return (
    <motion.div
      onMouseMove={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        setMousePosition({
          x: e.clientX - rect.left - rect.width / 2,
          y: e.clientY - rect.top - rect.height / 2,
        });
      }}
      onMouseLeave={() => setMousePosition({ x: 0, y: 0 })}
    >
      <motion.div
        animate={{
          x: mousePosition.x * 0.1,
          y: mousePosition.y * 0.1,
        }}
        transition={{ type: 'spring', stiffness: 150, damping: 15 }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
};
