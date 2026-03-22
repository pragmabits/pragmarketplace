# Use With Nuxt

Source: https://docs.fontawesome.com/web/use-with/vue/use-with

## Install

```bash
npm i --save @fortawesome/vue-fontawesome@latest-3
```

## Configuration

Create `plugins/fontawesome.js`, set `config.autoAddCss = false` to let Nuxt worry about the CSS. Register FontAwesomeIcon globally, add icons to library. Update `nuxt.config.ts` to include FA stylesheet in CSS array.

## Usage

```html
<font-awesome-icon icon="fa-solid fa-user-secret" />
<font-awesome-icon :icon="['fas', 'user-secret']" />
```
