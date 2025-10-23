/**
 * Cost Estimation Display Component
 * Shows estimated cost for cloud generation requests
 */

import { Box, Flex, Spinner, Text, Tooltip } from '@invoke-ai/ui-library';
import { useAppSelector } from 'app/store/storeHooks';
import type { CloudProviderType } from 'features/cloudIntegration/types';
import { PROVIDER_DISPLAY_INFO } from 'features/cloudIntegration/types';
import { memo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useEstimateCloudGenerationCostMutation } from 'services/api/endpoints/cloudModels';

interface CostEstimationDisplayProps {
  provider: CloudProviderType;
  modelId: string;
  numImages?: number;
  width?: number;
  height?: number;
  quality?: string;
}

export const CostEstimationDisplay = memo(
  ({ provider, modelId, numImages = 1, width = 1024, height = 1024, quality }: CostEstimationDisplayProps) => {
    const { t } = useTranslation();
    const showCostEstimates = useAppSelector((s) => s.cloud.showCostEstimates);

    const [estimateCost, { data: estimate, isLoading, isError }] = useEstimateCloudGenerationCostMutation();

    // Estimate cost when parameters change
    useEffect(() => {
      if (showCostEstimates) {
        estimateCost({
          provider,
          model_id: modelId,
          num_images: numImages,
          width,
          height,
          quality,
        });
      }
    }, [provider, modelId, numImages, width, height, quality, showCostEstimates, estimateCost]);

    // Don't show if disabled
    if (!showCostEstimates) {
      return null;
    }

    const displayInfo = PROVIDER_DISPLAY_INFO[provider];

    return (
      <Tooltip label={t('cloudIntegration.estimatedCostTooltip')}>
        <Box bg="base.800" p={2} borderRadius="md" border="1px solid" borderColor="base.700">
          <Flex align="center" gap={2}>
            <Text fontSize="xs" fontWeight="medium" color="base.300">
              {t('cloudIntegration.estimatedCost')}:
            </Text>
            {isLoading ? (
              <Spinner size="xs" />
            ) : isError ? (
              <Text fontSize="xs" color="error.400">
                {t('cloudIntegration.errorEstimatingCost')}
              </Text>
            ) : estimate ? (
              <Flex align="center" gap={1}>
                <Text fontSize="sm">{displayInfo.icon}</Text>
                <Text fontSize="sm" fontWeight="bold" color="accent.400">
                  ${estimate.estimated_cost.toFixed(4)}
                </Text>
                <Text fontSize="xs" color="base.400">
                  ({numImages} {numImages === 1 ? 'image' : 'images'})
                </Text>
              </Flex>
            ) : null}
          </Flex>
        </Box>
      </Tooltip>
    );
  }
);

CostEstimationDisplay.displayName = 'CostEstimationDisplay';
