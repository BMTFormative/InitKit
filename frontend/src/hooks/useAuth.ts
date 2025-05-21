import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserRegister,
  UsersService,
} from "@/client";
import { handleError } from "@/utils";
import { UserWithTenant } from "@/types/tenant"; // Import our extended type

// Type for token payload
interface TokenData {
  sub: string;
  exp: number;
  tenant_id?: string;
  role?: string;
}

// Parse JWT without using atob (which can cause issues)
const parseJwt = (token: string): TokenData | null => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload) as TokenData;
  } catch (e) {
    return null;
  }
};

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null;
};

const useAuth = () => {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // Use the extended type here
  const { data: user } = useQuery<UserWithTenant | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const userData = await UsersService.readUserMe();
      
      // Get tenant_id and role from token if available
      const token = localStorage.getItem("access_token");
      if (token) {
        const tokenData = parseJwt(token);
        if (tokenData) {
          // Merge the token data with the user data
          return {
            ...userData,
            tenant_id: tokenData.tenant_id,
            role: tokenData.role || "user",
          };
        }
      }
      
      return userData;
    },
    enabled: isLoggedIn(),
  });
  
  // Fetch current user's credit balance
  const { data: creditBalance = 0 } = useQuery<number, Error>({
    queryKey: ["creditBalance"],
    queryFn: async () => {
      const token = localStorage.getItem("access_token");
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/users/me/credit-balance`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        }
      );
      if (!res.ok) {
        throw new Error("Failed to fetch credit balance");
      }
      const json = await res.json();
      return json.balance;
    },
    enabled: Boolean(user),
  });
  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),
    onSuccess: () => {
      navigate({ to: "/login" });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const login = async (data: AccessToken) => {
    try {
      const response = await LoginService.loginAccessToken({
        formData: data,
      });
      
      // Store token
      localStorage.setItem("access_token", response.access_token);
      
      // Parse token and store tenant_id and role if present
      const tokenData = parseJwt(response.access_token);
      if (tokenData) {
        if (tokenData.tenant_id) {
          localStorage.setItem("tenant_id", tokenData.tenant_id);
        }
        if (tokenData.role) {
          localStorage.setItem("role", tokenData.role);
        }
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("tenant_id");
    localStorage.removeItem("role");
    queryClient.invalidateQueries();
    navigate({ to: "/login" });
  };

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
    creditBalance,
    error,
    resetError: () => setError(null),
  };
};

export { isLoggedIn, useAuth };
export default useAuth;