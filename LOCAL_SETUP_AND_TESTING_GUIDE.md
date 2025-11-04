# Cloud Models - Local Setup and Testing Guide

**Complete guide to sync code changes and run tests in your local environment**

---

## Step 1: Sync Code Changes to Your Local Environment

### Option A: If You're Starting Fresh

```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/Moutonc/InvokeAI.git
cd InvokeAI

# 2. Fetch all branches
git fetch origin

# 3. Checkout the cloud models branch
git checkout claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 4. Verify you're on the right branch
git branch
# Should show: * claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 5. Verify you have the latest code
git log --oneline -5
# Should show: d632968 docs: Phase 5 - Complete documentation suite (PROJECT COMPLETE! 🎉)
```

### Option B: If You Already Have the Repo Locally

```bash
# 1. Navigate to your InvokeAI directory
cd /path/to/your/InvokeAI

# 2. Make sure your working directory is clean
git status
# If you have uncommitted changes, stash or commit them first

# 3. Fetch all remote branches
git fetch origin

# 4. Checkout the cloud models branch
git checkout claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 5. Pull the latest changes
git pull origin claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 6. Verify you have all the commits
git log --oneline -5
# Should show the latest commit: d632968
```

### Verify Files Are Present

```bash
# Check that new files exist
ls -la CLOUD_MODELS*.md
# Should see:
# - CLOUD_MODELS_CURRENT_STATE_AND_FORWARD_PLAN.md
# - CLOUD_MODELS_DEVELOPER_GUIDE.md
# - CLOUD_MODELS_FINAL_SUMMARY.md
# - CLOUD_MODELS_PROGRESS_SUMMARY.md
# - CLOUD_MODELS_TRANSLATION_KEYS.md
# - CLOUD_MODELS_USER_GUIDE.md

# Check backend files
ls invokeai/app/services/cloud_models/
# Should see:
# - __init__.py
# - cloud_model_service_base.py
# - cloud_model_service.py

# Check API router
ls invokeai/app/api/routers/cloud_models.py

# Check tests
ls tests/app/services/test_cloud_model_service.py
ls tests/backend/model_manager/test_cloud_model*.py

# Check frontend files
ls invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts
ls invokeai/frontend/web/src/features/cloudIntegration/components/CloudModelRegistrationPanel.tsx
```

---

## Step 2: Set Up Your Python Environment

### Prerequisites

You need Python 3.10 or 3.11 installed.

### Install InvokeAI Dependencies

```bash
# Method 1: Using the InvokeAI installer (recommended)
python scripts/install.py

# Method 2: Manual pip install
pip install -e ".[test]"
# This installs InvokeAI in editable mode with test dependencies

# Method 3: If you have a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[test]"
```

### Verify Installation

```bash
# Check that InvokeAI imports work
python -c "import invokeai; print('✓ InvokeAI imports successfully')"

# Check specific cloud model imports
python -c "from invokeai.backend.model_manager.configs.cloud_models import GeminiFlashImageConfig; print('✓ Cloud configs import')"
```

---

## Step 3: Configure API Keys (For Testing)

Cloud model functionality requires API keys. You'll need at least one:

### Create .env File

```bash
# Copy the example (if it exists) or create new
touch .env

# Edit with your preferred editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

### Add Your API Keys

Add at least ONE of these to your `.env` file:

```bash
# For Google Gemini (easiest to get)
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXX

# For Google Imagen (requires Google Cloud setup)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# For OpenAI
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX
```

**Getting API Keys:**
- **Gemini**: https://ai.google.dev/ → "Get API key"
- **Imagen**: https://console.cloud.google.com/ → Enable Vertex AI
- **OpenAI**: https://platform.openai.com/api-keys → "Create new secret key"

**Note**: You only need ONE provider configured to test basic functionality.

---

## Step 4: Run Backend Tests

### Run All Cloud Model Tests

```bash
# Run all tests related to cloud models
pytest tests/ -k "cloud" -v

# Expected output: 119+ tests should be collected
# Example:
# tests/app/services/test_cloud_model_service.py::test_... PASSED
# tests/backend/model_manager/test_cloud_model_configs.py::test_... PASSED
# etc.
```

### Run Specific Test Files

```bash
# Run service layer tests
pytest tests/app/services/test_cloud_model_service.py -v

# Run config tests
pytest tests/backend/model_manager/test_cloud_model_configs.py -v

# Run E2E tests
pytest tests/backend/model_manager/test_cloud_model_e2e.py -v

# Run validation tests
pytest tests/backend/model_manager/test_cloud_model_validation.py -v

# Run API tests
pytest tests/app/api/test_cloud_models_api.py -v
```

### Run Tests With Coverage

```bash
# Run with coverage report
pytest tests/ -k "cloud" -v --cov=invokeai.app.services.cloud_models --cov=invokeai.backend.model_manager.configs.cloud_models --cov-report=html

# View coverage report
open htmlcov/index.html  # On Mac
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

### Expected Results

```
================================ test session starts =================================
platform linux -- Python 3.11.x, pytest-7.x.x
collected 119 items

tests/app/services/test_cloud_model_service.py ...................... [ 17%]
tests/backend/model_manager/test_cloud_model_configs.py ............. [ 33%]
tests/backend/model_manager/test_cloud_model_e2e.py ................. [ 54%]
tests/backend/model_manager/test_cloud_model_validation.py .......... [ 79%]
tests/app/api/test_cloud_models_api.py ............................ [100%]

============================== 119 passed in 45.2s ===============================
```

---

## Step 5: Test Backend API Manually

### Start the InvokeAI Server

```bash
# Start the server (defaults to http://localhost:9090)
python scripts/invokeai-web.py

# Or with specific settings
python scripts/invokeai-web.py --host 0.0.0.0 --port 9090

# Wait for server to start - you should see:
# INFO: Application startup complete.
# INFO: Uvicorn running on http://0.0.0.0:9090
```

### Run the Interactive Test Script

Open a **new terminal** (keep the server running in the first one):

```bash
# Activate your virtual environment if needed
source .venv/bin/activate

# Run the test script
python test_cloud_models_api.py

# Follow the interactive prompts to:
# 1. Choose a provider (Gemini recommended)
# 2. Test registration
# 3. Test listing
# 4. Test getting specific model
# 5. Test deletion (optional)
```

### Manual API Testing with curl

```bash
# Test 1: Register a cloud model
curl -X POST http://localhost:9090/api/v1/models/cloud \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Gemini Model",
    "provider": "google-gemini",
    "cloud_model_id": "gemini-2.5-flash-image",
    "source": "https://ai.google.dev/",
    "description": "Test model"
  }'

# Expected: HTTP 201 with model details

# Test 2: List all cloud models
curl http://localhost:9090/api/v1/models/cloud

# Expected: HTTP 200 with array of models

# Test 3: Validate provider
curl http://localhost:9090/api/v1/models/cloud/validate/google-gemini

# Expected: HTTP 200 with validation status
```

---

## Step 6: Test Frontend (Optional)

### Install Frontend Dependencies

```bash
cd invokeai/frontend/web

# Install dependencies (using pnpm, InvokeAI's preferred package manager)
pnpm install

# Or if you prefer npm
npm install
```

### Build Frontend

```bash
# Development build
pnpm run dev

# Production build
pnpm run build

# Type checking
pnpm run lint:tsc
```

### Test in Browser

1. **Start the InvokeAI server** (if not already running):
   ```bash
   python scripts/invokeai-web.py
   ```

2. **Open browser** to http://localhost:9090

3. **Test Cloud Model Registration**:
   - Click Settings (gear icon)
   - Scroll to "Register Cloud Model"
   - Expand the accordion
   - Select a model from dropdown
   - Enter a name
   - Click "Register Model"
   - Should see success toast

4. **Test Model List**:
   - Go to Model Manager
   - Look for cloud models with ☁️ icon
   - Verify provider badge shows
   - Verify "Cloud" instead of file size

---

## Step 7: Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'XXX'"

**Solution**: Install dependencies
```bash
pip install -e ".[test]"
```

#### Issue: "API key not found" or tests fail

**Solution**: Check your `.env` file
```bash
# Verify .env exists
cat .env | grep -E "GOOGLE_API_KEY|OPENAI_API_KEY"

# Make sure server was restarted after adding keys
# Ctrl+C to stop server, then restart:
python scripts/invokeai-web.py
```

#### Issue: "Connection refused" when running test script

**Solution**: Make sure InvokeAI server is running
```bash
# Check if server is running
curl http://localhost:9090/api/v1/app/version

# If not, start it:
python scripts/invokeai-web.py
```

#### Issue: Tests fail with import errors

**Solution**: You might be missing test dependencies
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

#### Issue: Frontend build fails

**Solution**: Clear cache and reinstall
```bash
cd invokeai/frontend/web
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

---

## Step 8: Verify Everything Works

### Quick Verification Checklist

Run these commands to verify your setup:

```bash
# ✓ Check you're on the right branch
git branch | grep claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# ✓ Check files exist
ls CLOUD_MODELS_USER_GUIDE.md
ls invokeai/app/services/cloud_models/cloud_model_service.py
ls tests/app/services/test_cloud_model_service.py

# ✓ Check Python imports work
python -c "from invokeai.app.services.cloud_models import CloudModelService; print('✓')"

# ✓ Check config imports work
python -c "from invokeai.backend.model_manager.configs.cloud_models import GeminiFlashImageConfig; print('✓')"

# ✓ Run a quick test
pytest tests/backend/model_manager/test_cloud_model_configs.py -v

# ✓ Check server can start (Ctrl+C to stop after it starts)
python scripts/invokeai-web.py
```

If all of these succeed, you're good to go! ✅

---

## Step 9: Full Test Suite

### Run Complete Test Suite

```bash
# Run ALL cloud model tests with verbose output
pytest tests/ -k "cloud" -v --tb=short

# Run with coverage report
pytest tests/ -k "cloud" -v --cov=invokeai.app.services.cloud_models --cov=invokeai.backend.model_manager.configs.cloud_models --cov-report=term-missing

# Run and generate HTML coverage report
pytest tests/ -k "cloud" -v --cov=invokeai.app.services.cloud_models --cov=invokeai.backend.model_manager.configs.cloud_models --cov-report=html
```

### Expected Output

You should see approximately **119+ tests** run:

```
tests/app/api/test_cloud_models_api.py::TestCloudModelsAPI::test_register_model PASSED
tests/app/api/test_cloud_models_api.py::TestCloudModelsAPI::test_list_models PASSED
...
tests/app/services/test_cloud_model_service.py::TestCloudModelService::test_register_gemini PASSED
...
tests/backend/model_manager/test_cloud_model_configs.py::TestGeminiConfig::test_from_registration PASSED
...
tests/backend/model_manager/test_cloud_model_e2e.py::test_gemini_full_workflow PASSED
...
tests/backend/model_manager/test_cloud_model_validation.py::TestPhase1Validation::test_no_file_fields PASSED
...

============================== 119 passed in 60.3s ===============================
```

---

## Step 10: Run Integration Tests

### End-to-End Workflow Test

With the server running, test a complete workflow:

```bash
# Terminal 1: Server running
python scripts/invokeai-web.py

# Terminal 2: Run E2E test
python test_cloud_models_api.py

# Or manually:
# 1. Register a model
curl -X POST http://localhost:9090/api/v1/models/cloud \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","provider":"google-gemini","cloud_model_id":"gemini-2.5-flash-image","source":"https://ai.google.dev/"}'

# 2. List models (should see your model)
curl http://localhost:9090/api/v1/models/cloud

# 3. Get specific model (use key from step 1)
curl http://localhost:9090/api/v1/models/cloud/{KEY}

# 4. Delete model
curl -X DELETE http://localhost:9090/api/v1/models/cloud/{KEY}
```

---

## Quick Start Summary

**Fastest way to get testing:**

```bash
# 1. Sync code
git checkout claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk
git pull origin claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 2. Install dependencies
pip install -e ".[test]"

# 3. Add at least one API key to .env
echo "GOOGLE_API_KEY=your-key-here" > .env

# 4. Run tests
pytest tests/ -k "cloud" -v

# 5. Test API (in 2 terminals)
# Terminal 1:
python scripts/invokeai-web.py

# Terminal 2:
python test_cloud_models_api.py
```

---

## Documentation Reference

- **User Guide**: `CLOUD_MODELS_USER_GUIDE.md`
- **Developer Guide**: `CLOUD_MODELS_DEVELOPER_GUIDE.md`
- **Testing Guide**: `PHASE4_TESTING_GUIDE.md`
- **Progress Summary**: `CLOUD_MODELS_PROGRESS_SUMMARY.md`

---

## Need Help?

If you encounter issues:

1. Check **PHASE4_TESTING_GUIDE.md** for detailed troubleshooting
2. Verify your Python version: `python --version` (should be 3.10 or 3.11)
3. Check your API keys are set correctly in `.env`
4. Make sure InvokeAI server is running when testing API
5. Check the InvokeAI logs for error messages

---

**You're all set! Happy testing! 🚀**
