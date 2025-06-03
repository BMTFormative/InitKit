// frontend/src/components/Admin/EmailConfiguration.tsx
import { useEffect } from "react";
import {
  Button,
  Input,
  VStack,
  Alert,
  Heading,
  Flex,
  NumberInput,
  Link,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { type SubmitHandler, useForm, Controller } from "react-hook-form";
import useAuth from "@/hooks/useAuth";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { Field } from "../ui/field";
import { UserWithTenant, EmailConfig } from "@/types/tenant";
import { EmailConfigService } from "@/services/email-config-service";
import { SkeletonText } from "../ui/skeleton";
import { Checkbox } from "../ui/checkbox";

const EmailConfiguration = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  const { user } = useAuth();

  // Type assertion for user
  const typedUser = user as UserWithTenant | null;
  const tenantId = typedUser?.tenant_id ?? "";

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<EmailConfig>();

  const { data: emailConfig, isLoading } = useQuery({
    queryKey: ["email-config", tenantId],
    queryFn: () => EmailConfigService.getEmailConfig(tenantId),
    enabled: !!tenantId,
  });

  // Use useEffect instead of onSuccess for TanStack Query v5
  useEffect(() => {
    if (emailConfig) {
      reset(emailConfig);
    }
  }, [emailConfig, reset]);

  const saveConfigMutation = useMutation({
    mutationFn: (data: EmailConfig) =>
      EmailConfigService.saveEmailConfig({ tenantId, data }),
    onSuccess: () => {
      showSuccessToast("Email configuration saved successfully");
      queryClient.invalidateQueries({ queryKey: ["email-config"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const testEmailMutation = useMutation({
    mutationFn: () => EmailConfigService.testEmailConfig(tenantId),
    onSuccess: () => {
      showSuccessToast(
        "Test email sent successfully. Please check your inbox."
      );
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const onSubmit: SubmitHandler<EmailConfig> = (data) => {
    saveConfigMutation.mutate(data);
  };

  if (!tenantId) {
    return <Heading size="md">No tenant associated with your account</Heading>;
  }

  if (isLoading) {
    return <SkeletonText noOfLines={10} gap="4" />;
  }

  return (
    <VStack align="stretch" gap={6}>
      <Heading size="md">Email Configuration</Heading>

      <Alert.Root status="info">
        <Alert.Description>
          Configure SMTP settings to send invitation emails to your company
          members. These settings will be used only for your tenant's outgoing
          emails.
        </Alert.Description>
      </Alert.Root>

      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack gap={4} align="stretch">
          <Field
            label="SMTP Host"
            required
            invalid={!!errors.smtp_host}
            errorText={errors.smtp_host?.message}
          >
            <Input
              {...register("smtp_host", { required: "SMTP host is required" })}
              placeholder="smtp.gmail.com"
            />
          </Field>

          <Field
            label="SMTP Port"
            required
            invalid={!!errors.smtp_port}
            errorText={errors.smtp_port?.message}
          >
            <NumberInput.Root min={1} max={65535} defaultValue="587">
              <NumberInput.Input
                {...register("smtp_port", {
                  required: "SMTP port is required",
                  valueAsNumber: true,
                })}
              />
              <NumberInput.Control>
                <NumberInput.IncrementTrigger />
                <NumberInput.DecrementTrigger />
              </NumberInput.Control>
            </NumberInput.Root>
          </Field>

          <Field
            label="SMTP Username"
            required
            invalid={!!errors.smtp_user}
            errorText={errors.smtp_user?.message}
          >
            <Input
              {...register("smtp_user", {
                required: "SMTP username is required",
              })}
              placeholder="your_username@gmail.com"
            />
          </Field>

          <Field
            label="Gmail App Password"
            helperText={
              <Link
                href="https://support.google.com/mail/?p=BadCredentials"
                isExternal
                color="teal.500"
              >
                Learn how to create an App Password
              </Link>
            }
            required
            invalid={!!errors.smtp_password}
            errorText={errors.smtp_password?.message}
          >
            <Input
              type="password"
              {...register("smtp_password", {
                required: "Gmail App Password is required",
                minLength: {
                  value: 16,
                  message: "App Password should be 16 characters",
                },
                maxLength: {
                  value: 16,
                  message: "App Password should be 16 characters",
                },
              })}
              placeholder="Enter your 16-character App Password"
            />
          </Field>

          <Field>
            <Controller
              control={control}
              name="smtp_use_tls"
              defaultValue={true}
              render={({ field }) => (
                <Checkbox
                  checked={field.value}
                  onCheckedChange={({ checked }) => field.onChange(checked)}
                >
                  Use TLS
                </Checkbox>
              )}
            />
          </Field>

          <Field
            label="From Email Address"
            required
            invalid={!!errors.from_email}
            errorText={errors.from_email?.message}
          >
            <Input
              {...register("from_email", {
                required: "From email is required",
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Invalid email address",
                },
              })}
              placeholder="noreply@yourcompany.com"
            />
          </Field>

          <Field
            label="From Name"
            invalid={!!errors.from_name}
            errorText={errors.from_name?.message}
          >
            <Input {...register("from_name")} placeholder="Your Company Name" />
          </Field>

          <Flex justify="space-between" mt={4}>
            <Button
              variant="subtle"
              colorPalette="gray"
              onClick={() => testEmailMutation.mutate()}
              disabled={!emailConfig && !isDirty}
              loading={testEmailMutation.isPending}
            >
              Send Test Email
            </Button>
            <Button
              type="submit"
              colorPalette="teal"
              loading={isSubmitting || saveConfigMutation.isPending}
            >
              Save Configuration
            </Button>
          </Flex>
        </VStack>
      </form>
    </VStack>
  );
};

export default EmailConfiguration;
