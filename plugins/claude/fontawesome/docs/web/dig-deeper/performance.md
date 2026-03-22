# Performance

Source: https://docs.fontawesome.com/web/dig-deeper/performance

Implementation choices significantly impact site performance. Different projects have unique requirements.

## Create a Subset

- **Kit Custom Subsetting:** Select specific styles or individual icons from each style in Kit Settings.
- **Hosting Options:** Font Awesome can host the subsetted Kit, or users can download and self-host.
- **Self-Hosting Style Limitation:** Reduce loading by including only necessary style files (Web Fonts or SVG+JS approach).

## Load Only One Version

Remove older FA versions running alongside v7, especially in ecosystems where plugins/themes might load multiple versions.

## Performance with SVG with JavaScript

- Converts `<i>` tags to SVG elements using batched mutations
- **Best for:** Smaller icon quantities, JavaScript subsetting capability, resource-capable browsers

## Performance with Web Fonts with CSS

- Original, battle-tested approach
- **Best for:** Established web font technology preference, large icon quantities, resource-limited browsers

## Performance with SVG Sprites

- Consolidates all icons into single sprite file with CSS-based display
- **Best for:** Smaller icon sets, JavaScript-free environments, custom CSS styling, resource-limited user agents

## Performance with Individual SVG Icons

- Most basic integration method without styling assistance
- **Best for:** Efficient individual file requests or embedded SVGs, JavaScript-free requirements, custom CSS styling
