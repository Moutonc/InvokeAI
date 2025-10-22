/**
 * Provider Status Indicator Component
 * Shows the connection status of a cloud provider with a colored badge
 */

import { Badge, Flex, Spinner, Text, Tooltip } from '@invoke-ai/ui-library';
import type { CloudProviderInfo } from 'features/cloudIntegration/types';
import { STATUS_COLORS, STATUS_TEXT } from 'features/cloudIntegration/types';
import { memo } from 'react';

interface ProviderStatusIndicatorProps {
  provider: CloudProviderInfo;
  isLoading?: boolean;
  showText?: boolean;
}

export const ProviderStatusIndicator = memo(
  ({ provider, isLoading = false, showText = true }: ProviderStatusIndicatorProps) => {
    const colorScheme = STATUS_COLORS[provider.status];
    const statusText = STATUS_TEXT[provider.status];

    const tooltipContent = provider.error_message || statusText;

    return (
      <Tooltip label={tooltipContent}>
        <Flex align="center" gap={2}>
          {isLoading ? (
            <Spinner size="sm" />
          ) : (
            <Badge colorScheme={colorScheme} size="sm">
              {showText ? statusText : ''}
            </Badge>
          )}
          {provider.status === 'error' && provider.error_message && (
            <Text fontSize="xs" color="error.400">
              {provider.error_message.substring(0, 50)}
              {provider.error_message.length > 50 ? '...' : ''}
            </Text>
          )}
        </Flex>
      </Tooltip>
    );
  }
);

ProviderStatusIndicator.displayName = 'ProviderStatusIndicator';
