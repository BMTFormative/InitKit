interface PaymentMethod {
  id: string;
  card_last_four: string;
  card_brand: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
  created_at: string;
}

interface PaymentMethodCreate {
  stripe_payment_method_id: string;
}

export const PaymentService = {
  createPaymentMethod: async (data: PaymentMethodCreate): Promise<PaymentMethod> =>
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/payment/payment-methods`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),

  listPaymentMethods: async (): Promise<PaymentMethod[]> =>
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/payment/payment-methods`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),

  subscribeWithPayment: async (planId: string, paymentMethodId?: string): Promise<any> =>
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/subscriptions/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        plan_id: planId,
        payment_method_id: paymentMethodId
      })
    }).then(res => res.json()),
};