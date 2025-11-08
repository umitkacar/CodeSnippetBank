import { motion } from 'framer-motion';

export const LoadingDots = () => {
  const dotVariants = {
    initial: { y: 0 },
    animate: { y: -10 },
  };

  return (
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          variants={dotVariants}
          initial="initial"
          animate="animate"
          transition={{
            duration: 0.5,
            repeat: Infinity,
            repeatType: 'reverse',
            delay: index * 0.15,
          }}
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: '#3b82f6',
          }}
        />
      ))}
    </div>
  );
};
