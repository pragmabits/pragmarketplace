# Web Fonts vs SVG

Source: https://docs.fontawesome.com/web/dig-deeper/webfont-vs-svg

## Web Fonts + CSS

**Superpowers:** Easiest setup, reliable/established, works in CSS pseudo-elements, unicode references, batched subsets.

**Weakness:** Can't do advanced styling tricks (power transforms, masking, layering).

## SVG + JS

**Superpowers:** Great for JS apps, masking/layering/power transforms, crisp vectors at any size, easier custom subsets.

**Weakness:** No native rendering without JS, can bog down browsers with many icons (fixable with SVG symbols).

## Feature Comparison

| Feature | Web Fonts & CSS | SVG & JS |
|---------|-----------------|----------|
| How Icons Render | CSS pseudo-elements | SVG elements in HTML |
| Best For | People used to older FA; projects where HTML can't be modified | People who prefer SVGs; those wanting Power Transforms |
| Requirements | CSS + browser supporting @font-face | CSS + JavaScript + SVG support |
| Icon Sizing | Supported | Supported |
| Icon Rotating | Supported | Supported |
| Listed/Bordered/Pulled Styling | Supported | Supported |
| Icon Animations | Supported | Supported |
| Stacking Icons | Supported | Supported |
| Power Transforms | **Not supported** | Supported |
| Masking | **Not supported** | Supported |
| Layering Text and Counters | **Not supported** | Supported |
