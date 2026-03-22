# Add Icons with WordPress

Source: https://docs.fontawesome.com/web/use-with/wordpress/add-icons

Once you've set up your plugin, you're ready to add icons to your pages and posts. The plugin has full support for adding icons as a block element or inline with text.

## Add an Icon

### Icon as a Block Element

Open up the page or post where you want to add the icon, and add a new block element. Search for "icon" and select "Font Awesome Icon". Click the "Choose Icon" button to open the Icon Chooser.

### Inline Icon with Text

Place your cursor in the text element where you would like to add an icon, and select the Font Awesome icon item from the in-context menu. (Note: Inline icons require at least WP 6.3.)

## Find Icons Using the Icon Chooser

Search for icons by **icon name, category, or keyword** and select from a variety of styles.

> **Important:** Use a Pro Kit to add Pro icons using the Icon Chooser. If your plugin is set to use the CDN, you can still search and add Free icons, but you won't be able to find and add Pro/Pro+ icons via the CDN.

## A Note About Updating Icons

### Icons Don't Auto Update with the Block Editor

Icons added with the Block Editor and Icon Chooser are inserted as embedded SVGs — they do not automatically update when new versions of Font Awesome are released.

To get a newer icon design, manually re-add the updated icon using the Icon Chooser.

### But if you're not using the block editor, icons _will_ update automatically

If you're using `<i>` tags or `[icon]` shortcodes to add icons with a Kit set to use the latest version, they will update automatically.

## Other Ways to Add Icons

### Shortcodes

```
[icon name="coffee" prefix="fa-solid"]
```

If you don't include any prefix, the style will default to Solid. Note that you don't need to include the `fa-` part of the name.

### HTML

```html
<i class="fa-solid fa-coffee"></i>
```

### Using Pseudo-elements

CSS pseudo-elements add icons before or after content without editing HTML. Some plugins/themes rely on pseudo-elements — disabling them may cause missing icons.

> **Performance Warning:** Avoid using SVG with pseudo-elements if possible. For performance reasons, the SVG-with-pseudo-elements option is not available when using a Kit. With CDN, enabling it can cause your site to be very slow.

Pseudo-elements are enabled by default with Web Font (both Kits and CDN) since they don't impact performance.

You can get the best of both worlds by using a Web Font Kit to enable pseudo-elements, while using the Icon Chooser in the block editor to add inline SVG icons.
