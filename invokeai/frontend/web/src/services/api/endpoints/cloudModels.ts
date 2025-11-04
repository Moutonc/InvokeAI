/**
 * RTK Query API endpoints for cloud model management.
 *
 * These endpoints connect to the backend cloud model service layer
 * created in Phase 2 of the cloud model integration.
 */

import { api, buildV1Url } from '..';

/**
 * Type definitions matching backend API models
 */

export type CloudProviderType = 'google-gemini' | 'google-imagen' | 'openai';

// Request types
export interface CloudModelRegistrationRequest {
  name: string;
  provider: CloudProviderType;
  cloud_model_id: string;
  source: string;
  description?: string | null;
}

export interface ListCloudModelsParams {
  provider?: CloudProviderType;
}

// Response types
export interface CloudModelRegistrationResponse {
  key: string;
  name: string;
  provider: CloudProviderType;
  message: string;
}

export interface CloudModelConfig {
  key: string;
  name: string;
  description?: string | null;
  type: string;
  base: string;
  format: string;
  source: string;
  source_type: string;
  provider: CloudProviderType;
  cloud_model_id: string;
  [key: string]: unknown; // Allow additional provider-specific fields
}

export interface CloudModelsList {
  models: CloudModelConfig[];
}

export interface APIKeyValidationResponse {
  provider: CloudProviderType;
  valid: boolean;
  message: string;
}

export interface CloudProviderInfo {
  provider: CloudProviderType;
  is_configured: boolean;
  is_valid: boolean | null;
  error_message?: string;
  supported_models: string[];
}

/**
 * Builds an endpoint URL for the cloud models router
 * @example
 * buildCloudModelsUrl('validate/google-gemini')
 * // '/api/v1/models/cloud/validate/google-gemini'
 */
const buildCloudModelsUrl = (path: string = '') => buildV1Url(`models/cloud/${path}`);

/**
 * Cloud models API endpoints
 */
export const cloudModelsApi = api.injectEndpoints({
  endpoints: (build) => ({
    /**
     * Register a new cloud model
     */
    registerCloudModel: build.mutation<CloudModelRegistrationResponse, CloudModelRegistrationRequest>({
      query: (body) => ({
        url: buildCloudModelsUrl(),
        method: 'POST',
        body,
      }),
      invalidatesTags: ['ModelConfig'],
    }),

    /**
     * List all registered cloud models
     */
    listCloudModels: build.query<CloudModelsList, ListCloudModelsParams | void>({
      query: (params) => ({
        url: buildCloudModelsUrl(),
        method: 'GET',
        params,
      }),
      providesTags: ['ModelConfig'],
    }),

    /**
     * Get a specific cloud model by key
     */
    getCloudModel: build.query<CloudModelConfig, string>({
      query: (key) => ({
        url: buildCloudModelsUrl(key),
        method: 'GET',
      }),
      providesTags: (_result, _error, key) => [{ type: 'ModelConfig', id: key }],
    }),

    /**
     * Delete a cloud model
     */
    deleteCloudModel: build.mutation<void, string>({
      query: (key) => ({
        url: buildCloudModelsUrl(key),
        method: 'DELETE',
      }),
      invalidatesTags: ['ModelConfig'],
    }),

    /**
     * Validate provider API key
     */
    validateProvider: build.query<ProviderValidationResponse, string>({
      query: (provider) => ({
        url: buildCloudModelsUrl(`validate/${provider}`),
        method: 'GET',
      }),
    }),

    /**
     * List cloud providers (for backwards compatibility with existing UI)
     * This synthesizes provider info from registered cloud models
     */
    listCloudProviders: build.query<CloudProviderInfo[], { checkCredentials?: boolean } | void>({
      query: () => ({
        url: buildCloudModelsUrl(),
        method: 'GET',
      }),
      transformResponse: (response: CloudModelsList) => {
        // All possible providers
        const allProviders: CloudProviderType[] = ['google-gemini', 'google-imagen', 'openai'];

        // Group models by provider
        const providerMap = new Map<CloudProviderType, CloudProviderInfo>();

        // Initialize all providers as not configured
        allProviders.forEach((provider) => {
          providerMap.set(provider, {
            provider,
            is_configured: false,
            is_valid: null,
            supported_models: [],
          });
        });

        // Update with registered models
        response.models.forEach((model) => {
          const provider = model.provider;
          if (!providerMap.has(provider)) {
            providerMap.set(provider, {
              provider,
              is_configured: true,
              is_valid: true,
              supported_models: [],
            });
          } else {
            const info = providerMap.get(provider)!;
            info.is_configured = true;
            info.is_valid = true;
          }
          providerMap.get(provider)!.supported_models.push(model.cloud_model_id);
        });

        return Array.from(providerMap.values());
      },
      providesTags: ['ModelConfig'],
    }),
  }),
});

export const {
  useRegisterCloudModelMutation,
  useListCloudModelsQuery,
  useGetCloudModelQuery,
  useDeleteCloudModelMutation,
  useValidateProviderQuery,
  useListCloudProvidersQuery,
} = cloudModelsApi;
