<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-all duration-300"
  >
    <div
      class="bg-white rounded-[32px] w-full max-w-md overflow-hidden shadow-2xl transform transition-all duration-300 scale-100 opacity-100"
    >
      <div class="px-8 pt-10 pb-8 flex flex-col items-center">
        <!-- 아이콘 -->
        <div
          class="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 mb-6"
        >
          <font-awesome-icon icon="fa-solid fa-face-smile" class="w-8 h-8" />
        </div>

        <!-- 텍스트 다국어 적용 -->
        <h2 class="text-2xl font-bold text-slate-900 mb-2">
          {{ i18n.title }}
        </h2>
        <p class="text-sm font-medium text-slate-500 text-center mb-8">
          {{ i18n.description }}
        </p>

        <div class="w-full space-y-6">
          <!-- 아이디 입력 -->
          <div class="space-y-2">
            <label class="text-xs font-bold text-slate-400 ml-1">
              {{ i18n.idLabel }}
            </label>
            <input
              v-model="formData.id"
              type="text"
              :placeholder="i18n.idPlaceholder"
              class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 px-5 text-base font-bold text-slate-800 placeholder-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all"
            />
          </div>

          <!-- 이름 입력 -->
          <div class="space-y-2">
            <label class="text-xs font-bold text-slate-400 ml-1">
              {{ i18n.nameLabel }}
            </label>
            <input
              v-model="formData.name"
              type="text"
              :placeholder="i18n.placeholder"
              class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 px-5 text-base font-bold text-slate-800 placeholder-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all"
            />
          </div>

          <!-- 언어 선택 -->
          <div class="space-y-2">
            <label class="text-xs font-bold text-slate-400 ml-1">
              {{ i18n.langLabel }}
            </label>
            <!-- 3개 국어가 한 줄에 균등하게 배치되도록 grid-cols-3으로 변경 -->
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="lang in languages"
                :key="lang.code"
                @click="formData.language = lang.code"
                :class="[
                  'py-4 rounded-2xl font-bold text-sm transition-all border',
                  formData.language === lang.code
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-200'
                    : 'bg-white text-slate-600 border-slate-100 hover:border-slate-200',
                ]"
              >
                {{ lang.label }}
              </button>
            </div>
          </div>
        </div>

        <button
          @click="handleSubmit"
          :disabled="!isFormValid"
          :class="[
            'w-full mt-10 py-4 rounded-2xl font-bold text-lg shadow-lg transition-all active:scale-[0.98]',
            isFormValid
              ? 'bg-indigo-600 text-white shadow-indigo-600/20'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none',
          ]"
        >
          {{ i18n.submitBtn }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['submit']);

const formData = ref({
  id: '',
  name: '',
  language: 'ko',
});

// 영어(English) 옵션 추가
const languages = [
  { code: 'ko', label: '한국어' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' },
];

// 다국어 텍스트 사전 정의 (영어 추가)
const contentText = {
  ko: {
    title: '환영합니다!',
    description: '서비스 이용을 위해 기본 정보를 입력해주세요.',
    idLabel: '아이디',
    idPlaceholder: '아이디를 입력해주세요',
    nameLabel: '이름',
    placeholder: '이름을 입력해주세요',
    langLabel: '선호 언어',
    submitBtn: '시작하기',
  },
  en: {
    title: 'Welcome!',
    description: 'Please enter your basic profile details to get started.',
    idLabel: 'ID',
    idPlaceholder: 'Enter your ID',
    nameLabel: 'Name',
    placeholder: 'Enter your name',
    langLabel: 'Preferred Language',
    submitBtn: 'Get Started',
  },
  ja: {
    title: 'ようこそ！',
    description: 'サービスをご利用いただくために、基本情報を 입력해주세요.',
    idLabel: 'ID',
    idPlaceholder: 'IDを入力してください',
    nameLabel: '名前',
    placeholder: '名前を入力してください',
    langLabel: '希望言語',
    submitBtn: '始める',
  },
};

// 현재 선택된 언어에 맞는 텍스트를 실시간 반환
const i18n = computed(() => {
  return contentText[formData.value.language] || contentText.ko;
});

const isFormValid = computed(() => {
  return (
    formData.value.id.trim().length > 0 &&
    formData.value.name.trim().length > 0 &&
    formData.value.language
  );
});

const handleSubmit = () => {
  if (isFormValid.value) {
    emit('submit', { ...formData.value });
  }
};
</script>

<style scoped>
/* 추가 스타일이 필요한 경우 작성 */
</style>
