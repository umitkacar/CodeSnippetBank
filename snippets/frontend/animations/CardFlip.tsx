import { useState } from 'react';
import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface CardFlipProps {
  front: ReactNode;
  back: ReactNode;
}

export const CardFlip = ({ front, back }: CardFlipProps) => {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div onClick={() => setIsFlipped(!isFlipped)} style={{ perspective: '1000px', cursor: 'pointer' }}>
      <motion.div
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.6 }}
        style={{
          transformStyle: 'preserve-3d',
          position: 'relative',
        }}
      >
        <div style={{ backfaceVisibility: 'hidden' }}>
          {front}
        </div>
        <div style={{
          backfaceVisibility: 'hidden',
          position: 'absolute',
          top: 0,
          left: 0,
          transform: 'rotateY(180deg)'
        }}>
          {back}
        </div>
      </motion.div>
    </div>
  );
};
