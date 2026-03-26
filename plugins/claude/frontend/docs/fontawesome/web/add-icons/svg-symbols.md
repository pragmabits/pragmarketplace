# SVG Symbols

Source: https://docs.fontawesome.com/web/add-icons/svg-symbols

Use the SVG + JS method to get icon sprites that make repeated icons more performant on your page.

## Before You Get Started

- Plan to use the SVG+JS method of Font Awesome
- Are using a lot of the same icon or icons on a single page
- Have your project set up with Font Awesome

Testing shows that for the typical number of icons most people use on a site, the loading and rendering time for the SVG+JS method is faster than Web Fonts.

## A Case for SVG Symbols

When there are many of the same icon repeated on the page, you get a big performance boost by loading each only once.

Define icons as symbols using `data-fa-symbol`, then reference them with `<svg><use href="#name">`:

```html
<!-- Define the icon symbols, these are invisible on the page -->
<i data-fa-symbol="edit" class="fa-solid fa-pencil fa-fw" title="Edit"></i>
<i data-fa-symbol="delete" class="fa-solid fa-trash fa-fw" title="Delete"></i>
<i data-fa-symbol="favorite" class="fa-solid fa-star fa-fw" title="Favorite"></i>

<!-- Use the defined symbols -->
<svg><use href="#edit"></use></svg>
<svg><use href="#delete"></use></svg>
<svg><use href="#favorite"></use></svg>
```

## Accessibility

When using icons without accompanying text, add an `aria-label` to explain their purpose to assistive technology.

## Make Sure to Add Some CSS

SVG sprites require extra styling. When using symbols you must handle this yourself:

```html
<style>
  .icon {
    width: 1em;
    height: 1em;
  }
</style>

<!-- Name symbols with the value of data-fa-symbol -->
<i data-fa-symbol="picture-taker" class="fas fa-camera"></i>

<!-- Use the defined name -->
<svg class="icon"><use href="#picture-taker"></use></svg> Say Cheese!
```

## Related Topics

- Performance optimization
- Web Fonts vs. SVG comparison
