# Bordered & Pulled Icons

Source: https://docs.fontawesome.com/web/style/pull

Pull classes float icons left or right within text content, similar to CSS `float`. Commonly used for blockquote-style layouts.

## Pull Classes

| Class | Effect |
|-------|--------|
| `fa-pull-left` | Floats the icon to the left with appropriate margin |
| `fa-pull-right` | Floats the icon to the right with appropriate margin |

## Border Class

| Class | Effect |
|-------|--------|
| `fa-border` | Adds a border around the icon |

## Blockquote Pattern

Typically used with `fa-border` for a blockquote effect:

```html
<i class="fa-solid fa-quote-left fa-2x fa-pull-left fa-border"></i>
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.
Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor.
```

The icon floats to the left with a border, and text wraps around it.
