import { useState } from 'react';
import { motion } from 'framer-motion';

export const MorphShape = () => {
  const [isCircle, setIsCircle] = useState(true);

  return (
    <motion.div
      onClick={() => setIsCircle(!isCircle)}
      animate={{
        borderRadius: isCircle ? '50%' : '0%',
      }}
      transition={{ duration: 0.5 }}
      style={{
        width: '100px',
        height: '100px',
        backgroundColor: '#3b82f6',
        cursor: 'pointer',
      }}
    />
  );
};
