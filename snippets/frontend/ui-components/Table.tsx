import React, { ReactNode } from 'react';

interface TableProps {
  children: ReactNode;
}

export const Table = ({ children }: TableProps) => (
  <div className="w-full overflow-auto">
    <table className="w-full caption-bottom text-sm">{children}</table>
  </div>
);

export const TableHeader = ({ children }: TableProps) => (
  <thead className="border-b">{children}</thead>
);

export const TableBody = ({ children }: TableProps) => (
  <tbody className="divide-y">{children}</tbody>
);

export const TableRow = ({ children }: TableProps) => (
  <tr className="hover:bg-gray-50">{children}</tr>
);

export const TableHead = ({ children }: TableProps) => (
  <th className="h-12 px-4 text-left align-middle font-medium">{children}</th>
);

export const TableCell = ({ children }: TableProps) => (
  <td className="p-4 align-middle">{children}</td>
);
