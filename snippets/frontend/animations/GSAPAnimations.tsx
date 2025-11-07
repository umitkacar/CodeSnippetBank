/**
 * GSAP Animation Examples
 */
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Fade in animation
export const GSAPFadeIn = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    gsap.fromTo(
      ref.current,
      { opacity: 0 },
      { opacity: 1, duration: 1, ease: 'power2.out' }
    );
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Slide in from left
export const GSAPSlideIn = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    gsap.fromTo(
      ref.current,
      { x: -100, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.8, ease: 'power3.out' }
    );
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Scroll-triggered animation
export const GSAPScrollReveal = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    gsap.fromTo(
      ref.current,
      { y: 50, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 1,
        scrollTrigger: {
          trigger: ref.current,
          start: 'top 80%',
          end: 'bottom 20%',
          toggleActions: 'play none none reverse',
        },
      }
    );
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Stagger animation
export const GSAPStagger = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    const elements = ref.current?.children;
    if (elements) {
      gsap.fromTo(
        elements,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, stagger: 0.2, duration: 0.8, ease: 'power2.out' }
      );
    }
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Parallax scrolling
export const GSAPParallax = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    gsap.to(ref.current, {
      y: -100,
      ease: 'none',
      scrollTrigger: {
        trigger: ref.current,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true,
      },
    });
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Rotating animation
export const GSAPRotate = ({ children }: any) => {
  const ref = useRef(null);

  useEffect(() => {
    gsap.to(ref.current, {
      rotation: 360,
      duration: 2,
      repeat: -1,
      ease: 'linear',
    });
  }, []);

  return <div ref={ref}>{children}</div>;
};

// Text reveal animation
export const GSAPTextReveal = ({ text }: { text: string }) => {
  const ref = useRef(null);

  useEffect(() => {
    const chars = ref.current?.querySelectorAll('.char');
    if (chars) {
      gsap.fromTo(
        chars,
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, stagger: 0.05, duration: 0.5 }
      );
    }
  }, []);

  return (
    <div ref={ref}>
      {text.split('').map((char, i) => (
        <span key={i} className="char">
          {char}
        </span>
      ))}
    </div>
  );
};
