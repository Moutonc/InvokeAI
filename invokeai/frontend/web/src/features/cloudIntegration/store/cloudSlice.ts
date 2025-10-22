/**
 * Redux slice for cloud integration state management.
 */

import type { PayloadAction, SliceConfig } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';
import type { PersistConfig } from 'app/store/store';
import type { CloudProviderInfo, CloudProviderType } from 'features/cloudIntegration/types';
import { z } from 'zod';

/**
 * Zod schema for cloud integration state validation
 */
const zCloudState = z.object({
  providers: z.record(z.string(), z.any()).default({}),
  lastChecked: z.number().nullable().default(null),
  autoCheckOnStartup: z.boolean().default(true),
  showCostEstimates: z.boolean().default(true),
  selectedProvider: z.string().nullable().default(null),
});

export type CloudState = z.infer<typeof zCloudState>;

/**
 * Initial state for cloud integration
 */
const initialState: CloudState = {
  providers: {},
  lastChecked: null,
  autoCheckOnStartup: true,
  showCostEstimates: true,
  selectedProvider: null,
};

/**
 * Cloud integration slice
 */
export const cloudSlice = createSlice({
  name: 'cloud',
  initialState,
  reducers: {
    /**
     * Update provider status
     */
    providerStatusUpdated: (state, action: PayloadAction<CloudProviderInfo>) => {
      state.providers[action.payload.provider] = action.payload;
      state.lastChecked = Date.now();
    },

    /**
     * Update all providers
     */
    providersUpdated: (state, action: PayloadAction<CloudProviderInfo[]>) => {
      action.payload.forEach((provider) => {
        state.providers[provider.provider] = provider;
      });
      state.lastChecked = Date.now();
    },

    /**
     * Clear provider status
     */
    providerStatusCleared: (state, action: PayloadAction<CloudProviderType>) => {
      delete state.providers[action.payload];
    },

    /**
     * Set auto-check on startup preference
     */
    autoCheckOnStartupChanged: (state, action: PayloadAction<boolean>) => {
      state.autoCheckOnStartup = action.payload;
    },

    /**
     * Set show cost estimates preference
     */
    showCostEstimatesChanged: (state, action: PayloadAction<boolean>) => {
      state.showCostEstimates = action.payload;
    },

    /**
     * Set selected provider
     */
    selectedProviderChanged: (state, action: PayloadAction<CloudProviderType | null>) => {
      state.selectedProvider = action.payload;
    },

    /**
     * Reset to initial state
     */
    cloudReset: () => initialState,
  },
});

export const {
  providerStatusUpdated,
  providersUpdated,
  providerStatusCleared,
  autoCheckOnStartupChanged,
  showCostEstimatesChanged,
  selectedProviderChanged,
  cloudReset,
} = cloudSlice.actions;

/**
 * Persistence configuration
 */
const persistConfig: PersistConfig<CloudState> = {
  name: cloudSlice.name,
  initialState,
  migrate: (state) => {
    return zCloudState.parse(state);
  },
  persistDenylist: ['lastChecked'], // Don't persist last checked time
};

/**
 * Slice configuration for app store
 */
export const cloudSliceConfig: SliceConfig<CloudState> = {
  slice: cloudSlice,
  persistConfig,
};
