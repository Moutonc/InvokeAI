# Cloud Model Integration - Deployment Plan

This guide walks you through merging your cloud model integration into your fork's main branch and testing it locally.

## Overview

**What We'll Do**:
1. Create a Pull Request to merge changes into your fork's main branch
2. Merge the PR (after review if desired)
3. Set up InvokeAI to run locally
4. Configure cloud provider API keys
5. Test the new cloud model functionality

**Your Repository**: `Moutonc/InvokeAI` (your fork)
**Feature Branch**: `claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk`
**Target Branch**: `main`
**Commits to Merge**: 4 feature commits (Phases 1-4)

---

## PART 1: Create and Merge Pull Request

### Step 1: Create Pull Request via GitHub Web Interface

**Option A: Using GitHub Web Interface (Recommended)**

1. **Navigate to your fork**:
   - Go to: `https://github.com/Moutonc/InvokeAI`

2. **Start PR creation**:
   - You should see a yellow banner saying "claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk had recent pushes"
   - Click **"Compare & pull request"** button

   OR

   - Click "Pull requests" tab
   - Click "New pull request" button
   - Set base: `main`
   - Set compare: `claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk`

3. **Fill in PR details**:

   **Title**:
   ```
   feat: Add Cloud Model Integration (Google Gemini, Imagen, OpenAI DALL-E)
   ```

   **Description** (copy/paste this):
   ```markdown
   ## Summary

   Adds complete cloud model integration to InvokeAI with support for Google Gemini 2.5 Flash, Google Imagen 4 Ultra, and OpenAI DALL-E 3/2.

   ## Features Added

   ### Backend (Python)
   - ✅ Cloud provider infrastructure with abstract base class
   - ✅ Google Gemini 2.5 Flash provider ($0.039/image, 10 aspect ratios, seed support)
   - ✅ Google Imagen 4 Ultra provider ($0.06/image, batch generation, safety filters)
   - ✅ OpenAI DALL-E 3 provider (quality/style controls, revised prompts)
   - ✅ OpenAI DALL-E 2 provider (batch up to 10 images, budget-friendly)
   - ✅ 4 invocation nodes for workflow integration
   - ✅ REST API endpoints for provider management
   - ✅ Secure .env-based API key management

   ### Frontend (React/TypeScript)
   - ✅ Cloud Provider Settings Panel in Settings Modal
   - ✅ Real-time provider status indicators (connected/error/not configured)
   - ✅ Cost estimation display for cloud generations
   - ✅ Redux state management with RTK Query
   - ✅ Complete i18n translations

   ### Documentation
   - ✅ Backend integration guide (CLOUD_MODELS.md)
   - ✅ Frontend UI guide (CLOUD_MODELS_UI.md)
   - ✅ Integration test scripts for all providers
   - ✅ .env configuration examples

   ## Commits Included

   1. Phase 1: Google Gemini 2.5 Flash integration
   2. Phase 2: Google Imagen 4 Ultra integration
   3. Phase 3: OpenAI DALL-E 3 and DALL-E 2 integration
   4. Phase 4: Frontend UI integration

   ## Testing

   - ✅ Integration test scripts created for all providers
   - ✅ Backend API endpoints tested
   - ✅ Frontend components follow InvokeAI patterns
   - ⏳ End-to-end testing pending (will test after merge)

   ## Security

   - API keys stored only in .env file (never in database)
   - No credentials exposed through API
   - Frontend only sees status (configured/not_configured)
   - Following OWASP best practices

   ## Breaking Changes

   None - fully backward compatible.

   ## Files Changed

   - **New Files**: 30+ (providers, nodes, UI components, docs)
   - **Modified Files**: 5 (API routing, store, settings)
   - **Total Lines**: ~3,500+ added

   ## Next Steps After Merge

   1. Set up .env with provider API keys
   2. Install dependencies (httpx, google-auth, python-dotenv)
   3. Test with integration scripts
   4. Use cloud nodes in workflows
   ```

4. **Set PR options**:
   - Base repository: `Moutonc/InvokeAI`
   - Base branch: `main`
   - Head branch: `claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk`
   - Check: "Allow edits by maintainers" (optional, you're the maintainer)

5. **Create the PR**:
   - Click **"Create pull request"** button

---

### Step 2: Review the PR (Optional but Recommended)

1. **Review the "Files changed" tab**:
   - Check the 4 commits are included
   - Verify new files look correct
   - Ensure no sensitive data (API keys) accidentally committed

2. **Review the "Commits" tab**:
   - Confirm all 4 phase commits are there
   - Check commit messages are clear

3. **Check for conflicts**:
   - GitHub will show if there are merge conflicts
   - Should say "✓ This branch has no conflicts with the base branch"

---

### Step 3: Merge the Pull Request

**Option A: Merge via GitHub UI (Recommended)**

1. On the PR page, scroll down to the merge section
2. Choose merge strategy:
   - **"Create a merge commit"** ← RECOMMENDED (preserves all commit history)
   - "Squash and merge" (combines into 1 commit - loses phase separation)
   - "Rebase and merge" (rewrites history - generally not needed)

3. Click **"Merge pull request"** button
4. Confirm by clicking **"Confirm merge"**
5. Optionally delete the feature branch after merge

**Option B: Merge via Command Line**

If you prefer command line:

```bash
cd /home/user/InvokeAI

# Switch to main branch
git checkout main

# Merge the feature branch
git merge claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# Push to your fork
git push origin main
```

---

### Step 4: Verify Merge

1. **Check GitHub**:
   - Go to your fork's main branch
   - Verify the 4 commits appear in the commit history
   - Check that new files are visible

2. **Update local main branch**:
   ```bash
   cd /home/user/InvokeAI
   git checkout main
   git pull origin main
   ```

✅ **Part 1 Complete!** Your changes are now in your fork's main branch.

---

## PART 2: Set Up InvokeAI Locally

### Step 5: Install System Dependencies

**Check Python Version** (requires Python 3.10+):
```bash
python3 --version
```

If Python < 3.10, install Python 3.10 or 3.11:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11
```

**Install Other Dependencies**:
```bash
# Ubuntu/Debian
sudo apt install -y \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev \
  python3-pip \
  git \
  wget \
  curl

# macOS (via Homebrew)
brew install python@3.11 git wget
```

---

### Step 6: Install InvokeAI

**Navigate to repository**:
```bash
cd /home/user/InvokeAI
```

**Create virtual environment**:
```bash
# Create venv
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

**Install InvokeAI with dependencies**:
```bash
# Install InvokeAI in editable mode with all dependencies
pip install -e ".[dev,test]"

# Install cloud model dependencies
pip install httpx>=0.27.0 python-dotenv>=1.0.0 google-auth>=2.29.0
```

This will take 5-15 minutes depending on your internet speed.

---

### Step 7: Install Frontend Dependencies

InvokeAI uses pnpm for frontend package management:

**Install Node.js** (if not already installed):
```bash
# Check if Node.js is installed
node --version

# If not installed (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node
```

**Install pnpm**:
```bash
npm install -g pnpm
```

**Install frontend dependencies**:
```bash
cd /home/user/InvokeAI/invokeai/frontend/web
pnpm install
```

This will take 3-10 minutes.

---

### Step 8: Initialize InvokeAI

**Run InvokeAI configuration**:
```bash
cd /home/user/InvokeAI
source .venv/bin/activate

# Initialize InvokeAI (creates config, downloads models)
invokeai-configure --yes
```

This will:
- Create configuration directory (`~/.invokeai/` by default)
- Set up database
- Optionally download starter models
- Create initial config files

**Choose your setup**:
- When prompted, you can choose to download starter models or skip for now
- For testing cloud models, you don't need local models immediately
- Can download models later from the UI

---

## PART 3: Configure Cloud Providers

### Step 9: Get API Keys

You'll need API keys from the providers you want to use.

#### Google Gemini API Key

1. **Visit**: https://ai.google.dev/
2. Click "Get API key in Google AI Studio"
3. Sign in with Google account
4. Click "Create API key"
5. Select or create a Google Cloud project
6. Copy the API key (starts with `AIza...`)
7. **Keep this secure!**

#### Google Imagen (Vertex AI)

1. **Create Google Cloud Project**: https://console.cloud.google.com/
2. **Enable Vertex AI API**:
   - Go to: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
   - Click "Enable"
3. **Enable Billing**: Cloud project must have billing enabled
4. **Set up authentication**:

   **Option A: Local Development (gcloud CLI)**
   ```bash
   # Install gcloud CLI if not installed
   # See: https://cloud.google.com/sdk/docs/install

   # Authenticate
   gcloud auth application-default login

   # Set project
   gcloud config set project YOUR_PROJECT_ID
   ```

   **Option B: Service Account**
   - Create service account in Google Cloud Console
   - Grant "Vertex AI User" role
   - Download JSON key file
   - Set environment variable (we'll do this in Step 10)

5. **Note your**:
   - Project ID (e.g., `my-project-123456`)
   - Region (e.g., `us-central1`)

#### OpenAI API Key

1. **Visit**: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Name it (e.g., "InvokeAI Cloud Models")
5. Copy the key (starts with `sk-proj-` or `sk-`)
6. **Keep this secure!**
7. **Set up billing**:
   - Go to: https://platform.openai.com/account/billing
   - Add payment method
   - Add credits or set up auto-recharge
   - **Note**: DALL-E 3 requires active billing

---

### Step 10: Configure .env File

**Create .env file** in InvokeAI root:
```bash
cd /home/user/InvokeAI

# Create .env file
touch .env

# Edit with your preferred editor
nano .env
```

**Add your API keys** (replace with your actual keys):
```bash
# ============================================
# CLOUD MODEL PROVIDER API KEYS
# ============================================

# Google Gemini API Key
# Get from: https://ai.google.dev/
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXX

# Google Imagen (Vertex AI) Configuration
# Get from: https://console.cloud.google.com/
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Optional: If using service account JSON key instead of gcloud auth
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OpenAI API Key
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX

# ============================================
# NOTES
# ============================================
# - Never commit this file to git (.gitignore already includes it)
# - Keep your API keys secure
# - Each provider is optional - only configure what you want to use
# - Restart InvokeAI after changing this file
```

**Save and exit** (in nano: Ctrl+O, Enter, Ctrl+X)

**Verify .env is gitignored**:
```bash
git check-ignore .env
# Should output: .env
```

---

## PART 4: Test the Integration

### Step 11: Run Backend Tests

**Test each provider** with the integration scripts:

#### Test Google Gemini
```bash
cd /home/user/InvokeAI
source .venv/bin/activate

python scripts/test_gemini_integration.py
```

**Expected output**:
```
✓ Loaded .env file
✓ Found API key: AIzaXXXXXXXXXXXXXXXX...
✓ Successfully imported Gemini provider
✓ Created Gemini provider instance
✓ API credentials are valid
✓ Successfully generated image
✓ Saved test image to: outputs/test_gemini_output.png

✓ ALL TESTS PASSED!
```

#### Test Google Imagen
```bash
python scripts/test_imagen_integration.py
```

**Expected output**:
```
✓ Loaded .env file
✓ Found Google Cloud project: your-project-id
✓ Using region: us-central1
✓ Successfully imported Imagen provider
✓ Created Imagen provider instance
✓ Google Cloud credentials are valid
✓ Vertex AI API is accessible
✓ Successfully generated image
✓ Saved test image to: outputs/test_imagen_output.png

✓ ALL TESTS PASSED!
```

#### Test OpenAI
```bash
python scripts/test_openai_integration.py
```

**Expected output**:
```
✓ Loaded .env file
✓ Found API key: sk-proj-XXXXXXXXXXXX...
✓ Successfully imported OpenAI provider
✓ Created OpenAI provider instance
✓ OpenAI API key is valid
✓ Successfully generated image
✓ Saved test image to: outputs/test_dalle3_output.png

📝 DALL-E 3 Revised Prompt:
   A high-quality photograph of a majestic sunset...

✓ ALL TESTS PASSED!
```

**Check generated images**:
```bash
ls -lh outputs/test_*_output.png
```

---

### Step 12: Start InvokeAI

**Option A: Development Mode (Backend + Frontend separate)**

Terminal 1 - Backend:
```bash
cd /home/user/InvokeAI
source .venv/bin/activate
invokeai-web
```

Terminal 2 - Frontend (for live UI development):
```bash
cd /home/user/InvokeAI/invokeai/frontend/web
pnpm dev
```

**Option B: Production Mode (Bundled)**

```bash
cd /home/user/InvokeAI
source .venv/bin/activate

# Build frontend first (one-time)
cd invokeai/frontend/web
pnpm build

# Start InvokeAI
cd /home/user/InvokeAI
invokeai-web
```

**Access InvokeAI**:
- Open browser to: `http://localhost:9090`
- You should see the InvokeAI interface

---

### Step 13: Test Cloud Provider Settings in UI

1. **Open Settings**:
   - Click the ⚙️ (Settings) icon in the top navigation
   - Settings modal opens

2. **Scroll to Cloud Providers section**:
   - Should see "Cloud Providers" accordion
   - Expand it

3. **Check Provider Status**:
   - You should see three providers:
     - ✨ Google Gemini 2.5 Flash
     - 🎨 Google Imagen 4 Ultra
     - 🤖 OpenAI DALL-E

   - Initial status might be 🟡 "Configured" (credentials exist but not validated)

4. **Refresh Status**:
   - Click **"Refresh Provider Status"** button
   - Status should update to:
     - 🟢 "Connected" (if credentials are valid)
     - 🔴 "Invalid Credentials" (if there's an issue)
     - 🔴 "Not Configured" (if .env not set up)

5. **Check Settings**:
   - Toggle "Check Provider Status on Startup" (optional)
   - Toggle "Show Cost Estimates" (recommended: ON)

**If you see errors**:
- Check console (F12) for error messages
- Verify .env file is in correct location
- Ensure InvokeAI was restarted after adding .env
- Check API keys are correct and active

---

### Step 14: Test Cloud Model Workflow

1. **Go to Workflow Editor**:
   - Click "Workflows" or "Linear" tab
   - Click to add a new node

2. **Find Cloud Nodes**:
   Search for:
   - "Gemini 2.5 Flash - Text to Image"
   - "Imagen 4 Ultra - Text to Image"
   - "OpenAI DALL-E 3 - Text to Image"
   - "OpenAI DALL-E 2 - Text to Image"

3. **Test Gemini Node**:
   - Add "Gemini 2.5 Flash - Text to Image" node
   - Set parameters:
     - Prompt: "A serene mountain landscape at sunset"
     - Aspect Ratio: 16:9
     - Seed: 42 (for reproducibility)

   - **If "Show Cost Estimates" is enabled**, you should see:
     ```
     💰 Estimated Cost: $0.0390 (1 image)
     ```

   - Connect to output node
   - Click **Invoke**

4. **Verify Results**:
   - Image should generate in ~5-15 seconds
   - Check image appears in gallery
   - Verify image quality and dimensions

5. **Test Other Providers**:
   - Try Imagen node (batch generation: set num_images to 4)
   - Try DALL-E 3 (try quality: HD, style: vivid)
   - Try DALL-E 2 (try batch: 10 images)

6. **Check Cost Estimates Update**:
   - Change num_images
   - Change size/quality
   - Cost estimate should update in real-time

---

### Step 15: Verify All Features

**Backend Checklist**:
- ✅ Gemini provider generates images
- ✅ Imagen provider generates images (batch if num_images > 1)
- ✅ DALL-E 3 generates images with quality/style
- ✅ DALL-E 2 generates images (batch if num_images > 1)
- ✅ Seeds work for Gemini/Imagen (same prompt+seed = same image)
- ✅ Different aspect ratios work

**Frontend Checklist**:
- ✅ Settings → Cloud Providers section exists
- ✅ Provider status indicators show correct status
- ✅ Refresh button updates status
- ✅ Cost estimates display correctly
- ✅ Cost estimates update when parameters change
- ✅ Settings persist after page reload

**Integration Checklist**:
- ✅ Cloud nodes appear in workflow editor
- ✅ Generated images save to gallery
- ✅ Metadata includes provider info
- ✅ No console errors
- ✅ No API key exposure in browser

---

## PART 5: Troubleshooting

### Common Issues and Solutions

#### Issue: "API key not found"

**Symptoms**:
- Provider shows "Not Configured"
- Test script fails with ValueError

**Solutions**:
1. Check .env file exists: `ls -la /home/user/InvokeAI/.env`
2. Check .env has correct format (no spaces around =)
3. Verify API key variable names match exactly
4. Restart InvokeAI after editing .env
5. Check .env is in InvokeAI root, not subdirectory

#### Issue: "Invalid credentials"

**Symptoms**:
- Provider shows "Invalid Credentials"
- API returns 401/403 errors

**Solutions**:

**For Gemini**:
- Verify API key is correct (starts with `AIza`)
- Check key isn't restricted to specific domains
- Ensure Generative Language API is enabled in Google Cloud
- Try creating a new API key

**For Imagen**:
- Run `gcloud auth application-default login`
- Verify project ID is correct
- Check Vertex AI API is enabled
- Verify billing is enabled on project
- Check you have "Vertex AI User" role

**For OpenAI**:
- Verify API key is correct (starts with `sk-proj-` or `sk-`)
- Check billing is set up and has credits
- Verify key hasn't been revoked
- Try creating a new API key

#### Issue: "Module not found"

**Symptoms**:
- Import errors when running test scripts
- "No module named 'httpx'" or similar

**Solutions**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install httpx python-dotenv google-auth

# Or reinstall everything
pip install -e ".[dev]"
```

#### Issue: Frontend not loading

**Symptoms**:
- Blank page or build errors
- 404 errors in browser console

**Solutions**:
```bash
# Rebuild frontend
cd /home/user/InvokeAI/invokeai/frontend/web
rm -rf node_modules .next
pnpm install
pnpm build

# Restart backend
cd /home/user/InvokeAI
source .venv/bin/activate
invokeai-web
```

#### Issue: Cloud nodes not appearing

**Symptoms**:
- Can't find cloud nodes in workflow editor

**Solutions**:
1. Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
2. Check backend console for errors
3. Verify invocation files exist:
   ```bash
   ls -l invokeai/app/invocations/*text_to_image.py
   ```
4. Check providers imported correctly in backend logs

#### Issue: Cost estimates not showing

**Symptoms**:
- No cost display below node parameters

**Solutions**:
1. Open Settings → Cloud Providers
2. Enable "Show Cost Estimates"
3. Refresh page
4. Verify provider is connected (status check)

---

## PART 6: Next Steps

### After Successful Testing

1. **Update Documentation** (if needed):
   - Add any environment-specific notes
   - Document your specific setup

2. **Set Up Production** (optional):
   - Configure reverse proxy (nginx)
   - Set up SSL certificates
   - Configure firewall rules
   - Set resource limits

3. **Monitor Usage**:
   - Check provider dashboards for usage
   - Set up billing alerts
   - Monitor costs

4. **Optimize Workflow**:
   - Create workflow templates
   - Set up favorite providers
   - Build hybrid local+cloud workflows

5. **Share with Team** (optional):
   - Document your .env setup process
   - Share workflow templates
   - Set up shared API keys (with caution)

---

## Quick Reference Commands

```bash
# Activate environment
cd /home/user/InvokeAI
source .venv/bin/activate

# Start InvokeAI
invokeai-web

# Run tests
python scripts/test_gemini_integration.py
python scripts/test_imagen_integration.py
python scripts/test_openai_integration.py

# Check logs
tail -f ~/.invokeai/logs/invokeai.log

# Update dependencies
pip install --upgrade httpx python-dotenv google-auth

# Rebuild frontend
cd invokeai/frontend/web
pnpm build

# Check git status
git status
git log --oneline -10
```

---

## Support Resources

- **Documentation**:
  - Backend: `docs/features/CLOUD_MODELS.md`
  - Frontend: `docs/features/CLOUD_MODELS_UI.md`

- **Provider Documentation**:
  - Google Gemini: https://ai.google.dev/gemini-api/docs/image-generation
  - Google Imagen: https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview
  - OpenAI DALL-E: https://platform.openai.com/docs/guides/images

- **InvokeAI Community**:
  - Discord: https://discord.gg/ZmtBAhwWhy
  - GitHub Issues: https://github.com/invoke-ai/InvokeAI/issues
  - Discussions: https://github.com/invoke-ai/InvokeAI/discussions

---

## Security Checklist

Before deploying to production:

- [ ] .env file is gitignored
- [ ] API keys are secure and not shared
- [ ] Billing alerts set up on all providers
- [ ] Usage limits configured (if available)
- [ ] Regular key rotation scheduled
- [ ] Backup .env file to secure location
- [ ] Team access to API keys controlled
- [ ] Monitoring/logging enabled
- [ ] HTTPS configured (if exposing externally)
- [ ] Firewall rules configured

---

**Ready to begin? Let's start with Part 1: Creating the Pull Request!**
