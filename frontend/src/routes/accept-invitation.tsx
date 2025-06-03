// frontend/src/routes/accept-invitation.tsx
import {
  Container,
  Heading,
  Input,
  Text,
  VStack,
  Alert,
} from "@chakra-ui/react";
import { useMutation } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { type SubmitHandler, useForm } from "react-hook-form";
import { FiLock, FiUser } from "react-icons/fi";

import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { InputGroup } from "@/components/ui/input-group";
import { PasswordInput } from "@/components/ui/password-input";
import { emailPattern, passwordRules, confirmPasswordRules } from "@/utils";
import useCustomToast from "@/hooks/useCustomToast";
import { InvitationService } from "@/services/invitation-service";
import { AcceptInvitationInput } from "@/types/tenant";

export const Route = createFileRoute("/accept-invitation")({
  component: AcceptInvitation,
});

interface AcceptInvitationForm {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

function AcceptInvitation() {
  const navigate = useNavigate();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    getValues,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<AcceptInvitationForm>({
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      confirm_password: "",
    },
  });

  useEffect(() => {
    // Extract token from URL
    const params = new URLSearchParams(window.location.search);
    const tokenParam = params.get("token");
    
    if (!tokenParam) {
      setError("Invalid invitation link. Please request a new one.");
      return;
    }
    
    setToken(tokenParam);
    
    // Try to decode the token to get the email (this is a simplification)
    try {
      const parts = tokenParam.split(".");
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        const invitationEmail = payload.email ?? payload.eml;
        if (invitationEmail) {
          setValue("email", invitationEmail);
        }
      }
    } catch (e) {
      console.error("Failed to decode token", e);
    }
  }, [setValue]);

  const acceptInvitationMutation = useMutation({
    mutationFn: (data: AcceptInvitationInput) => {
      return InvitationService.acceptInvitation(data);
    },
    onSuccess: () => {
      showSuccessToast("Account created successfully! You can now log in.");
      navigate({ to: "/login" });
    },
    onError: (err: any) => {
      // Show API error detail if available
      const message = err?.body?.detail || err?.detail || "Failed to accept invitation";
      showErrorToast(message);
    },
  });

  const onSubmit: SubmitHandler<AcceptInvitationForm> = (data) => {
    if (!token) {
      setError("Invalid invitation token");
      return;
    }
    
    const invitationData: AcceptInvitationInput = {
      token,
      user_data: {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      }
    };
    
    acceptInvitationMutation.mutate(invitationData);
  };

  if (error) {
    return (
      <Container maxW="sm" centerContent mt={20}>
        <Alert.Root status="error">
          <Alert.Description>{error}</Alert.Description>
        </Alert.Root>
        <Button
          mt={4}
          colorPalette="teal"
          onClick={() => navigate({ to: "/login" })}
        >
          Go to Login
        </Button>
      </Container>
    );
  }

  return (
    <Container
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      maxW="sm"
      alignItems="stretch"
      justifyContent="center"
      gap={4}
      centerContent
      mt={20}
    >
      <VStack gap={6} align="center" w="100%">
        <Heading textAlign="center">Accept Invitation</Heading>
        <Text textAlign="center">
          Complete your registration to join the tenant organization.
        </Text>

        <Field
          invalid={!!errors.full_name}
          errorText={errors.full_name?.message}
          w="full"
        >
          <InputGroup w="100%" startElement={<FiUser />}>
            <Input
              id="full_name"
              {...register("full_name", {
                required: "Full name is required",
              })}
              placeholder="Full Name"
              type="text"
            />
          </InputGroup>
        </Field>

        <Field
          invalid={!!errors.email}
          errorText={errors.email?.message}
          w="full"
        >
          <InputGroup w="100%" startElement={<FiUser />}>
            <Input
              id="email"
              {...register("email", {
                required: "Email is required",
                pattern: emailPattern,
              })}
              placeholder="Email"
              type="email"
              disabled // Email is pre-filled from token
            />
          </InputGroup>
        </Field>

        <PasswordInput
          type="password"
          startElement={<FiLock />}
          {...register("password", passwordRules())}
          placeholder="Password"
          errors={errors}
        />

        <PasswordInput
          type="confirm_password"
          startElement={<FiLock />}
          {...register("confirm_password", confirmPasswordRules(getValues))}
          placeholder="Confirm Password"
          errors={errors}
        />

        <Button
          variant="solid"
          type="submit"
          loading={isSubmitting}
          width="full"
          colorPalette="teal"
        >
          Create Account
        </Button>
      </VStack>
    </Container>
  );
}

export default AcceptInvitation;