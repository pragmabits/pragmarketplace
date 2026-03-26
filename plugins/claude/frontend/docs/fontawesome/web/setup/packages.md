# Using a Package Manager

Source: https://docs.fontawesome.com/web/setup/packages

## Three Primary Package Types

1. **Kit Packages** — Custom subsets with Pro+ icons available
2. **SVG Icon Packages** — Individual style packages for JavaScript-based implementations
3. **All Inclusive Packages** — Complete icon libraries (Free or Pro)

## Kit Packages (Recommended)

"The most efficient and customized way" to access Font Awesome icons through package managers. Contain only icons and styles you've selected, plus custom uploads. Pro+ icons are exclusively available through Kit packages.

```bash
npm install @awesome.me/kit-KIT_CODE@latest
# or
yarn add @awesome.me/kit-KIT_CODE@latest
```

## SVG Icon Packages

JavaScript-based packages that replace standard HTML elements with SVG icons and handle CSS loading automatically. Compatible with Vue.js, React, and other frameworks, with options for different icon styles (Solid, Regular, Light, Thin) and families (Classic, Sharp, Duotone).

### Free Packages

```bash
npm i @fortawesome/fontawesome-free
npm i @fortawesome/free-solid-svg-icons
npm i @fortawesome/free-regular-svg-icons
npm i @fortawesome/free-brands-svg-icons
```

### Pro Packages (requires active Pro Plan)

```bash
npm i @fortawesome/fontawesome-pro
npm i @fortawesome/pro-solid-svg-icons
npm i @fortawesome/pro-regular-svg-icons
npm i @fortawesome/pro-light-svg-icons
npm i @fortawesome/pro-thin-svg-icons
npm i @fortawesome/pro-duotone-svg-icons
npm i @fortawesome/sharp-solid-svg-icons
npm i @fortawesome/sharp-regular-svg-icons
npm i @fortawesome/sharp-light-svg-icons
npm i @fortawesome/sharp-thin-svg-icons
# ... and more
```

## All Inclusive Packages

Bundle everything from the standard Font Awesome download but are "really huge" with potential performance implications. Pro version notably excludes Pro+ icons.

## Configuration Requirements

Pro package access requires `.npmrc` or `.yarnrc.yml` with authentication tokens. Free packages skip this step.

### .npmrc Configuration

```ini
@fortawesome:registry=https://npm.fontawesome.com/
//npm.fontawesome.com/:_authToken=YOUR_TOKEN_HERE
```

### .yarnrc.yml Configuration

```yaml
npmScopes:
  fortawesome:
    npmRegistryServer: "https://npm.fontawesome.com/"
    npmAuthToken: "YOUR_TOKEN_HERE"
```

Environment variables offer a more secure approach than hardcoding tokens.
