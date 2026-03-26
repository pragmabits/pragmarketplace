# CSS Selectors Quick Reference

## Basic Selectors

| Selector | Example | Specificity |
|----------|---------|-------------|
| Universal | `*` | (0,0,0) |
| Type | `div`, `p`, `h1` | (0,0,1) |
| Class | `.card` | (0,1,0) |
| ID | `#header` | (1,0,0) |
| Attribute | `[type="text"]` | (0,1,0) |

## Combinators

| Combinator | Syntax | Selects |
|-----------|--------|---------|
| Descendant | `A B` | B anywhere inside A |
| Child | `A > B` | B direct child of A |
| Adjacent sibling | `A + B` | B immediately after A |
| General sibling | `A ~ B` | B after A (same parent) |
| Column | `col \|\| td` | Cells in a column |

## Attribute Selectors

| Selector | Matches |
|----------|---------|
| `[attr]` | Has attribute |
| `[attr="val"]` | Exact match |
| `[attr~="val"]` | Word in space-separated list |
| `[attr\|="val"]` | Exact or starts with `val-` |
| `[attr^="val"]` | Starts with |
| `[attr$="val"]` | Ends with |
| `[attr*="val"]` | Contains |
| `[attr="val" i]` | Case-insensitive match |

## Pseudo-Classes

### State

| Pseudo-class | Purpose |
|-------------|---------|
| `:hover` | Mouse over |
| `:active` | Being activated (clicked) |
| `:focus` | Has focus |
| `:focus-visible` | Focus via keyboard (preferred for outlines) |
| `:focus-within` | Contains a focused element |
| `:visited` | Visited link |
| `:target` | Matches URL fragment |
| `:disabled` / `:enabled` | Form element state |
| `:checked` | Checked checkbox/radio |
| `:indeterminate` | Indeterminate checkbox |
| `:valid` / `:invalid` | Form validation state |
| `:required` / `:optional` | Form field requirement |
| `:placeholder-shown` | Placeholder visible |
| `:empty` | No children |

### Structural

| Pseudo-class | Purpose |
|-------------|---------|
| `:first-child` | First child of parent |
| `:last-child` | Last child of parent |
| `:nth-child(n)` | nth child (`2n`, `odd`, `3n+1`) |
| `:nth-last-child(n)` | From the end |
| `:nth-of-type(n)` | nth of same type |
| `:only-child` | No siblings |
| `:only-of-type` | No siblings of same type |
| `:first-of-type` | First of type |
| `:last-of-type` | Last of type |
| `:root` | Document root (`<html>`) |

### Functional

| Pseudo-class | Purpose | Specificity |
|-------------|---------|-------------|
| `:is()` | Matches any argument | Highest in list |
| `:where()` | Same as `:is()` | **Zero** (0,0,0) |
| `:not()` | Negation | Highest in list |
| `:has()` | Parent/relational selector | Highest in list |
| `:nth-child(n of S)` | nth matching selector S | Per arguments |

## Pseudo-Elements

| Pseudo-element | Purpose |
|---------------|---------|
| `::before` | Insert before content |
| `::after` | Insert after content |
| `::first-line` | First line of text |
| `::first-letter` | First letter of text |
| `::placeholder` | Input placeholder text |
| `::marker` | List item marker |
| `::selection` | User-selected text |
| `::backdrop` | Behind fullscreen/dialog |
| `::file-selector-button` | File input button |

## Specificity Calculation

```
Specificity: (ID, CLASS, TYPE)

#nav .item:hover   → (1, 2, 0)
  #nav = 1 ID
  .item = 1 class
  :hover = 1 pseudo-class (counts as class)

div.card > p::before → (0, 1, 3)
  div = 1 type
  .card = 1 class
  p = 1 type
  ::before = 1 pseudo-element (counts as type)
```

### Specificity Rules

1. `!important` > inline styles > ID > class/attribute/pseudo-class > type/pseudo-element > universal
2. `:is()` and `:not()` take the specificity of their **most specific argument**
3. `:where()` always has **zero specificity**
4. `:has()` takes the specificity of its **most specific argument**
5. `@layer` styles lose to unlayered styles regardless of specificity

## Cascade Layers

```css
/* Declare layer order (first = lowest priority) */
@layer reset, base, components, utilities;

/* Add styles to layers */
@layer reset { /* ... */ }
@layer components { /* ... */ }

/* Unlayered styles always beat layered styles */
```

### Layer Priority (lowest → highest)

1. Layered styles (in declared order)
2. Unlayered styles
3. Inline styles
4. `!important` (reverses layer order)

## Browser Support Notes

- `:has()` — Supported in all modern browsers (2023+)
- `:is()` / `:where()` — Widely supported
- `@layer` — Supported in all modern browsers (2022+)
- `:focus-visible` — Widely supported, prefer over `:focus` for outlines
- `::backdrop` — Supported for `<dialog>` and fullscreen API
