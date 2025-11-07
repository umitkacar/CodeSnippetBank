import React, { memo, useMemo, useCallback } from 'react';

/**
 * Optimized list component with virtualization concepts
 */
interface ListItem {
  id: string;
  title: string;
  description: string;
}

interface OptimizedListProps {
  items: ListItem[];
  onItemClick: (id: string) => void;
}

// Memoized list item component
const ListItemComponent = memo<{
  item: ListItem;
  onClick: (id: string) => void;
}>(({ item, onClick }) => {
  const handleClick = useCallback(() => {
    onClick(item.id);
  }, [item.id, onClick]);

  return (
    <div className="list-item" onClick={handleClick}>
      <h3>{item.title}</h3>
      <p>{item.description}</p>
    </div>
  );
});

ListItemComponent.displayName = 'ListItemComponent';

export const OptimizedList: React.FC<OptimizedListProps> = memo(
  ({ items, onItemClick }) => {
    // Memoize filtered/sorted items if needed
    const processedItems = useMemo(() => {
      // Perform expensive operations here
      return items.filter((item) => item.title.length > 0);
    }, [items]);

    // Memoize callback to prevent re-renders
    const handleItemClick = useCallback(
      (id: string) => {
        onItemClick(id);
      },
      [onItemClick]
    );

    return (
      <div className="optimized-list">
        {processedItems.map((item) => (
          <ListItemComponent
            key={item.id}
            item={item}
            onClick={handleItemClick}
          />
        ))}
      </div>
    );
  }
);

OptimizedList.displayName = 'OptimizedList';
