<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-all duration-300"
  >
    <div
      class="bg-white rounded-[32px] w-full max-w-md overflow-hidden shadow-2xl transform transition-all duration-300 scale-100 opacity-100"
    >
      <!-- 헤더 영역 -->
      <div
        class="px-6 pt-6 pb-4 flex items-center justify-between border-b border-slate-50"
      >
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

      <!-- 본문 영역 -->
      <div class="px-8 py-6 flex flex-col space-y-6">
        <!-- 1. 이름 변경 섹션 -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 ml-1">
            {{ i18n.nameLabel }}
          </label>
          <input
            v-model="localData.name"
            type="text"
            :placeholder="i18n.namePlaceholder"
            class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 px-5 text-base font-bold text-slate-800 placeholder-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all"
          />
        </div>

        <!-- 2. 언어 설정 변경 섹션 -->
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

      <!-- 하단 버튼 영역 -->
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
          로그아웃
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
    name: string;
    language: string;
  };
}>();

const emit = defineEmits(['close', 'save']);

// 모달 내부에서 임시로 변경 사항을 들고 있을 반응형 데이터
const localData = ref({
  name: '',
  language: 'ko',
});

// 모달이 열릴 때 부모의 데이터를 받아와 동기화
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
  { code: 'ko', label: '한국어' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' },
];

// 설정 창 내부에서 즉각 반영될 다국어 사전
const contentText: Record<string, any> = {
  ko: {
    settingTitle: '환경 설정',
    nameLabel: '이름 변경',
    namePlaceholder: '이름을 입력해주세요',
    langLabel: '언어 설정 변경',
    saveBtn: '변경사항 저장',
  },
  en: {
    settingTitle: 'Settings',
    nameLabel: 'Change Name',
    namePlaceholder: 'Enter your name',
    langLabel: 'Change Language',
    saveBtn: 'Save Changes',
  },
  ja: {
    settingTitle: '環境設定',
    nameLabel: '名前의 변경',
    namePlaceholder: '名前を入力してください',
    langLabel: '言語設定の変更',
    saveBtn: '変更を保存',
  },
};

// 현재 임시 선택된 언어에 맞춰 모달의 텍스트 실시간 반영
const i18n = computed(() => {
  return contentText[localData.value.language] || contentText.ko;
});

// 빈 이름 저장 방지 검증
const isFormValid = computed(() => {
  return localData.value.name.trim().length > 0 && !!localData.value.language;
});

const handleClose = () => {
  emit('close');
};

const handleSave = async () => {
  if (isFormValid.value) {
    try {
      const response = await apiClient.post('/auth/profile', {
        name: localData.value.name,
        language: localData.value.language,
      });
      if (response.data.success) {
        emit('save', { ...localData.value });
        emit('close');
      } else {
        alert(response.data.detail || '설정 저장에 실패했습니다.');
      }
    } catch (error: any) {
      console.error('설정 저장 에러:', error);
      alert(error.response?.data?.detail || '오류가 발생했습니다.');
    }
  }
};

const handleLogout = async () => {
  try {
    await apiClient.post('/auth/logout');
    authStore.logout();
    window.location.href = '/login';
  } catch (error) {
    console.error('로그아웃 에러:', error);
    // 에러가 나도 로컬에서는 로그아웃 처리
    authStore.logout();
    window.location.href = '/login';
  }
};
</script>

<style scoped>
/* 필요한 스타일 커스텀이 있다면 이곳에 작성 */
</style>
