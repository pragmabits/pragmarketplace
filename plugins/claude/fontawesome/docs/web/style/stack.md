# Stacking Icons

Source: https://docs.fontawesome.com/web/style/stack

Stacking allows you to place multiple icons on top of each other.

## Key Classes

| Class | Purpose |
|-------|---------|
| `fa-stack` | Container element — must be on the parent |
| `fa-stack-1x` | Regular-sized icon in the stack (foreground) |
| `fa-stack-2x` | Twice-sized icon in the stack (background) |
| `fa-inverse` | Sets icon color to white (useful for foreground icon on dark background) |

## How It Works

- The parent `span` (or other element) gets `fa-stack`, which sets it to `position: relative` with `display: inline-block`.
- Child icons are absolutely positioned on top of each other.
- `fa-stack-2x` is the larger background icon.
- `fa-stack-1x` is the smaller foreground icon.
- Size the container with standard sizing classes like `fa-2x` on the `fa-stack` element.

## Basic Structure

```html
<span class="fa-stack fa-2x">
  <i class="fa-solid fa-square fa-stack-2x"></i>
  <i class="fa-solid fa-terminal fa-stack-1x fa-inverse"></i>
</span>
```

## Examples

### Icon on a Circle

```html
<span class="fa-stack fa-2x">
  <i class="fa-solid fa-circle fa-stack-2x"></i>
  <i class="fa-solid fa-flag fa-stack-1x fa-inverse"></i>
</span>
```

### Ban/Prohibition Overlay

```html
<span class="fa-stack fa-2x">
  <i class="fa-solid fa-camera fa-stack-1x"></i>
  <i class="fa-solid fa-ban fa-stack-2x" style="color: tomato;"></i>
</span>
```

### Icon on a Square

```html
<span class="fa-stack fa-2x">
  <i class="fa-solid fa-square fa-stack-2x"></i>
  <i class="fa-solid fa-terminal fa-stack-1x fa-inverse"></i>
</span>
```
