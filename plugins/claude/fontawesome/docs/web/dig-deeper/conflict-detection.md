# Conflict Detection

Source: https://docs.fontawesome.com/web/dig-deeper/conflict-detection

The Conflict Detection tool identifies multiple versions of Font Awesome loaded on the same webpage that could cause unpredictable behavior.

> **Temporary Use Only**: The tool is designed for diagnostic purposes. Disable it after identifying issues, as it performs extra background work that may impact performance.

> **Security Note**: This tool may trigger some security scanning tools due to its unconventional methods.

## Enabling Conflict Detection

### Via Font Awesome Kit

Access your Kit's settings page and enable the Conflict Detection feature.

### Manual Implementation

Add this embed code before the closing `</body>` tag:

```html
<script src="https://kit.fontawesome.com/YOUR_KIT_CODE/fontawesome/v7.0.1/js/conflict-detection.js"></script>
```

Supported versions: v5.10.0 and later.

## Viewing Results

Open your browser's developer console and reload the page. Results display conflicting elements with details including source URLs and inline CSS excerpts.

## Resolution Methods

- **Static HTML**: Search for and remove conflicting tags using provided checksums
- **Web Frameworks**: Remove conflicting tags from page templates
- **WordPress**: Enable the "Remove unregistered clients" feature in the Font Awesome plugin
- **Advanced**: Use the `md5ForNode` function on `window.FontAwesomeDetection` object for programmatic removal

Always remove the conflict detector after use to avoid production performance degradation.
