# Troubleshoot React

Source: https://docs.fontawesome.com/web/use-with/react/troubleshoot

## Upgrading

From v4/v5 to v7: review dedicated upgrade docs.

## React Native

Requires separate component (`@fortawesome/react-native-fontawesome`).

## Tree-Shaking Problems

See dedicated tree-shaking documentation.

## Babel/babel-loader Errors (Mac/Linux)

```bash
brew update && brew upgrade
```

Delete `package.json.lock` and `node_modules`, then reinstall:

```bash
npm install
# or
yarn install
```
