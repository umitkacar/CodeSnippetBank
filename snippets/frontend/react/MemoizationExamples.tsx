import React, { useState, useMemo, useCallback, memo } from 'react';

/**
 * Examples of React.memo, useMemo, and useCallback
 */

// 1. React.memo for component memoization
interface ExpensiveComponentProps {
  data: number[];
  multiplier: number;
}

export const ExpensiveComponent = memo<ExpensiveComponentProps>(
  ({ data, multiplier }) => {
    console.log('ExpensiveComponent rendered');

    const result = data.map((num) => num * multiplier);

    return (
      <div>
        {result.map((num, idx) => (
          <span key={idx}>{num} </span>
        ))}
      </div>
    );
  }
);

ExpensiveComponent.displayName = 'ExpensiveComponent';

// 2. useMemo for expensive calculations
export const UseMemoExample: React.FC = () => {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<number[]>([1, 2, 3, 4, 5]);

  // Without useMemo, this would run on every render
  const expensiveCalculation = useMemo(() => {
    console.log('Calculating expensive value...');
    return items.reduce((acc, item) => acc + item, 0) * 2;
  }, [items]); // Only recalculate when items change

  return (
    <div>
      <p>Expensive result: {expensiveCalculation}</p>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment Count</button>
      <button onClick={() => setItems([...items, items.length + 1])}>
        Add Item
      </button>
    </div>
  );
};

// 3. useCallback for memoizing functions
interface UseCallbackExampleProps {
  onSubmit: (value: string) => void;
}

export const UseCallbackExample: React.FC<UseCallbackExampleProps> = ({
  onSubmit,
}) => {
  const [value, setValue] = useState('');

  // Memoize the handler so child components don't re-render unnecessarily
  const handleSubmit = useCallback(() => {
    onSubmit(value);
  }, [value, onSubmit]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  }, []);

  return (
    <div>
      <input value={value} onChange={handleChange} />
      <MemoizedButton onClick={handleSubmit} />
    </div>
  );
};

// Memoized button that only re-renders when onClick changes
const MemoizedButton = memo<{ onClick: () => void }>(({ onClick }) => {
  console.log('Button rendered');
  return <button onClick={onClick}>Submit</button>;
});

MemoizedButton.displayName = 'MemoizedButton';

// 4. Custom equality function for memo
interface ComplexDataProps {
  data: {
    id: string;
    value: number;
    metadata: Record<string, unknown>;
  };
}

export const ComplexDataComponent = memo<ComplexDataProps>(
  ({ data }) => {
    return (
      <div>
        <p>ID: {data.id}</p>
        <p>Value: {data.value}</p>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison - only re-render if id or value changes
    return (
      prevProps.data.id === nextProps.data.id &&
      prevProps.data.value === nextProps.data.value
    );
  }
);

ComplexDataComponent.displayName = 'ComplexDataComponent';
