import { ref, onMounted, onUnmounted } from 'vue';

export function useBreakpoints() {
  const breakpoints = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536,
  };

  const width = ref(0);

  const update = () => {
    width.value = window.innerWidth;
  };

  onMounted(() => {
    update();
    window.addEventListener('resize', update);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', update);
  });

  const isGreaterThan = (breakpoint: keyof typeof breakpoints) => {
    return width.value >= breakpoints[breakpoint];
  };

  return {
    width,
    isGreaterThan,
    isSm: () => isGreaterThan('sm'),
    isMd: () => isGreaterThan('md'),
    isLg: () => isGreaterThan('lg'),
    isXl: () => isGreaterThan('xl'),
    is2xl: () => isGreaterThan('2xl'),
  };
}
