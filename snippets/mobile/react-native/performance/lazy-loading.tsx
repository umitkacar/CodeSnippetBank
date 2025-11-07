import React, { Suspense, lazy, useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

// Lazy load component
const HeavyComponent = lazy(() => import('./HeavyComponent'));

export const LazyLoadedScreen: React.FC = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <HeavyComponent />
    </Suspense>
  );
};

const LoadingFallback: React.FC = () => (
  <View style={styles.loading}>
    <ActivityIndicator size="large" color="#6200ee" />
    <Text>Loading...</Text>
  </View>
);

// Image lazy loading with intersection observer concept
export const LazyImage: React.FC<{ uri: string; height: number }> = ({ uri, height }) => {
  const [visible, setVisible] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // Simulate visibility check
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) {
    return <View style={[styles.imagePlaceholder, { height }]} />;
  }

  return (
    <View style={{ height }}>
      {!loaded && (
        <View style={[styles.imagePlaceholder, StyleSheet.absoluteFill]}>
          <ActivityIndicator />
        </View>
      )}
      <Image
        source={{ uri }}
        style={{ width: '100%', height: '100%' }}
        onLoad={() => setLoaded(true)}
      />
    </View>
  );
};

// Component code splitting
export const CodeSplitRoute: React.FC = () => {
  const [Component, setComponent] = useState<React.ComponentType | null>(null);

  useEffect(() => {
    import('./DynamicComponent').then((module) => {
      setComponent(() => module.default);
    });
  }, []);

  if (!Component) {
    return <LoadingFallback />;
  }

  return <Component />;
};

// Lazy list with progressive loading
export const ProgressiveList: React.FC<{ items: any[] }> = ({ items }) => {
  const [visibleCount, setVisibleCount] = useState(10);

  const loadMore = () => {
    setVisibleCount(prev => Math.min(prev + 10, items.length));
  };

  const visibleItems = items.slice(0, visibleCount);

  return (
    <FlatList
      data={visibleItems}
      renderItem={({ item }) => <ListItem item={item} />}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      ListFooterComponent={
        visibleCount < items.length ? <ActivityIndicator /> : null
      }
    />
  );
};

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholder: {
    backgroundColor: '#e0e0e0',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
