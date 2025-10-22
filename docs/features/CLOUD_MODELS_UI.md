# Cloud Models - UI Guide

This guide covers the frontend user interface for managing cloud model integration in InvokeAI.

## Overview

The cloud models UI provides:
- **Provider Status Indicators**: Real-time status of cloud provider connections
- **Settings Panel**: Configure cloud provider preferences
- **Cost Estimation**: See estimated costs before generating images
- **Easy Access**: All cloud settings in one place in the Settings Modal

---

## Accessing Cloud Settings

1. Click the **Settings** icon (⚙️) in the top navigation bar
2. Open InvokeAI Settings modal
3. Scroll down to the **Cloud Providers** section

The Cloud Providers panel shows:
- List of all available providers (Google Gemini, Google Imagen, OpenAI)
- Current connection status for each provider
- Quick setup instructions for unconfigured providers

---

## Understanding Provider Status

Each cloud provider can have one of the following statuses:

| Status Badge | Meaning | Action Needed |
|-------------|---------|---------------|
| 🔴 **Not Configured** | No API credentials found | Add API keys to `.env` file |
| 🟡 **Configured** | Credentials exist but not validated | Click "Refresh Provider Status" |
| 🟢 **Connected** | Credentials validated and working | Ready to use! |
| 🟠 **Invalid Credentials** | API key exists but doesn't work | Check and update API keys |
| 🔴 **Error** | Connection error occurred | Check error message and connectivity |

---

## Configuration Options

### Auto-Check Providers on Startup
- **What it does**: Automatically validates provider credentials when InvokeAI starts
- **When to enable**: If you want immediate feedback on provider status
- **When to disable**: If you want faster startup (credentials checked on-demand)

### Show Cost Estimates
- **What it does**: Displays estimated cost before generating images with cloud models
- **When to enable**: To monitor and control cloud generation costs
- **When to disable**: If cost isn't a concern and you want a cleaner UI

---

## Setting Up Cloud Providers

### Step 1: Get API Keys
Follow the setup instructions links shown in the Cloud Providers panel:

**Google Gemini**:
1. Visit https://ai.google.dev/
2. Create an API key
3. Copy the key (starts with `AIza...`)

**Google Imagen (Vertex AI)**:
1. Create a Google Cloud project
2. Enable Vertex AI API
3. Set up authentication (gcloud CLI or service account)
4. Note your project ID and region

**OpenAI**:
1. Visit https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (starts with `sk-proj-` or `sk-`)
4. Ensure billing is set up

### Step 2: Configure .env File
Add your API keys to the `.env` file in the InvokeAI root directory:

```bash
# Google Gemini
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXX

# Google Imagen (Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# OpenAI
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX
```

**Important Security Notes**:
- Never commit `.env` to git (it's gitignored by default)
- API keys are NOT visible in the UI for security
- Only the status (configured/not configured) is shown

### Step 3: Restart InvokeAI
After adding API keys, restart InvokeAI for changes to take effect:

```bash
# Stop InvokeAI (Ctrl+C)
# Start again
invokeai-web
```

### Step 4: Verify Connection
1. Open Settings → Cloud Providers
2. Click **"Refresh Provider Status"**
3. Check that providers show 🟢 **Connected** status

---

## Using Cloud Models in Workflows

### Text-to-Image Generation

Once cloud providers are configured, cloud model nodes appear in the workflow editor:

**Available Nodes**:
- `Gemini 2.5 Flash - Text to Image`
- `Imagen 4 Ultra - Text to Image`
- `OpenAI DALL-E 3 - Text to Image`
- `OpenAI DALL-E 2 - Text to Image`

**Parameters**:
- **Prompt**: Text description of desired image
- **Aspect Ratio** / **Size**: Image dimensions (varies by provider)
- **Seed**: Random seed for reproducibility (Gemini/Imagen only)
- **Quality**: Standard/HD (DALL-E 3 only)
- **Style**: Vivid/Natural (DALL-E 3 only)
- **Number of Images**: Batch generation (DALL-E 2, Imagen only)

### Cost Estimation Display

When **Show Cost Estimates** is enabled:
- Cost estimate appears below generation parameters
- Updates automatically when you change:
  - Number of images
  - Image size
  - Quality settings (DALL-E 3)
- Shows cost in USD per generation

**Example**:
```
💰 Estimated Cost: $0.0400 (1 image)
```

---

## Provider-Specific Features

### Google Gemini 2.5 Flash
- **10 Aspect Ratios**: Square, landscape, portrait, ultrawide, and more
- **Seed Support**: Reproducible generations
- **Fast & Affordable**: $0.039 per image
- **Best For**: Rapid iteration, affordable experimentation

### Google Imagen 4 Ultra
- **Batch Generation**: 1-4 images per request
- **Safety Filters**: 3 configurable levels
- **Prompt Enhancement**: AI-powered prompt improvement
- **SynthID Watermark**: Authenticity tracking
- **Best For**: Premium quality, batch variations

### OpenAI DALL-E 3
- **Quality Control**: Standard or HD output
- **Style Selection**: Vivid (dramatic) or Natural (realistic)
- **Revised Prompts**: GPT-4 enhances your prompts automatically
- **Metadata**: See how GPT-4 interpreted your prompt
- **Best For**: High-quality, controlled generations

### OpenAI DALL-E 2
- **Batch Generation**: Up to 10 images at once
- **3 Sizes**: 256×256, 512×512, 1024×1024
- **Most Affordable**: $0.016-$0.020 per image
- **Best For**: Quick exploration, bulk generation

---

## Troubleshooting

### Provider Shows "Not Configured"
**Solution**:
1. Check that API key is added to `.env` file
2. Verify no typos in key or environment variable name
3. Restart InvokeAI after adding keys
4. Check `.env` is in the correct location (InvokeAI root directory)

### Provider Shows "Invalid Credentials"
**Solution**:
1. Verify API key is correct and active
2. Check key hasn't been revoked or restricted
3. For Imagen: Ensure Vertex AI API is enabled
4. For OpenAI: Verify billing is set up
5. Try creating a new API key

### Provider Shows "Error"
**Solution**:
1. Check internet connectivity
2. Verify no firewall blocking API requests
3. For Imagen: Check Google Cloud authentication
4. Look at error message for specific details
5. Try "Refresh Provider Status" after a few minutes

### Cost Estimate Not Showing
**Solution**:
1. Open Settings → Cloud Providers
2. Enable **"Show Cost Estimates"**
3. Verify provider is connected
4. Refresh the page if needed

### Cloud Nodes Not Appearing in Workflow Editor
**Solution**:
1. Verify backend API is running
2. Check browser console for errors
3. Refresh the page (Ctrl+R / Cmd+R)
4. Verify cloud providers are configured

---

## Best Practices

### Security
- **Never share API keys** publicly or commit to version control
- **Use separate keys** for development and production
- **Rotate keys regularly** for enhanced security
- **Monitor usage** through provider dashboards

### Cost Management
- **Enable cost estimates** to stay informed
- **Use cheaper models** (Gemini, DALL-E 2) for iteration
- **Use premium models** (Imagen, DALL-E 3 HD) for final outputs
- **Set billing alerts** in provider dashboards
- **Review usage monthly** to track spending

### Workflow Efficiency
- **Check provider status** before starting large batches
- **Use batch generation** (Imagen, DALL-E 2) when exploring variations
- **Enable auto-check on startup** for immediate status feedback
- **Combine with local models** for hybrid workflows

### Quality Optimization
- **Use seed parameter** (Gemini/Imagen) for reproducible results
- **Try prompt enhancement** (Imagen) for better quality
- **Use HD quality** (DALL-E 3) for final deliverables
- **Review revised prompts** (DALL-E 3) to learn prompt techniques

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Settings | `Cmd/Ctrl + ,` |
| Close Modal | `Esc` |
| Refresh Status | Click button in Cloud Providers panel |

---

## Architecture Notes (For Developers)

### Frontend Components
- **CloudProviderSettingsPanel**: Main settings accordion
- **ProviderStatusIndicator**: Colored status badges
- **CostEstimationDisplay**: Real-time cost calculator

### State Management
- **Redux Slice**: `features/cloudIntegration/store/cloudSlice.ts`
- **API Endpoints**: `services/api/endpoints/cloudModels.ts`
- **Persistence**: Settings saved to browser local storage

### API Endpoints
- `GET /api/v2/cloud/providers` - List all providers with status
- `GET /api/v2/cloud/providers/{provider}/status` - Get specific provider status
- `GET /api/v2/cloud/models` - List available cloud models
- `POST /api/v2/cloud/estimate_cost` - Calculate generation cost

### Security Design
- API keys stored only in `.env` (server-side)
- Frontend only knows if key is "configured" or "not configured"
- No key values transmitted to frontend
- Status checks validate credentials without exposing them

---

## FAQ

**Q: Can I use multiple cloud providers at the same time?**
A: Yes! Configure all desired providers and use them in different workflow nodes.

**Q: Are API keys stored securely?**
A: Yes. Keys are only stored in the `.env` file on your server. The UI never sees the actual key values.

**Q: Why is my provider status "Configured" instead of "Connected"?**
A: Click "Refresh Provider Status" to validate credentials. Auto-check on startup can also be enabled.

**Q: Can I change API keys without restarting?**
A: No, InvokeAI must be restarted to pick up new `.env` values.

**Q: Do cost estimates include all fees?**
A: Estimates are based on official provider pricing but may not include taxes or regional variations. Always check your provider dashboard for actual billing.

**Q: Can I disable cloud models if I only want local models?**
A: Yes, simply don't configure any API keys and cloud nodes won't be functional.

**Q: How do I know which model to use?**
A: See the provider comparison in the main [CLOUD_MODELS.md](./CLOUD_MODELS.md) documentation.

---

## Additional Resources

- **Main Documentation**: [CLOUD_MODELS.md](./CLOUD_MODELS.md)
- **Provider Documentation**:
  - [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs/image-generation)
  - [Google Imagen (Vertex AI) Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)
  - [OpenAI DALL-E Docs](https://platform.openai.com/docs/guides/images)
- **InvokeAI Community**: https://discord.gg/ZmtBAhwWhy
- **Report Issues**: https://github.com/invoke-ai/InvokeAI/issues

---

**Last Updated**: 2025-10-22
**Version**: Phase 4 - Frontend Integration Complete
