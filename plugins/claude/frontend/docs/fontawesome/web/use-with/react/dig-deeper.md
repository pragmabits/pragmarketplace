# Dig Deeper with React

Source: https://docs.fontawesome.com/web/use-with/react/dig-deeper

## Unit Testing

Two approaches:

### Import Icons Explicitly in Tests

Import and pass icons directly to components under test.

### Mock FontAwesomeIcon

```javascript
export function FontAwesomeIcon(props) {
  return <i className="fa"></i>
}
```

For create-react-app, place mock at `src/__mocks__/@fortawesome/react-fontawesome.js`.

## Related Documentation

- SVG Core documentation
- JavaScript API documentation
