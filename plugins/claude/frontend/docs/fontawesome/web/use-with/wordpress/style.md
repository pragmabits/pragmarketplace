# Style Icons with WordPress

Source: https://docs.fontawesome.com/web/use-with/wordpress/style

The Font Awesome WordPress plugin provides interactive styling tools to customize icons directly within the editor.

## Opening Styling Tools

Click the styling option in the format bar for your element. Block elements use a paintbrush icon, while inline icons require selecting the Style button after clicking the icon itself.

## Available Styling Options

The styling interface displays a preview pane alongside customization controls:

- **Colors**: Select from theme colors or custom options; use "No Color" to reset
- **Rotation**: Customize icon orientation
- **Size**: Adjust icon dimensions
- **Animation**: Add motion effects through a dedicated Animation tab

Changes appear in real-time on the preview.

## Alternative Styling Methods

For shortcodes or HTML elements, styling attributes can be added directly:

```
[icon name="yin-yang" prefix="fas" class="fa-2x fa-spin"]
```

```html
<i class="fa-yin-yang fa-solid fa-2x fa-spin"></i>
```

### Supported Attributes

| Attribute | Purpose |
|-----------|---------|
| `class` | Font Awesome or custom CSS classes |
| `style` | Custom CSS styling |
| `title` | Accessibility title |
| `aria-hidden` | Accessibility helper |
| `aria-labelledby` | Accessibility helper |
| `role` | Accessibility role |
| `name` | Icon identification |
| `prefix` | Icon style/family identification |

This approach enables access to Font Awesome's full CSS styling library, including sizing, rotation, animation, and accessibility features.
