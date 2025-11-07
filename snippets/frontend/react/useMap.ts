import { useState, useCallback } from 'react';

/**
 * Custom hook for Map data structure
 */
export function useMap<K, V>(initialValues?: [K, V][]) {
  const [map, setMap] = useState<Map<K, V>>(new Map(initialValues));

  const set = useCallback((key: K, value: V) => {
    setMap((prevMap) => {
      const newMap = new Map(prevMap);
      newMap.set(key, value);
      return newMap;
    });
  }, []);

  const remove = useCallback((key: K) => {
    setMap((prevMap) => {
      const newMap = new Map(prevMap);
      newMap.delete(key);
      return newMap;
    });
  }, []);

  const clear = useCallback(() => {
    setMap(new Map());
  }, []);

  const get = useCallback(
    (key: K) => {
      return map.get(key);
    },
    [map]
  );

  const has = useCallback(
    (key: K) => {
      return map.has(key);
    },
    [map]
  );

  return {
    map,
    set,
    get,
    remove,
    clear,
    has,
    size: map.size,
  };
}
