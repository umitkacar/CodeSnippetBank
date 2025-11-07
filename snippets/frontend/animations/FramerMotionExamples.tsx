/**
 * Framer Motion Animation Examples
 */
import { motion, useAnimation, useInView, AnimatePresence } from 'framer-motion';
import { useRef, useEffect } from 'react';

// Fade in animation
export const FadeIn = ({ children, delay = 0 }: any) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5, delay }}
  >
    {children}
  </motion.div>
);

// Slide up animation
export const SlideUp = ({ children }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, ease: 'easeOut' }}
  >
    {children}
  </motion.div>
);

// Scale animation
export const ScaleIn = ({ children }: any) => (
  <motion.div
    initial={{ scale: 0 }}
    animate={{ scale: 1 }}
    transition={{ type: 'spring', stiffness: 260, damping: 20 }}
  >
    {children}
  </motion.div>
);

// Staggered children animation
export const StaggerContainer = ({ children }: any) => (
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
    {children}
  </motion.div>
);

export const StaggerItem = ({ children }: any) => (
  <motion.div
    variants={{
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 },
    }}
  >
    {children}
  </motion.div>
);

// Scroll-triggered animation
export const ScrollReveal = ({ children }: any) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.8 }}
    >
      {children}
    </motion.div>
  );
};

// Page transition
export const PageTransition = ({ children }: any) => (
  <AnimatePresence mode="wait">
    <motion.div
      initial={{ opacity: 0, x: -100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  </AnimatePresence>
);

// Hover animation
export const HoverScale = ({ children }: any) => (
  <motion.div
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
  >
    {children}
  </motion.div>
);

// Parallax effect
export const Parallax = ({ children, offset = 50 }: any) => (
  <motion.div
    initial={{ y: 0 }}
    animate={{ y: offset }}
    transition={{ type: 'spring', stiffness: 100 }}
  >
    {children}
  </motion.div>
);

// Rotate animation
export const RotateIn = ({ children }: any) => (
  <motion.div
    initial={{ rotate: -180, opacity: 0 }}
    animate={{ rotate: 0, opacity: 1 }}
    transition={{ duration: 0.5 }}
  >
    {children}
  </motion.div>
);

// Path animation
export const PathAnimation = () => (
  <svg width="200" height="200">
    <motion.path
      d="M 10 80 Q 95 10 180 80"
      fill="transparent"
      stroke="black"
      strokeWidth="3"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 2, ease: 'easeInOut' }}
    />
  </svg>
);
