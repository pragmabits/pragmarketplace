# React Native

Source: https://docs.fontawesome.com/web/use-with/react-native

## Install

```bash
npm i @fortawesome/fontawesome-svg-core
npm i @fortawesome/free-solid-svg-icons  # or other icon packages
npm i @fortawesome/react-native-fontawesome@latest
npm i react-native-svg
```

iOS:

```bash
cd ios && pod install
```

## Usage

```javascript
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome'
import { faMugSaucer } from '@fortawesome/free-solid-svg-icons/faMugSaucer'

<FontAwesomeIcon icon={faMugSaucer} />
```

## Library Building

Centralized registration for icons used throughout the app.

## Styling

- `color` prop or StyleSheet for colors
- Default size: 16
- Duotone: `secondaryColor` and `secondaryOpacity` props
- Power transforms and masking supported

## Limitation

Version 7 and Pro+ Icons are not yet available in the React Native package.
