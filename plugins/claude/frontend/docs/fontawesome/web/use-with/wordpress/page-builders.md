# Using Page Builders

Source: https://docs.fontawesome.com/web/use-with/wordpress/page-builders

The Font Awesome WordPress plugin works primarily with the block editor but also supports `<i>` tags and `[icon]` shortcodes across page builders.

## Builder Independence

Each page builder (Elementor, Divi, Beaver Builder, etc.) integrates Font Awesome differently. Support for Pro icons depends entirely on how individual builders implement Font Awesome functionality — it's not controlled by Font Awesome itself.

## Pro Icon Access

Whether you can use Pro icons in a specific builder depends on that builder's developers. Font Awesome provides infrastructure like GraphQL APIs and CDNs to enable Pro support, but builders must choose to implement these tools.

## Workaround for Limited Builder Support

If your builder lacks Pro icon support, you may still use them by:

- Adding custom HTML with `<i>` tags or `[icon]` shortcodes
- Ensuring your Kit loads correctly on the site
- Accepting that icons may appear as code in the editor but render properly on the front end

## Icon Chooser Limitations

Some builders display outdated icon lists in their icon pickers. Even if the picker doesn't show newer or Pro icons, they'll still work if your Kit loads correctly — try the custom code approach above.
