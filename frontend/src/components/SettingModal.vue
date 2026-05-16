<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-all duration-300"
  >
    <div
      class="bg-white rounded-[32px] w-full max-w-md overflow-hidden shadow-2xl transform transition-all duration-300 scale-100 opacity-100"
    >
      <!-- Header -->
      <div class="px-6 pt-6 pb-4 flex items-center justify-between border-b border-slate-50">
        <h2 class="text-xl font-bold text-slate-900 ml-2">
          {{ i18n.settingTitle }}
        </h2>
        <button
          @click="handleClose"
          class="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-all"
        >
          <font-awesome-icon icon="fa-solid fa-xmark" class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="px-8 py-6 flex flex-col space-y-6">
        <!-- ID Change Section -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 ml-1">
            {{ i18n.usernameLabel }}
          </label>
          <input
            v-model="localData.username"
            type="text"
            :placeholder="i18n.usernamePlaceholder"
            class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 px-5 text-base font-bold text-slate-800 placeholder-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all"
          />
        </div>

        <!-- Language Change Section -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 ml-1">
            {{ i18n.langLabel }}
          </label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="lang in languages"
              :key="lang.code"
              @click="localData.language = lang.code"
              :class="[
                'py-3.5 rounded-2xl font-bold text-sm transition-all border',
                localData.language === lang.code
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-200'
                  : 'bg-white text-slate-600 border-slate-100 hover:border-slate-200',
              ]"
            >
              {{ lang.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div class="px-8 pb-8 pt-2 space-y-3">
        <button
          @click="handleSave"
          :disabled="!isFormValid"
          :class="[
            'w-full py-4 rounded-2xl font-bold text-lg shadow-lg transition-all active:scale-[0.98]',
            isFormValid
              ? 'bg-indigo-600 text-white shadow-indigo-600/20 hover:bg-indigo-700'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none',
          ]"
        >
          {{ i18n.saveBtn }}
        </button>
        <button
          @click="handleLogout"
          class="w-full py-4 rounded-2xl font-bold text-lg text-rose-600 bg-rose-50 hover:bg-rose-100 transition-all active:scale-[0.98]"
        >
          {{ i18n.logoutBtn }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import apiClient from '../utils/api';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const props = defineProps<{
  isOpen: boolean;
  currentSettings: {
    username: string;
    language: string;
  };
}>();

const emit = defineEmits(['close', 'save']);

const localData = ref({
  username: '',
  language: 'en',
});

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      localData.value = { ...props.currentSettings };
    }
  },
  { immediate: true },
);

const languages = [
  { code: 'en', label: 'English' },
  { code: 'ko', label: '한국어' },
  { code: 'ja', label: '日本語' },
];

const contentText: Record<string, any> = {
  en: {
    settingTitle: 'Settings',
    usernameLabel: 'Change ID',
    usernamePlaceholder: 'Enter your ID',
    langLabel: 'Change Language',
    saveBtn: 'Save Changes',
    logoutBtn: 'Log Out',
  },
  ko: {
    settingTitle: '환경 설정',
    usernameLabel: '아이디 변경',
    usernamePlaceholder: '아이디를 입력해주세요',
    langLabel: '언어 설정 변경',
    saveBtn: '변경사항 저장',
    logoutBtn: '로그아웃',
  },
  ja: {
    settingTitle: '環境設定',
    usernameLabel: 'IDの変更',
    usernamePlaceholder: 'IDを入力してください',
    langLabel: '言語設定の変更',
    saveBtn: '変更を保存',
    logoutBtn: 'ログアウト',
  },
};

const i18n = computed(() => {
  return contentText[localData.value.language] || contentText.en;
});

const isFormValid = computed(() => {
  return localData.value.username.trim().length > 0 && !!localData.value.language;
});

const handleClose = () => {
  emit('close');
};

const handleSave = async () => {
  if (isFormValid.value) {
    try {
      const response = await apiClient.post('/auth/profile', {
        username: localData.value.username,
        language: localData.value.language,
      });
      if (response.data.success) {
        emit('save', { ...localData.value });
        emit('close');
      } else {
        alert(response.data.detail || 'Failed to save settings.');
      }
    } catch (error: any) {
      console.error('Settings save error:', error);
      alert(error.response?.data?.detail || 'An error occurred.');
    }
  }
};

const handleLogout = async () => {
  try {
    await apiClient.post('/auth/logout');
    authStore.logout();
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout error:', error);
    authStore.logout();
    window.location.href = '/login';
  }
};
</script>
