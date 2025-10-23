/**
 * RTK Query API endpoints for cloud model operations.
 */

import type {
  CloudModelInfo,
  CloudProviderInfo,
  CloudProviderType,
  CostEstimate,
} from 'features/cloudIntegration/types';
import { api } from 'services/api';

/**
 * Cloud models API endpoints
 */
export const cloudModelsApi = api.injectEndpoints({
  endpoints: (build) => ({
    /**
     * List all cloud providers with their status
     */
    listCloudProviders: build.query<CloudProviderInfo[], { checkCredentials?: boolean }>({
      query: ({ checkCredentials = false }) => ({
        url: 'api/v2/cloud/providers',
        method: 'GET',
        params: { check_credentials: checkCredentials },
      }),
      providesTags: ['CloudProviders'],
    }),

    /**
     * Get status of a specific cloud provider
     */
    getCloudProviderStatus: build.query<CloudProviderInfo, CloudProviderType>({
      query: (provider) => ({
        url: `api/v2/cloud/providers/${provider}/status`,
        method: 'GET',
      }),
      providesTags: (result, error, provider) => [{ type: 'CloudProviders', id: provider }],
    }),

    /**
     * List all available cloud models
     */
    listCloudModels: build.query<CloudModelInfo[], { provider?: CloudProviderType; onlyConfigured?: boolean }>({
      query: ({ provider, onlyConfigured = false }) => ({
        url: 'api/v2/cloud/models',
        method: 'GET',
        params: {
          provider,
          only_configured: onlyConfigured,
        },
      }),
      providesTags: ['CloudModels'],
    }),

    /**
     * Estimate cost for a cloud generation request
     */
    estimateCloudGenerationCost: build.mutation<
      CostEstimate,
      {
        provider: CloudProviderType;
        model_id: string;
        num_images?: number;
        width?: number;
        height?: number;
        quality?: string;
      }
    >({
      query: (params) => ({
        url: 'api/v2/cloud/estimate_cost',
        method: 'POST',
        params,
      }),
    }),
  }),
});

export const {
  useListCloudProvidersQuery,
  useLazyListCloudProvidersQuery,
  useGetCloudProviderStatusQuery,
  useLazyGetCloudProviderStatusQuery,
  useListCloudModelsQuery,
  useLazyListCloudModelsQuery,
  useEstimateCloudGenerationCostMutation,
} = cloudModelsApi;
