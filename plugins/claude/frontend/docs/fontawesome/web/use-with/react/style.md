# Style Icons in React

Source: https://docs.fontawesome.com/web/use-with/react/style

All Font Awesome styling tools are available with React-specific syntax.

## Size

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" size="xs" />
<FontAwesomeIcon icon="fa-solid fa-coffee" size="6x" />
```

## Automatic Width

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" widthAuto />
```

## List Items

```jsx
<ul className="fa-ul">
  <li><FontAwesomeIcon icon="fa-solid fa-check" listItem /> Item</li>
</ul>
```

## Rotate and Flip

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" rotation={90} />
<FontAwesomeIcon icon="fa-solid fa-coffee" flip="horizontal" />
```

### Custom Rotation

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" rotateBy style={{ '--fa-rotate-angle': '329deg' }} />
```

## Animate

Props: `beat`, `beatFade`, `bounce`, `fade`, `flip`, `shake`, `spin`, `spinReverse`, `spinPulse`.

```jsx
<FontAwesomeIcon icon="fa-solid fa-heart" beat />
<FontAwesomeIcon icon="fa-solid fa-spinner" spin />
```

## Border and Pull

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" border />
<FontAwesomeIcon icon="fa-solid fa-coffee" pull="left" />
```

## Power Transforms

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" transform="shrink-6 left-4" />
<FontAwesomeIcon icon="fa-solid fa-coffee" transform={{ rotate: 42 }} />
```

## Mask

```jsx
<FontAwesomeIcon icon="fa-solid fa-coffee" transform="shrink-7" mask="fa-solid fa-circle" />
```

## Duotone, Symbols, Layers, Inverse, Custom Classes

All supported with React props.
