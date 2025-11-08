import { motion } from 'framer-motion';

export const Ping = () => (
  <div style={{ position: 'relative', width: '20px', height: '20px' }}>
    <motion.span
      animate={{
        scale: [1, 2],
        opacity: [1, 0]
      }}
      transition={{
        duration: 1,
        repeat: Infinity
      }}
      style={{
        position: 'absolute',
        inset: 0,
        borderRadius: '50%',
        backgroundColor: '#3b82f6',
      }}
    />
    <span style={{
      position: 'relative',
      display: 'inline-flex',
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      backgroundColor: '#3b82f6',
    }} />
  </div>
);
