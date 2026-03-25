# Data Table Pattern

## Overview

Build custom data tables using TanStack Table and shadcn/ui's `<Table />` component. This is a headless UI approach — you build the table to your exact needs.

## Installation

```bash
pnpm dlx shadcn@latest add table
pnpm add @tanstack/react-table
```

## Project Structure

```
app/payments/
├── columns.tsx      # Column definitions
├── data-table.tsx   # DataTable component
└── page.tsx         # Server component for data fetching
```

## Column Definitions

```typescript
"use client"

import { ColumnDef } from "@tanstack/react-table"

export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [
  { accessorKey: "status", header: "Status" },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "amount", header: "Amount" },
]
```

## DataTable Component

```typescript
"use client"

import {
  ColumnDef, flexRender, getCoreRowModel, useReactTable,
} from "@tanstack/react-table"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns, data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data, columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="overflow-hidden rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

## Features

### Sorting

```typescript
import { SortingState, getSortedRowModel } from "@tanstack/react-table"

const [sorting, setSorting] = React.useState<SortingState>([])

const table = useReactTable({
  data, columns,
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
  state: { sorting },
})
```

### Filtering

```typescript
import { ColumnFiltersState, getFilteredRowModel } from "@tanstack/react-table"

const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

const table = useReactTable({
  data, columns,
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  state: { columnFilters },
})
```

### Pagination

```typescript
import { getPaginationRowModel } from "@tanstack/react-table"

const table = useReactTable({
  data, columns,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

### Row Selection

```typescript
{
  id: "select",
  header: ({ table }) => (
    <Checkbox
      checked={table.getIsAllPageRowsSelected()}
      onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
      aria-label="Select all"
    />
  ),
  cell: ({ row }) => (
    <Checkbox
      checked={row.getIsSelected()}
      onCheckedChange={(value) => row.toggleSelected(!!value)}
      aria-label="Select row"
    />
  ),
}
```

### Column Visibility

```typescript
import { VisibilityState } from "@tanstack/react-table"

const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})

const table = useReactTable({
  data, columns,
  onColumnVisibilityChange: setColumnVisibility,
  state: { columnVisibility },
})
```

### Cell Formatting

```typescript
{
  accessorKey: "amount",
  header: () => <div className="text-right">Amount</div>,
  cell: ({ row }) => {
    const amount = parseFloat(row.getValue("amount"))
    const formatted = new Intl.NumberFormat("en-US", {
      style: "currency", currency: "USD",
    }).format(amount)
    return <div className="text-right font-medium">{formatted}</div>
  },
}
```

### Row Actions

```typescript
{
  id: "actions",
  cell: ({ row }) => {
    const payment = row.original
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Actions</DropdownMenuLabel>
          <DropdownMenuItem onClick={() => navigator.clipboard.writeText(payment.id)}>
            Copy payment ID
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>View customer</DropdownMenuItem>
          <DropdownMenuItem>View payment details</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  },
}
```
