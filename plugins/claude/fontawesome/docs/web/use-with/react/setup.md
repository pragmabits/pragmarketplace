# Set Up with React

Source: https://docs.fontawesome.com/web/use-with/react

Recommended: use official `react-fontawesome` component. Requires React 16.3 or later.

## 1. Add the React Component

```bash
npm i --save @fortawesome/react-fontawesome@latest
# or
yarn add @fortawesome/react-fontawesome@latest
```

## 2. Add SVG Core

```bash
npm i --save @fortawesome/fontawesome-svg-core
# or
yarn add @fortawesome/fontawesome-svg-core
```

## 3. Add Icon Packages

### Using a Kit Package (Recommended)

1. Set up a Kit
2. Enable Package Installation for that Kit
3. Configure access to your Kit's package

```bash
npm install @awesome.me/kit-KIT_CODE@latest
# or
yarn add @awesome.me/kit-KIT_CODE@latest
```

> **TypeScript Note:** If using `@awesome.me/kit-KIT_CODE` and experiencing import errors, configure moduleResolution in your TypeScript config.

### Using SVG Icon Packages (Alternate)

**Free Icon Packages:**

```bash
npm i --save @fortawesome/free-solid-svg-icons
npm i --save @fortawesome/free-regular-svg-icons
npm i --save @fortawesome/free-brands-svg-icons
```

**Pro Icon Packages** (requires active Pro Plan and configured access):

```bash
npm install @fortawesome/pro-solid-svg-icons
npm install @fortawesome/pro-regular-svg-icons
npm install @fortawesome/pro-light-svg-icons
npm install @fortawesome/pro-thin-svg-icons
npm install @fortawesome/pro-duotone-svg-icons
npm install @fortawesome/duotone-regular-svg-icons
npm install @fortawesome/duotone-light-svg-icons
npm install @fortawesome/duotone-thin-svg-icons
npm install @fortawesome/sharp-solid-svg-icons
npm install @fortawesome/sharp-regular-svg-icons
npm install @fortawesome/sharp-light-svg-icons
npm install @fortawesome/sharp-thin-svg-icons
npm install @fortawesome/sharp-duotone-solid-svg-icons
npm install @fortawesome/sharp-duotone-regular-svg-icons
npm install @fortawesome/sharp-duotone-light-svg-icons
npm install @fortawesome/sharp-duotone-thin-svg-icons
```

> Pro+ Icons are available only in Kit Packages alongside a Pro+ Plan.
