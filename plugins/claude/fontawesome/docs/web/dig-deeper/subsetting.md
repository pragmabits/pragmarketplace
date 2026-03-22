# Subsetting

Source: https://docs.fontawesome.com/web/dig-deeper/subsetting

Speed up your site by creating a super-lean, super-fast subset of Font Awesome.

> **Note:** This feature requires a Pro Plan.

## Subsetting Options

### 1. Auto-Subsetting (Kits)

Default method for hosted Kits using SVG+JS technology. Automatically loads minimal icons without customization. Slims down the number of icons and serves the ones you're using in your project, site, or app.

Not available for bare SVGs, SVG Sprites, or SVG Unicodes.

### 2. Subset By Style (Kits)

Configure Kit Settings to select only needed styles, reducing overall file weight while maintaining access to all icons within selected styles.

### 3. Custom Subsetting By Icon (Kits)

Enables precise control by selecting exact icons to include.

**Process:**
1. Enable Custom Subsetting in Kit Settings
2. Navigate to the Icons tab and select specific styles
3. Search or browse to find and add individual icons
4. Save selections before deployment

> **Important:** "We don't recommend switching to Custom Subsetting when using a hosted Kit on a production site" without creating a new Kit first to ensure continuous icon availability.

## Self-Hosted Subsetting

Self-hosted implementations can also use "Select Styles" for Web Fonts or SVG+JS approaches — simply include only the CSS/JS files for the styles you need.

## Using Subsetted Kits

Subsetted Kits can be used via:
- Embed code (hosted)
- Download for self-hosting
- Integration with desktop applications

All using the same methods as standard Kits.
