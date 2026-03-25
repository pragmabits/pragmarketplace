---
name: vue-forms
description: "This skill should be used when the user asks about form validation in Vue with vee-validate, zod, or @vee-validate/zod. Trigger phrases include \"vee-validate\", \"useForm\", \"useField\", \"form validation\", \"zod schema\", \"z.object\", \"z.string\", \"@vee-validate/zod\", \"toTypedSchema\", \"form errors\", \"handleSubmit\", \"schema validation\"."
---

# vee-validate + Zod Form Validation

This skill delegates to the `vuejs` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for vee-validate v4, @vee-validate/zod, and zod.

## Why this skill matters

vee-validate v4 is a complete rewrite using the Composition API — the v3 component-based approach (`<Field>`, `<Form>`) is legacy. The `toTypedSchema()` bridge from `@vee-validate/zod` enables sharing zod schemas between frontend validation and API contracts. Without consulting documentation, answers may use v3 patterns, miss `toTypedSchema`, or implement manual validation instead of leveraging the composable API.

## When to use this skill

Use for ANY request involving:

- Form validation with vee-validate
- Zod schema definitions for form data
- `useForm()` and `useField()` composables
- `toTypedSchema()` bridge between zod and vee-validate
- `handleSubmit` with typed values
- Field-level and form-level error handling
- Cross-field validation with zod refinements
- Dynamic forms with validation

## Common patterns

### Zod schema definition

```typescript
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginForm = z.infer<typeof loginSchema>
```

### useForm with toTypedSchema

```vue
<script setup lang="ts">
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

const schema = toTypedSchema(
  z.object({
    email: z.string().email('Invalid email'),
    password: z.string().min(8, 'Min 8 characters'),
  })
)

const { handleSubmit, errors, defineField } = useForm({
  validationSchema: schema,
})

const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const onSubmit = handleSubmit((values) => {
  // values is typed as { email: string; password: string }
  console.log(values)
})
</script>

<template>
  <form @submit="onSubmit">
    <input v-model="email" v-bind="emailAttrs" />
    <span v-if="errors.email">{{ errors.email }}</span>

    <input v-model="password" v-bind="passwordAttrs" type="password" />
    <span v-if="errors.password">{{ errors.password }}</span>

    <button type="submit">Login</button>
  </form>
</template>
```

### useField for individual field binding

```typescript
import { useField } from 'vee-validate'

const { value, errorMessage, handleBlur } = useField<string>('email')
```

### handleSubmit with error handling

```typescript
const onSubmit = handleSubmit(
  (values) => {
    // Success — values is fully typed
    api.login(values)
  },
  (errors) => {
    // Validation failed — errors contains all field errors
    console.log('Validation errors:', errors)
  }
)
```

### Error display template pattern

```vue
<template>
  <div class="field">
    <label :for="name">{{ label }}</label>
    <input :id="name" v-model="value" v-bind="attrs" />
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>
```

### Zod refinements for cross-field validation

```typescript
const registerSchema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
```

## How to use

Invoke the `/vuejs` command, passing the user's question or task as the argument:

```
/vuejs <user's question or task>
```

The agent will:
1. Check the user's project context (package.json for vee-validate version)
2. Look up current vee-validate v4 and zod documentation
3. Answer with Composition API patterns (not v3 component-based)
4. Flag common pitfalls (v3 vs v4 patterns, missing toTypedSchema)

Form validation questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
