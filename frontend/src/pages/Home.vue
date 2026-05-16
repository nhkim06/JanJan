<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { peopleData } from '../data/mockData';
import SignUpModal from '../components/SignUpModal.vue';
import InputReceivedModal from '../components/InputReceivedModal.vue';
import SettingModal from '../components/SettingModal.vue';
import apiClient from '../utils/api';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isSignUpModalOpen = ref(false);
// 2. 경조사 입력 모달 상태 관리를 위한 ref 추가
const isInputModalOpen = ref(false);
const isSettingModalOpen = ref(false);

onMounted(() => {
  if (route.query.isNewUser === 'true') {
    isSignUpModalOpen.value = true;
    router.replace({ query: {} });
  }
  
  if (authStore.isAuthenticated) {
    fetchUserProfile();
  }
});

const fetchUserProfile = async () => {
  try {
    const response = await apiClient.get('/auth/profile');
    if (response.data.success) {
      authStore.setUser(response.data.user);
    }
  } catch (error) {
    console.error('프로필 조회 에러:', error);
  }
};

const handleSignUpSubmit = async (data: any) => {
  try {
    // data 에는 { id, name, language } 가 포함되어 있습니다.
    const response = await apiClient.post('/auth/register', data);
    
    if (response.data.success) {
      authStore.setAuthenticated(true);
      authStore.setIsRegistering(false);
      isSignUpModalOpen.value = false;
      fetchUserProfile();
    } else {
      alert(response.data.detail || '회원가입에 실패했습니다.');
    }
  } catch (error: any) {
    console.error('회원가입 에러:', error);
    const detail = error.response?.data?.detail || '회원가입 중 오류가 발생했습니다.';
    alert(detail);
  }
};

// 3. 경조사 입력 완료 시 처리할 핸들러 함수
const handleInputSubmit = (data) => {
  console.log('경조사 입력 데이터 제출:', data);
  // data 내부에는 경조사 종류, 날짜, 금액 등이 들어옵니다.
  isInputModalOpen.value = false;
};

const handleSettingSave = (data) => {
  console.log('설정 변경 데이터:', data);
  // 실제 저장 로직(localStorage 등)이 필요하면 여기에 추가
  isSettingModalOpen.value = false;
};

const goToChatList = (personId) => {
  router.push({
    name: 'chat-list',
    params: { personId },
  });
};
</script>

<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <SignUpModal :isOpen="isSignUpModalOpen" @submit="handleSignUpSubmit" />

    <!-- 4. 경조사 입력 모달 컴포넌트 배치 -->
    <InputReceivedModal
      :isOpen="isInputModalOpen"
      @submit="handleInputSubmit"
      @close="isInputModalOpen = false"
    />

    <!-- 설정 모달 컴포넌트 배치 -->
    <SettingModal
      :isOpen="isSettingModalOpen"
      :currentSettings="{ 
        name: authStore.user?.name || '', 
        language: authStore.user?.language || 'ko' 
      }"
      @close="isSettingModalOpen = false"
      @save="handleSettingSave"
    />

    <div
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <div class="flex flex-col h-full space-y-8">
        <button
          @click="isSettingModalOpen = true"
          class="absolute top-6 right-6 w-10 h-10 mt-3 hover:bg-slate-50 text-slate-500 hover:text-slate-700 rounded-xl flex items-center justify-center border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.02)] active:scale-95 transition-all z-40 group"
          aria-label="설정"
        >
          <font-awesome-icon
            icon="fa-solid fa-gear"
            class="w-5 h-5 transition-transform group-hover:rotate-45"
          />
        </button>

        <header class="md:text-center md:mb-4">
          <h1
            class="text-2xl md:text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight mb-2"
          >
            어떤 상황인가요?
          </h1>
          <p class="text-sm md:text-base font-medium text-slate-500/90">
            적정 축의금/부의금을 확인해보세요.
          </p>
        </header>

        <br class="hidden md:inline" />

        <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 축하 버튼 -->
          <button
            @click="router.push('/events/축하')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1"
              >
                축하
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">
                결혼, 승진, 출산 등
              </p>
            </div>
            <div
              class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100"
            >
              <font-awesome-icon
                icon="fa-solid fa-gift"
                class="w-6 h-6 md:w-8 md:h-8"
              />
            </div>
          </button>

          <!-- 위로 버튼 -->
          <button
            @click="router.push('/events/위로')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1"
              >
                위로
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">
                병문안 등 위로 상황
              </p>
            </div>
            <div
              class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100"
            >
              <font-awesome-icon
                icon="fa-solid fa-bandage"
                class="w-6 h-6 md:w-8 md:h-8"
              />
            </div>
          </button>
        </section>

        <section class="pt-2">
          <div class="text-xs md:text-sm font-bold text-slate-400 mb-3 px-1">
            최근 대화한 인물 목록
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <button
              v-for="person in peopleData"
              :key="person.id"
              @click="goToChatList(person.id)"
              class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
            >
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 md:w-11 md:h-11 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs md:text-sm shadow-sm"
                >
                  {{ person.name[0] }}
                </div>
                <div>
                  <h3
                    class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm md:text-base"
                  >
                    {{ person.name }}
                  </h3>
                  <p class="text-[11px] md:text-xs text-slate-400 mt-0.5">
                    진단 결과 {{ person.chatRooms.length }}개
                  </p>
                </div>
              </div>
              <div
                class="text-slate-300 group-hover:text-indigo-500 transition-colors"
              >
                <font-awesome-icon
                  icon="fa-solid fa-chevron-right"
                  class="w-4 h-4"
                />
              </div>
            </button>
          </div>
        </section>
      </div>

      <!-- 5. 오른쪽 하단 플러스 플로팅 버튼 -->
      <button
        @click="isInputModalOpen = true"
        class="absolute bottom-6 right-6 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-indigo-200 active:scale-95 transition-all z-40 group"
        aria-label="경조사 직접 입력"
      >
        <font-awesome-icon
          icon="fa-solid fa-plus"
          class="w-6 h-6 transition-transform group-hover:rotate-90"
        />
      </button>
    </div>
  </div>
</template>
