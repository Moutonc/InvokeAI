/**
 * Cloud Provider Settings Panel Component
 * Settings panel for managing cloud provider configurations
 */

import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Link,
  StandaloneAccordion,
  Switch,
  Text,
} from '@invoke-ai/ui-library';
import { useAppDispatch, useAppSelector } from 'app/store/storeHooks';
import { ProviderStatusIndicator } from 'features/cloudIntegration/components/ProviderStatusIndicator';
import {
  autoCheckOnStartupChanged,
  showCostEstimatesChanged,
} from 'features/cloudIntegration/store/cloudSlice';
import { PROVIDER_DISPLAY_INFO } from 'features/cloudIntegration/types';
import { useListCloudProvidersQuery } from 'services/api/endpoints/cloudModels';
import { memo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

export const CloudProviderSettingsPanel = memo(() => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();

  // Get state from Redux
  const autoCheckOnStartup = useAppSelector((s) => s.cloud.autoCheckOnStartup);
  const showCostEstimates = useAppSelector((s) => s.cloud.showCostEstimates);

  // Fetch provider status
  const { data: providers, isLoading, refetch } = useListCloudProvidersQuery({ checkCredentials: true });

  // Handlers
  const handleAutoCheckChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      dispatch(autoCheckOnStartupChanged(e.target.checked));
    },
    [dispatch]
  );

  const handleShowCostEstimatesChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      dispatch(showCostEstimatesChanged(e.target.checked));
    },
    [dispatch]
  );

  const handleRefreshStatus = useCallback(() => {
    refetch();
  }, [refetch]);

  return (
    <StandaloneAccordion label={t('settings.cloudProviders')} defaultIsOpen={false}>
      <Flex gap={4} flexDir="column">
        {/* Global Settings */}
        <Box>
          <FormControl>
            <FormLabel>{t('settings.autoCheckProvidersOnStartup')}</FormLabel>
            <Switch isChecked={autoCheckOnStartup} onChange={handleAutoCheckChange} />
          </FormControl>

          <FormControl mt={4}>
            <FormLabel>{t('settings.showCostEstimates')}</FormLabel>
            <Switch isChecked={showCostEstimates} onChange={handleShowCostEstimatesChange} />
          </FormControl>

          <Button onClick={handleRefreshStatus} size="sm" mt={4} isLoading={isLoading}>
            {t('settings.refreshProviderStatus')}
          </Button>
        </Box>

        {/* Provider Status List */}
        <Box>
          <Text fontSize="md" fontWeight="semibold" mb={2}>
            {t('settings.providerStatus')}
          </Text>

          {providers?.map((provider) => {
            const displayInfo = PROVIDER_DISPLAY_INFO[provider.provider];
            return (
              <Flex
                key={provider.provider}
                justify="space-between"
                align="center"
                p={3}
                mb={2}
                bg="base.750"
                borderRadius="md"
              >
                <Flex flexDir="column" gap={1}>
                  <Flex align="center" gap={2}>
                    <Text fontSize="lg">{displayInfo.icon}</Text>
                    <Text fontWeight="medium">{displayInfo.displayName}</Text>
                  </Flex>
                  <Text fontSize="xs" color="base.400">
                    {displayInfo.description}
                  </Text>
                  {!provider.is_configured && (
                    <Link href={displayInfo.setupInstructions} isExternal fontSize="xs" color="accent.400">
                      {t('settings.setupInstructions')} →
                    </Link>
                  )}
                </Flex>

                <ProviderStatusIndicator provider={provider} isLoading={isLoading} />
              </Flex>
            );
          })}
        </Box>

        {/* Help Text */}
        <Box>
          <Text fontSize="sm" color="base.400">
            {t('settings.cloudProvidersHelpText')}
          </Text>
          <Text fontSize="sm" color="base.400" mt={2}>
            {t('settings.cloudProvidersConfigNote')}
          </Text>
        </Box>
      </Flex>
    </StandaloneAccordion>
  );
});

CloudProviderSettingsPanel.displayName = 'CloudProviderSettingsPanel';
