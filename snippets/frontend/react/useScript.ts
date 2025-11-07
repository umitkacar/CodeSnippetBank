import { useState, useEffect } from 'react';

/**
 * Custom hook for dynamically loading external scripts
 */
type ScriptStatus = 'idle' | 'loading' | 'ready' | 'error';

export function useScript(src: string) {
  const [status, setStatus] = useState<ScriptStatus>('idle');

  useEffect(() => {
    if (!src) {
      setStatus('idle');
      return;
    }

    // Check if script already exists
    let script = document.querySelector<HTMLScriptElement>(
      `script[src="${src}"]`
    );

    if (!script) {
      script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.setAttribute('data-status', 'loading');
      document.body.appendChild(script);

      const setAttributeFromEvent = (event: Event) => {
        const status = event.type === 'load' ? 'ready' : 'error';
        script?.setAttribute('data-status', status);
      };

      script.addEventListener('load', setAttributeFromEvent);
      script.addEventListener('error', setAttributeFromEvent);
    } else {
      setStatus(script.getAttribute('data-status') as ScriptStatus);
    }

    const setStateFromEvent = (event: Event) => {
      setStatus(event.type === 'load' ? 'ready' : 'error');
    };

    script.addEventListener('load', setStateFromEvent);
    script.addEventListener('error', setStateFromEvent);

    return () => {
      if (script) {
        script.removeEventListener('load', setStateFromEvent);
        script.removeEventListener('error', setStateFromEvent);
      }
    };
  }, [src]);

  return status;
}
