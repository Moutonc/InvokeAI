# Cloud Models User Guide

**Quick Start Guide for Using Cloud Image Generation Models in InvokeAI**

---

## Overview

InvokeAI now supports cloud-based image generation alongside your local models! Use powerful APIs from Google (Gemini, Imagen) and OpenAI (DALL-E) directly in your workflows without downloading gigabytes of model files.

### Benefits
- ✨ **No Downloads**: Use models instantly without waiting for multi-GB downloads
- 💰 **Pay-per-Use**: Only pay for images you generate
- 🚀 **Latest Models**: Access cutting-edge models like Gemini 2.5 Flash and Imagen 4 Ultra
- 🔄 **Unified Experience**: Cloud models work just like local models in your workflows

---

## Getting Started

### Step 1: Get API Keys

You'll need at least one API key from a cloud provider.

#### Option A: Google Gemini (Fastest Setup)
1. Visit https://ai.google.dev/
2. Click "Get API key in Google AI Studio"
3. Create a new API key
4. Copy the key (starts with `AIza...`)

**Cost**: $0.039 per image | **Best for**: Fast iterations, natural language prompts

#### Option B: Google Imagen (Premium Quality)
1. Create Google Cloud project: https://console.cloud.google.com/
2. Enable Vertex AI API
3. Set up billing (required)
4. Authenticate locally:
   ```bash
   gcloud auth application-default login
   ```
5. Note your project ID

**Cost**: $0.06 per image | **Best for**: Premium quality, SynthID watermarking

#### Option C: OpenAI DALL-E (Well-Known)
1. Visit https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (starts with `sk-`)
4. Set up billing

**Cost**: $0.04-$0.12 per image | **Best for**: Quality/style controls

---

### Step 2: Configure API Keys

Add your API keys to InvokeAI's environment:

#### Method 1: .env File (Recommended)
1. Open (or create) `.env` file in your InvokeAI directory
2. Add your keys:

```bash
# For Google Gemini
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXX

# For Google Imagen (both required)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# For OpenAI
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX
```

3. Save the file
4. Restart InvokeAI

⚠️ **Important**: Never commit `.env` to git! It's already in `.gitignore`.

#### Method 2: Environment Variables
Set directly in your shell:

```bash
export GOOGLE_API_KEY="AIza..."
export OPENAI_API_KEY="sk-..."
```

---

### Step 3: Register Cloud Models

Now register the models you want to use:

1. **Open InvokeAI** in your browser (usually http://localhost:9090)

2. **Click Settings** (gear icon in top right)

3. **Scroll to "Register Cloud Model"** and expand it

4. **Select a Model** from the dropdown:
   - Gemini 2.5 Flash Image (Fast & affordable)
   - Imagen 4 Ultra (Premium quality)
   - DALL-E 3 (Quality/style controls)
   - DALL-E 2 (Budget option)

5. **Give it a Name** (e.g., "My Gemini Model")

6. **Add Description** (optional, like "For quick iterations")

7. **Click "Register Model"**

8. **Success!** You'll see a green notification

✅ The model is now available in your model list!

---

### Step 4: Use in Workflows

Cloud models work just like local models:

#### Visual Workflow Editor
1. Open **Workflow Editor**
2. Add a text-to-image node:
   - **Gemini Text to Image** (if you registered Gemini)
   - **Imagen Text to Image** (if you registered Imagen)
   - **OpenAI Text to Image** (if you registered OpenAI)
3. **Select your cloud model** from the dropdown
4. Enter your prompt
5. Configure settings (aspect ratio, seed, etc.)
6. **Invoke!**

#### Model List
- Cloud models appear in the **Model Manager**
- Look for the **☁️ cloud icon** next to the name
- Provider badge shows which service (google-gemini, etc.)
- Shows "Cloud" instead of file size

---

## Usage Tips

### Prompting
- **Gemini**: Excels at natural language, descriptive prompts
- **Imagen**: Best for photorealistic scenes, proper nouns
- **DALL-E 3**: Good for creative interpretations, style variations

### Cost Management
- **Preview locally first**: Use local models for iterations, cloud for finals
- **Batch carefully**: Some providers charge per image (DALL-E 3: 1 image only)
- **Monitor usage**: Check your provider dashboard regularly

### Best Practices
1. **Start with Gemini**: It's the cheapest ($0.039/image) and easiest to set up
2. **Use seeds**: Gemini and Imagen support seeds for reproducibility
3. **Save favorites**: Register multiple configurations for different use cases
4. **Local + Cloud**: Use both! Local models for experimentation, cloud for specific needs

---

## Troubleshooting

### "API key not found" Error

**Problem**: InvokeAI can't find your API key

**Solutions**:
1. Check `.env` file has the correct key name:
   - `GOOGLE_API_KEY=...` (not `GEMINI_API_KEY`)
   - `OPENAI_API_KEY=...` (not `OPENAI_KEY`)
2. Restart InvokeAI after adding keys
3. Check for typos in the key

### "Invalid API key" Error

**Problem**: API key doesn't work

**Solutions**:
1. Verify key hasn't been revoked in provider dashboard
2. Check billing is set up (required for most providers)
3. Try creating a new key
4. For Imagen: Run `gcloud auth application-default login` again

### "Model registration failed"

**Problem**: Can't register a model

**Solutions**:
1. Check API key is configured (see above)
2. Make sure you don't already have a model with that name
3. Check InvokeAI logs for specific error
4. Try a different provider first

### Model doesn't appear in workflow

**Problem**: Registered model not showing in dropdown

**Solutions**:
1. Refresh the page (Ctrl+R or Cmd+R)
2. Check Model Manager to verify registration
3. Make sure you're using a cloud-compatible invocation node
4. Check browser console for errors

---

## Comparison: Local vs Cloud

| Feature | Local Models | Cloud Models |
|---------|-------------|--------------|
| **Setup Time** | Hours (download + install) | Minutes (get API key) |
| **Storage** | 2-8 GB per model | 0 GB (API-based) |
| **Cost** | GPU electricity + hardware | $0.02-$0.12 per image |
| **Speed** | 5-30 seconds | 5-15 seconds |
| **Privacy** | 100% private | Sent to provider |
| **Offline** | ✅ Yes | ❌ No (needs internet) |
| **Variety** | Thousands of models | 4 models (currently) |
| **Customization** | Full control | Provider settings only |

---

## Available Cloud Models

### Google Gemini 2.5 Flash Image
- **Best For**: Fast iterations, experimentation
- **Cost**: $0.039 per image ⭐ Cheapest!
- **Aspect Ratios**: 10 options (1:1, 16:9, 9:16, etc.)
- **Max Resolution**: 2048×2048
- **Supports**: Seeds, natural language prompts
- **Setup**: Easiest (just API key)

### Google Imagen 4 Ultra
- **Best For**: Premium quality, photorealism
- **Cost**: $0.06 per image
- **Aspect Ratios**: 5 options
- **Max Resolution**: 2048×2048 (2K)
- **Supports**: Seeds, batch (1-4 images), SynthID watermark
- **Setup**: Requires Google Cloud project

### OpenAI DALL-E 3
- **Best For**: Creative interpretations, style control
- **Cost**: $0.04-$0.12 per image (varies by size/quality)
- **Sizes**: 1024², 1792×1024, 1024×1792
- **Supports**: Quality (standard/HD), style (vivid/natural)
- **Setup**: API key + billing

### OpenAI DALL-E 2
- **Best For**: Budget iterations
- **Cost**: $0.016-$0.020 per image ⭐ Also cheap!
- **Sizes**: 256², 512², 1024²
- **Supports**: Batch generation (up to 10 images)
- **Setup**: Same as DALL-E 3

---

## FAQ

### Can I use cloud models offline?
No, cloud models require an internet connection to access the provider's API.

### Are cloud models as good as local models?
Different use cases! Cloud models (especially Imagen 4 Ultra) produce exceptional quality, but local models offer more variety and customization.

### How much will this cost me?
It depends on usage. Example costs:
- **Light use** (10 images/day): ~$0.40-$0.60/day
- **Medium use** (50 images/day): ~$2-$3/day
- **Heavy use** (200 images/day): ~$8-$12/day

Tip: Start with Gemini ($0.039/image) for the best value.

### Can I delete cloud models?
Yes! Go to Model Manager, select the cloud model, and click delete. Your API keys remain configured.

### Do cloud models support ControlNet, LoRA, etc.?
Not yet. Cloud models are text-to-image only currently. Provider APIs are expanding, so future support is possible.

### Can I use my own fine-tuned models?
Not with these providers. Cloud models only support the models offered by Google/OpenAI APIs.

### Is my data private?
Prompts and generated images are sent to the cloud provider. Check each provider's privacy policy. For complete privacy, use local models.

---

## Next Steps

- **Experiment**: Try different providers to find your favorite
- **Combine**: Use local models for base images, cloud for variations
- **Monitor**: Keep an eye on API usage and costs
- **Share**: Tell the InvokeAI community about your results!

---

## Need Help?

- **Documentation**: `docs/features/CLOUD_MODELS.md`
- **Testing Guide**: `PHASE4_TESTING_GUIDE.md`
- **Issues**: https://github.com/invoke-ai/InvokeAI/issues
- **Discord**: https://discord.gg/ZmtBAhwWhy
- **Discussions**: https://github.com/invoke-ai/InvokeAI/discussions

---

**Happy generating! ✨**
