/**
 * TypeScript types for cloud model integration.
 * These mirror the backend API types from cloud_models.py router.
 */

export type CloudProviderType = 'google-gemini' | 'google-imagen' | 'openai';

export type ProviderStatus = 'configured' | 'not_configured' | 'valid' | 'invalid' | 'error';

export interface CloudProviderInfo {
  provider: CloudProviderType;
  name: string;
  status: ProviderStatus;
  is_configured: boolean;
  is_valid?: boolean | null;
  supported_models: string[];
  error_message?: string | null;
}

export interface CloudModelInfo {
  key: string;
  provider: CloudProviderType;
  model_id: string;
  name: string;
  description: string;
  supported_sizes: string[];
  cost_per_image: Record<string, number>;
  features: string[];
}

export interface CostEstimate {
  provider: CloudProviderType;
  model_id: string;
  num_images: number;
  size: string;
  quality?: string | null;
  estimated_cost: number;
  currency: string;
}

/**
 * Provider display information for UI
 */
export interface ProviderDisplayInfo {
  provider: CloudProviderType;
  displayName: string;
  icon: string;
  description: string;
  docsUrl: string;
  setupInstructions: string;
}

/**
 * Map of provider types to display information
 */
export const PROVIDER_DISPLAY_INFO: Record<CloudProviderType, ProviderDisplayInfo> = {
  'google-gemini': {
    provider: 'google-gemini',
    displayName: 'Google Gemini 2.5 Flash',
    icon: '✨',
    description: 'Fast and affordable with 10 aspect ratios',
    docsUrl: 'https://ai.google.dev/gemini-api/docs/image-generation',
    setupInstructions: 'Get API key from https://ai.google.dev/',
  },
  'google-imagen': {
    provider: 'google-imagen',
    displayName: 'Google Imagen 4 Ultra',
    icon: '🎨',
    description: 'Premium quality with SynthID watermark',
    docsUrl: 'https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview',
    setupInstructions: 'Set up Google Cloud project and enable Vertex AI',
  },
  openai: {
    provider: 'openai',
    displayName: 'OpenAI DALL-E',
    icon: '🤖',
    description: 'DALL-E 3 with quality/style controls',
    docsUrl: 'https://platform.openai.com/docs/guides/images',
    setupInstructions: 'Get API key from https://platform.openai.com/api-keys',
  },
};

/**
 * Status badge colors
 */
export const STATUS_COLORS: Record<ProviderStatus, string> = {
  configured: 'gray',
  not_configured: 'red',
  valid: 'green',
  invalid: 'orange',
  error: 'red',
};

/**
 * Status display text
 */
export const STATUS_TEXT: Record<ProviderStatus, string> = {
  configured: 'Configured',
  not_configured: 'Not Configured',
  valid: 'Connected',
  invalid: 'Invalid Credentials',
  error: 'Error',
};
