import { useState } from 'react';
import { VStack, Button, Text, Box, HStack,Field } from '@chakra-ui/react';
import { Input } from '@chakra-ui/react';
import { FiCreditCard, FiCalendar, FiLock } from 'react-icons/fi';
import { InputGroup } from '@/components/ui/input-group';

interface CreditCardFormProps {
  onSubmit: (paymentMethodId: string) => void;
  loading?: boolean;
}

export const CreditCardForm = ({ onSubmit, loading }: CreditCardFormProps) => {
  const [cardNumber, setCardNumber] = useState('');
  const [expMonth, setExpMonth] = useState('');
  const [expYear, setExpYear] = useState('');
  const [cvc, setCvc] = useState('');
  const [cardholder, setCardholder] = useState('');
  const [processing, setProcessing] = useState(false);

  // Format card number with spaces
  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCardNumber(e.target.value);
    if (formatted.length <= 19) { // 16 digits + 3 spaces
      setCardNumber(formatted);
    }
  };

  const handleExpMonthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    if (value.length <= 2) {
      setExpMonth(value);
    }
  };

  const handleExpYearChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    if (value.length <= 2) {
      setExpYear(value);
    }
  };

  const handleCvcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    if (value.length <= 3) {
      setCvc(value);
    }
  };

  const validateForm = () => {
    const cleanCardNumber = cardNumber.replace(/\s/g, '');
    return (
      cleanCardNumber.length >= 13 &&
      expMonth.length === 2 &&
      parseInt(expMonth) >= 1 &&
      parseInt(expMonth) <= 12 &&
      expYear.length === 2 &&
      cvc.length >= 3 &&
      cardholder.trim().length > 0
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setProcessing(true);
    
    try {
      // In a real implementation, you would integrate with Stripe Elements here
      // For now, simulate payment method creation
      const paymentMethodId = 'pm_mock_' + Date.now();
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      onSubmit(paymentMethodId);
    } catch (error) {
      console.error('Payment method creation failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="lg" bg="white" shadow="md" >
      <VStack gap={2} align="start" mb={6}>
        <Text fontSize="lg" fontWeight="semibold">
          Payment Information
        </Text>
        <Text fontSize="sm" color="gray.600">
          Your payment information is secure and encrypted
        </Text>
      </VStack>
      
      <form onSubmit={handleSubmit}>
        <VStack gap={4}>
          {/* Cardholder Name */}
          <Field.Root>
            <Field.Label>Cardholder Name</Field.Label>
            <Input
              placeholder="John Doe"
              value={cardholder}
              onChange={(e) => setCardholder(e.target.value)}
              required
            />
          </Field.Root>

          {/* Card Number */}
          <Field.Root>
            <Field.Label>Card Number</Field.Label>
            <InputGroup startElement={<FiCreditCard />}>
              <Input
                placeholder="1234 5678 9012 3456"
                value={cardNumber}
                onChange={handleCardNumberChange}
                required
              />
            </InputGroup>
          </Field.Root>

          {/* Expiry Date and CVC */}
          <HStack gap={4} width="100%">
            <Field.Root flex={1}>
              <Field.Label textStyle="xs">Expiry Month</Field.Label>
              <InputGroup startElement={<FiCalendar />}>
                <Input
                  placeholder="MM"
                  value={expMonth}
                  onChange={handleExpMonthChange}
                  required
                />
              </InputGroup>
            </Field.Root>

            <Field.Root flex={1}>
              <Field.Label textStyle="xs">Expiry Year</Field.Label>
              <Input
                placeholder="YY"
                value={expYear}
                onChange={handleExpYearChange}
                required
              />
            </Field.Root>

            <Field.Root flex={1}>
              <Field.Label textStyle="xs">CVC</Field.Label>
              <InputGroup startElement={<FiLock />}>
                <Input
                  placeholder="123"
                  value={cvc}
                  onChange={handleCvcChange}
                  required
                />
              </InputGroup>
            </Field.Root>
          </HStack>

          {/* Security Notice */}
          <Box p={3} bg="blue.50" borderRadius="md" width="100%">
            <Text fontSize="xs" color="blue.700">
              🔒 Your payment information is processed securely. We never store your card details.
            </Text>
          </Box>

          {/* Submit Button */}
          <Button
            type="submit"
            width="100%"
            colorPalette="teal"
            loading={processing || loading}
            disabled={!validateForm() || processing || loading}
            size="lg"
          >
            {processing ? 'Processing...' : 'Complete Signup'}
          </Button>
        </VStack>
      </form>
    </Box>
  );
};