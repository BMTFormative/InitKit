import {
  Container,
  Flex,
  Image,
  Input,
  Text,
  VStack,
  SimpleGrid,
  Card,
  Badge,
  Heading,
  Box,
} from "@chakra-ui/react";
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
  useNavigate,
} from "@tanstack/react-router";
import { type SubmitHandler, useForm } from "react-hook-form";
import { FiLock, FiUser } from "react-icons/fi";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";

import type { UserRegister } from "@/client";
import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { InputGroup } from "@/components/ui/input-group";
import { PasswordInput } from "@/components/ui/password-input";
import useAuth, { isLoggedIn } from "@/hooks/useAuth";
import { confirmPasswordRules, emailPattern, passwordRules } from "@/utils";
import Logo from "/assets/images/Logo.svg";
import { SubscriptionsService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { SkeletonText } from "@/components/ui/skeleton";
import { CreditCardForm } from "@/components/Payment/CreditCardForm";

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      });
    }
  },
});

interface UserRegisterForm extends UserRegister {
  confirm_password: string;
}

type SignupStep = "form" | "plans" | "payment";

function SignUp() {
  const navigate = useNavigate();
  const { signUpMutation } = useAuth();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<any>(null);
  const [step, setStep] = useState<SignupStep>("form");
  const [userFormData, setUserFormData] = useState<UserRegisterForm | null>(null);

  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserRegisterForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  });

  const { data: plans, isLoading: plansLoading } = useQuery({
    queryKey: ["subscription-plans"],
    queryFn: () =>
      SubscriptionsService.listSubscriptionPlans({ activeOnly: true }),
    enabled: step === "plans",
  });

  const subscribeWithPaymentMutation = useMutation({
    mutationFn: async ({
      planId,
      userCredentials,
      paymentMethodId,
    }: {
      planId: string;
      userCredentials: { email: string; password: string };
      paymentMethodId?: string;
    }) => {
      // First, authenticate the user
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/login/access-token`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: userCredentials.email,
            password: userCredentials.password,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to authenticate after signup");
      }

      const tokens = await response.json();
      const accessToken = tokens.access_token;

      // Now subscribe to the plan with optional payment method
      const subscriptionPayload: any = { plan_id: planId };
      if (paymentMethodId) {
        subscriptionPayload.payment_method_id = paymentMethodId;
      }

      const subscriptionResponse = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/subscriptions/subscribe`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(subscriptionPayload),
        }
      );

      if (!subscriptionResponse.ok) {
        const errorData = await subscriptionResponse.json();
        throw new Error(errorData.detail || "Failed to subscribe to plan");
      }

      return subscriptionResponse.json();
    },
  });

  const onFormSubmit: SubmitHandler<UserRegisterForm> = async (data) => {
    setUserFormData(data);
    setStep("plans");
  };

  const handlePlanSelect = (plan: any) => {
    setSelectedPlanId(plan.id);
    setSelectedPlan(plan);
    
    // If plan is free (price = 0), skip payment step
    if (plan.price === 0) {
      handleCompleteSignup();
    } else {
      // Go to payment step for paid plans
      setStep("payment");
    }
  };

  const handleCompleteSignup = async (paymentMethodId?: string) => {
    if (!userFormData || !selectedPlanId) return;

    try {
      // Create user account first
      await signUpMutation.mutateAsync(userFormData);
      
      // Subscribe to selected plan
      await subscribeWithPaymentMutation.mutateAsync({
        planId: selectedPlanId,
        userCredentials: {
          email: userFormData.email,
          password: userFormData.password,
        },
        paymentMethodId,
      });

      showSuccessToast(
        selectedPlan?.price > 0
          ? "Account created and subscription activated!"
          : "Account created successfully!"
      );
      navigate({ to: "/login" });
    } catch (error: any) {
      showErrorToast(error.message || "Failed to complete signup. Please try again.");
      console.error(error);
    }
  };

  const handlePaymentSubmit = (paymentMethodId: string) => {
    handleCompleteSignup(paymentMethodId);
  };

  const handleBack = () => {
    if (step === "payment") {
      setStep("plans");
    } else if (step === "plans") {
      setStep("form");
    }
  };

  const handleSkipPlan = async () => {
    if (!userFormData) return;

    try {
      await signUpMutation.mutateAsync(userFormData);
      showSuccessToast("Account created successfully!");
      navigate({ to: "/login" });
    } catch (error) {
      showErrorToast("Failed to create account. Please try again.");
      console.error(error);
    }
  };

  return (
    <Flex
      flexDir={{ base: "column", md: "row" }}
      justify="center"
      minH="100vh"
      py={8}
    >
      <Container maxW={step === "plans" ? "4xl" : "sm"} h="100%">
        {step === "form" && (
          <form onSubmit={handleSubmit(onFormSubmit)}>
            <VStack gap={4} align="center">
              <Image
                src={Logo}
                alt="FastAPI logo"
                height="auto"
                maxW="2xs"
                alignSelf="center"
                mb={4}
              />
              <Heading size="lg" mb={2}>
                Create an Account
              </Heading>

              <Field
                invalid={!!errors.full_name}
                errorText={errors.full_name?.message}
                w="full"
              >
                <InputGroup w="100%" startElement={<FiUser />}>
                  <Input
                    id="full_name"
                    minLength={3}
                    {...register("full_name", {
                      required: "Full Name is required",
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
                {...register(
                  "confirm_password",
                  confirmPasswordRules(getValues)
                )}
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
                Next: Choose a Plan
              </Button>
              
              <Text>
                Already have an account?{" "}
                <RouterLink to="/login" className="main-link">
                  Log In
                </RouterLink>
              </Text>
            </VStack>
          </form>
        )}

        {step === "plans" && (
          <VStack gap={6} align="stretch">
            <Heading size="lg" textAlign="center">
              Choose Your Plan
            </Heading>
            <Text textAlign="center" color="gray.500">
              Select a subscription plan for your account
            </Text>

            {plansLoading ? (
              <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
                {[1, 2, 3].map((i) => (
                  <Card.Root key={i}>
                    <Card.Body>
                      <SkeletonText noOfLines={10} />
                    </Card.Body>
                  </Card.Root>
                ))}
              </SimpleGrid>
            ) : (
              <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
                {plans?.data.map((plan) => (
                  <Card.Root
                    key={plan.id}
                    borderWidth={selectedPlanId === plan.id ? "2px" : "1px"}
                    borderColor={
                      selectedPlanId === plan.id ? "teal.500" : "gray.200"
                    }
                    cursor="pointer"
                    onClick={() => handlePlanSelect(plan)}
                    transition="all 0.2s"
                    _hover={{ borderColor: "teal.400" }}
                  >
                    <Card.Header>
                      <VStack align="start" gap={2}>
                        <Flex justify="space-between" align="center" w="full">
                          <Text fontSize="xl" fontWeight="bold">
                            {plan.name}
                          </Text>
                          {plan.price === 0 && (
                            <Badge colorPalette="green">FREE</Badge>
                          )}
                        </Flex>
                        <Text
                          fontSize="3xl"
                          fontWeight="bold"
                          color="teal.500"
                        >
                          ${plan.price}
                          <Text as="span" fontSize="sm" color="gray.500">
                            /{plan.duration_days} days
                          </Text>
                        </Text>
                        <Text fontSize="md" color="gray.600">
                          Credits per user: {plan.credit_limit}
                        </Text>
                      </VStack>
                    </Card.Header>

                    <Card.Body>
                      <VStack align="stretch" gap={4}>
                        <Text>{plan.description}</Text>

                        {plan.features && plan.features.length > 0 && (
                          <VStack align="start">
                            {plan.features.map((feature, index) => (
                              <Text key={index}>• {feature}</Text>
                            ))}
                          </VStack>
                        )}
                      </VStack>
                    </Card.Body>

                    <Card.Footer>
                      <Button
                        width="full"
                        colorPalette={plan.price === 0 ? "green" : "teal"}
                        variant={selectedPlanId === plan.id ? "solid" : "outline"}
                      >
                        {plan.price === 0 ? "Start Free" : "Select Plan"}
                      </Button>
                    </Card.Footer>
                  </Card.Root>
                ))}
              </SimpleGrid>
            )}

            <Flex gap={4} justify="center" mt={6}>
              <Button
                variant="subtle"
                onClick={handleBack}
                disabled={isSubmitting}
              >
                Back
              </Button>
            </Flex>

            <Text textAlign="center" fontSize="sm" color="gray.500">
              Or{" "}
              <Button
                variant="ghost"
                size="sm"
                colorPalette="teal"
                onClick={handleSkipPlan}
                ml={1}
                loading={signUpMutation.isPending}
                _hover={{ textDecoration: "underline" }}
              >
                continue without a subscription
              </Button>
            </Text>
          </VStack>
        )}

        {step === "payment" && selectedPlan && (
          <VStack gap={6} align="stretch">
            <Heading size="lg" textAlign="center">
              Payment Information
            </Heading>
            
            <Box p={4} bg="gray.50" borderRadius="md">
              <Text fontWeight="semibold">Selected Plan: {selectedPlan.name}</Text>
              <Text color="gray.600">
                ${selectedPlan.price} for {selectedPlan.duration_days} days
              </Text>
            </Box>

            <CreditCardForm
              onSubmit={handlePaymentSubmit}
              loading={subscribeWithPaymentMutation.isPending || signUpMutation.isPending}
            />

            <Button
              variant="subtle"
              onClick={handleBack}
              disabled={subscribeWithPaymentMutation.isPending || signUpMutation.isPending}
            >
              Back to Plans
            </Button>
          </VStack>
        )}
      </Container>
    </Flex>
  );
}

export default SignUp;