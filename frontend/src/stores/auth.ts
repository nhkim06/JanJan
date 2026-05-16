import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
  const isRegistering = ref(false);

  const isAuthenticated = computed(() => !!token.value);

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  }

  function setIsRegistering(value: boolean) {
    isRegistering.value = value;
  }

  function setUser(newUser: any) {
    user.value = newUser;
    localStorage.setItem('user', JSON.stringify(newUser));
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  return {
    token,
    user,
    isAuthenticated,
    isRegistering,
    setToken,
    setIsRegistering,
    setUser,
    logout,
  };
});
