import React from 'react';
import { GenericListProps } from '../../types/components';

/**
 * Generic List Component.
 * Demonstrates TypeScript Generics <T> in React components.
 * Renders any type of data array safely with custom item renderers and key extractors.
 */
export function GenericList<T>({
  items,
  renderItem,
  keyExtractor,
  emptyMessage = 'No items found',
  className = '',
  listClassName = '',
}: GenericListProps<T>): React.ReactElement {
  if (!items || items.length === 0) {
    return (
      <div
        data-testid="generic-list-empty"
        className={`text-center py-8 px-4 bg-slate-50 border border-dashed border-slate-200 rounded-lg text-slate-500 text-sm ${className}`}
      >
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <ul className={`divide-y divide-slate-100 ${listClassName}`} role="list">
        {items.map((item, index) => (
          <li key={keyExtractor(item, index)} className="transition-colors">
            {renderItem(item, index)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default GenericList;
