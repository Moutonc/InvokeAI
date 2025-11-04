/**
 * Cloud Model Registration Panel Component
 * Allows users to register new cloud models for use in workflows
 */

import {
  Box,
  Button,
  Flex,
  FormControl,
  FormHelperText,
  FormLabel,
  Input,
  Select,
  StandaloneAccordion,
  Text,
  Textarea,
  useToast,
} from '@invoke-ai/ui-library';
import { useStandaloneAccordionToggle } from 'features/settingsAccordions/hooks/useStandaloneAccordionToggle';
import type { ChangeEvent, FormEvent } from 'react';
import { memo, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { CloudProviderType } from 'services/api/endpoints/cloudModels';
import { useRegisterCloudModelMutation } from 'services/api/endpoints/cloudModels';

interface CloudModelOption {
  provider: CloudProviderType;
  model_id: string;
  name: string;
  description: string;
  source: string;
}

/**
 * Available cloud models that can be registered
 */
const AVAILABLE_MODELS: CloudModelOption[] = [
  {
    provider: 'google-gemini',
    model_id: 'gemini-2.5-flash-image',
    name: 'Gemini 2.5 Flash Image',
    description: 'Fast and affordable with 10 aspect ratios. $0.039 per image.',
    source: 'https://ai.google.dev/gemini-api/docs/image-generation',
  },
  {
    provider: 'google-imagen',
    model_id: 'imagen-4.0-ultra-generate-001',
    name: 'Imagen 4 Ultra',
    description: 'Premium quality with SynthID watermark. $0.06 per image.',
    source: 'https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview',
  },
  {
    provider: 'openai',
    model_id: 'dall-e-3',
    name: 'DALL-E 3',
    description: 'Latest OpenAI model with quality/style controls. $0.04-$0.12 per image.',
    source: 'https://platform.openai.com/docs/guides/images',
  },
  {
    provider: 'openai',
    model_id: 'dall-e-2',
    name: 'DALL-E 2',
    description: 'Affordable model for rapid iteration. $0.016-$0.020 per image.',
    source: 'https://platform.openai.com/docs/guides/images',
  },
];

export const CloudModelRegistrationPanel = memo(() => {
  const { t } = useTranslation();
  const toast = useToast();
  const { isOpen, onToggle } = useStandaloneAccordionToggle({
    id: 'cloudModelRegistration',
    defaultIsOpen: false,
  });

  // Form state
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [customName, setCustomName] = useState<string>('');
  const [customDescription, setCustomDescription] = useState<string>('');

  // RTK Query mutation
  const [registerModel, { isLoading }] = useRegisterCloudModelMutation();

  // Get the selected model details
  const getSelectedModelDetails = useCallback((): CloudModelOption | null => {
    if (!selectedModel) return null;
    return AVAILABLE_MODELS.find((m) => `${m.provider}:${m.model_id}` === selectedModel) || null;
  }, [selectedModel]);

  // Handlers
  const handleModelSelect = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSelectedModel(value);

    // Auto-fill name when model is selected
    if (value) {
      const model = AVAILABLE_MODELS.find((m) => `${m.provider}:${m.model_id}` === value);
      if (model && !customName) {
        setCustomName(model.name);
      }
    }
  }, [customName]);

  const handleNameChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setCustomName(e.target.value);
  }, []);

  const handleDescriptionChange = useCallback((e: ChangeEvent<HTMLTextAreaElement>) => {
    setCustomDescription(e.target.value);
  }, []);

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();

    const modelDetails = getSelectedModelDetails();
    if (!modelDetails) {
      toast({
        title: t('cloudModels.selectModel'),
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    if (!customName.trim()) {
      toast({
        title: t('cloudModels.nameRequired'),
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      await registerModel({
        name: customName.trim(),
        provider: modelDetails.provider,
        cloud_model_id: modelDetails.model_id,
        source: modelDetails.source,
        description: customDescription.trim() || null,
      }).unwrap();

      toast({
        title: t('cloudModels.registrationSuccess'),
        description: t('cloudModels.modelRegisteredMessage', { name: customName }),
        status: 'success',
        duration: 5000,
      });

      // Reset form
      setSelectedModel('');
      setCustomName('');
      setCustomDescription('');
    } catch (error) {
      const errorMessage = error && typeof error === 'object' && 'data' in error
        ? (error.data as { detail?: string }).detail || t('cloudModels.registrationFailed')
        : t('cloudModels.registrationFailed');

      toast({
        title: t('cloudModels.registrationFailed'),
        description: errorMessage,
        status: 'error',
        duration: 7000,
        isClosable: true,
      });
    }
  }, [getSelectedModelDetails, customName, customDescription, registerModel, toast, t]);

  const modelDetails = getSelectedModelDetails();

  return (
    <StandaloneAccordion
      label={t('settings.registerCloudModel')}
      isOpen={isOpen}
      onToggle={onToggle}
    >
      <Box as="form" onSubmit={handleSubmit}>
        <Flex direction="column" gap={4}>
          {/* Model Selection */}
          <FormControl isRequired>
            <FormLabel>{t('cloudModels.selectModel')}</FormLabel>
            <Select
              value={selectedModel}
              onChange={handleModelSelect}
              placeholder={t('cloudModels.chooseModel')}
            >
              {AVAILABLE_MODELS.map((model) => (
                <option key={`${model.provider}:${model.model_id}`} value={`${model.provider}:${model.model_id}`}>
                  {model.name} ({model.provider})
                </option>
              ))}
            </Select>
            {modelDetails && (
              <FormHelperText>
                {modelDetails.description}
              </FormHelperText>
            )}
          </FormControl>

          {/* Custom Name */}
          {selectedModel && (
            <>
              <FormControl isRequired>
                <FormLabel>{t('cloudModels.modelName')}</FormLabel>
                <Input
                  value={customName}
                  onChange={handleNameChange}
                  placeholder={t('cloudModels.modelNamePlaceholder')}
                />
                <FormHelperText>
                  {t('cloudModels.modelNameHelp')}
                </FormHelperText>
              </FormControl>

              {/* Custom Description */}
              <FormControl>
                <FormLabel>{t('cloudModels.description')}</FormLabel>
                <Textarea
                  value={customDescription}
                  onChange={handleDescriptionChange}
                  placeholder={t('cloudModels.descriptionPlaceholder')}
                  rows={3}
                />
                <FormHelperText>
                  {t('cloudModels.descriptionHelp')}
                </FormHelperText>
              </FormControl>

              {/* Provider Info */}
              <Box p={3} bg="base.750" borderRadius="md">
                <Text fontSize="sm" fontWeight="semibold" mb={1}>
                  {t('cloudModels.providerInfo')}
                </Text>
                <Text fontSize="xs" color="base.400">
                  {t('cloudModels.provider')}: {modelDetails?.provider}
                </Text>
                <Text fontSize="xs" color="base.400">
                  {t('cloudModels.modelId')}: {modelDetails?.model_id}
                </Text>
              </Box>

              {/* Submit Button */}
              <Button
                type="submit"
                colorScheme="accent"
                isLoading={isLoading}
                loadingText={t('cloudModels.registering')}
              >
                {t('cloudModels.registerModel')}
              </Button>
            </>
          )}

          {/* Help Text */}
          {!selectedModel && (
            <Box>
              <Text fontSize="sm" color="base.400">
                {t('cloudModels.registrationHelpText')}
              </Text>
            </Box>
          )}
        </Flex>
      </Box>
    </StandaloneAccordion>
  );
});

CloudModelRegistrationPanel.displayName = 'CloudModelRegistrationPanel';
