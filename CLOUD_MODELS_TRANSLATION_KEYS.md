# Cloud Models Translation Keys

Translation keys required for cloud model integration frontend UI.

## Settings Modal Keys

### CloudProviderSettingsPanel
```json
{
  "settings": {
    "cloudProviders": "Cloud Providers",
    "autoCheckProvidersOnStartup": "Check provider status on startup",
    "showCostEstimates": "Show cost estimates",
    "refreshProviderStatus": "Refresh Provider Status",
    "providerStatus": "Provider Status",
    "setupInstructions": "Setup Instructions",
    "cloudProvidersHelpText": "Configure API keys for cloud image generation providers to use their models in your workflows.",
    "cloudProvidersConfigNote": "Note: API keys are stored as environment variables. Set them in your .env file."
  }
}
```

### CloudModelRegistrationPanel
```json
{
  "settings": {
    "registerCloudModel": "Register Cloud Model"
  },
  "cloudModels": {
    "selectModel": "Select Model",
    "chooseModel": "Choose a cloud model...",
    "modelName": "Model Name",
    "modelNamePlaceholder": "e.g., My Gemini Model",
    "modelNameHelp": "Give this model a custom name for your workflow",
    "description": "Description (Optional)",
    "descriptionPlaceholder": "Notes about this model...",
    "descriptionHelp": "Add any notes about how you plan to use this model",
    "providerInfo": "Provider Information",
    "provider": "Provider",
    "modelId": "Model ID",
    "registerModel": "Register Model",
    "registering": "Registering...",
    "nameRequired": "Please enter a name for the model",
    "registrationSuccess": "Model Registered Successfully",
    "registrationFailed": "Registration Failed",
    "modelRegisteredMessage": "{{name}} is now available in your workflows",
    "registrationHelpText": "Select a cloud model above to register it for use in InvokeAI. You'll need the appropriate API keys configured."
  }
}
```

## Model List Keys
```json
{
  "modelManager": {
    "cloudModel": "Cloud Model"
  }
}
```

## Usage

Add these keys to the appropriate translation files:
- `invokeai/frontend/web/public/locales/en/translation.json`
- Other language files as needed

## Provider Display Names

Already defined in `features/cloudIntegration/types/index.ts`:
- **Google Gemini 2.5 Flash**: "Fast and affordable with 10 aspect ratios"
- **Google Imagen 4 Ultra**: "Premium quality with SynthID watermark"
- **OpenAI DALL-E**: "DALL-E 3 with quality/style controls"

## Example Usage in Code

```typescript
// In CloudModelRegistrationPanel.tsx
toast({
  title: t('cloudModels.registrationSuccess'),
  description: t('cloudModels.modelRegisteredMessage', { name: customName }),
  status: 'success',
});
```

## Status

Translation keys are documented but not yet added to translation files.

**Next Steps:**
1. Add keys to `public/locales/en/translation.json`
2. Verify all keys are properly referenced in components
3. Test UI with translations
4. Add translations for other languages (optional)
