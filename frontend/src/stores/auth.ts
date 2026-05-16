import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const sessionAuthenticated = ref(
    localStorage.getItem('sessionAuthenticated') === 'true'
  );
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
  const isRegistering = ref(false);

  const isAuthenticated = computed(() => sessionAuthenticated.value);

  function setAuthenticated(value: boolean) {
    sessionAuthenticated.value = value;
    if (value) {
      localStorage.setItem('sessionAuthenticated', 'true');
    } else {
      localStorage.removeItem('sessionAuthenticated');
    }
  }

  function setIsRegistering(value: boolean) {
    isRegistering.value = value;
  }

  function setUser(newUser: any) {
    user.value = newUser;
    setAuthenticated(true);
    localStorage.setItem('user', JSON.stringify(newUser));
  }

  function logout() {
    setAuthenticated(false);
    user.value = null;
    localStorage.removeItem('user');
  }

  return {
    sessionAuthenticated,
    user,
    isAuthenticated,
    isRegistering,
    setAuthenticated,
    setIsRegistering,
    setUser,
    logout,
  };
});
