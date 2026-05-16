<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import SignUpModal from '../components/SignUpModal.vue';
import InputReceivedModal from '../components/InputReceivedModal.vue';
import SettingModal from '../components/SettingModal.vue';
import apiClient from '../utils/api';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isSignUpModalOpen = ref(false);
const isInputModalOpen = ref(false);
const isSettingModalOpen = ref(false);
const isLoading = ref(true);

const peopleData = ref<any[]>([]);

onMounted(async () => {
  // 회원가입 모달 처리
  if (route.query.isNewUser === 'true') {
    isSignUpModalOpen.value = true;
    router.replace({ query: {} });
  }
  
  try {
    // 폼 목록 및 프로필 정보 로드
    await Promise.all([
      fetchForms(),
      authStore.isAuthenticated ? fetchUserProfile() : Promise.resolve()
    ]);
  } catch (error) {
    console.error('초기 데이터 로딩 에러:', error);
  } finally {
    // 자연스러운 전환을 위해 약간의 지연 후 로딩 해제
    setTimeout(() => {
      isLoading.value = false;
    }, 300);
  }
});

const fetchForms = async () => {
  try {
    const response = await apiClient.get('/form/list');
    if (response.data.success) {
      // targetName 기준으로 그룹화
      const grouped = response.data.forms.reduce((acc: any, form: any) => {
        if (!acc[form.targetName]) {
          acc[form.targetName] = {
            id: form.targetName,
            name: form.targetName,
            chatRooms: []
          };
        }
        acc[form.targetName].chatRooms.push(form);
        return acc;
      }, {});
      peopleData.value = Object.values(grouped);
    }
  } catch (error) {
    console.error('폼 목록 조회 에러:', error);
  }
};

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
    const response = await apiClient.post('/auth/register', data);
    if (response.data.success) {
      authStore.setAuthenticated(true);
      authStore.setIsRegistering(false);
      isSignUpModalOpen.value = false;
      await fetchUserProfile();
      await fetchForms();
    } else {
      alert(response.data.detail || '회원가입에 실패했습니다.');
    }
  } catch (error: any) {
    console.error('회원가입 에러:', error);
    alert(error.response?.data?.detail || '회원가입 중 오류가 발생했습니다.');
  }
};

const handleInputSubmit = async (data: any) => {
  try {
    const response = await apiClient.post('/history/new', data);
    if (response.data.success) {
      isInputModalOpen.value = false;
      await fetchForms(); // 목록 새로고침
    }
  } catch (error) {
    console.error('경조사 입력 에러:', error);
  }
};

const handleSettingSave = async (data: any) => {
  try {
    // SettingModal 내부에서 API 호출을 하므로 여기선 상태 갱신만 확인
    if (authStore.isAuthenticated) {
      await fetchUserProfile();
      await fetchForms();
    }
    isSettingModalOpen.value = false;
  } catch (error) {
    console.error('설정 저장 후 갱신 에러:', error);
  }
};

const goToChatList = (personId: string) => {
  router.push({
    name: 'chat-list',
    params: { personId },
  });
};
</script>

<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <SignUpModal :isOpen="isSignUpModalOpen" @submit="handleSignUpSubmit" />

    <InputReceivedModal
      :isOpen="isInputModalOpen"
      @submit="handleInputSubmit"
      @close="isInputModalOpen = false"
    />

    <SettingModal
      :isOpen="isSettingModalOpen"
      :currentSettings="{ 
        username: authStore.user?.username || '', 
        language: authStore.user?.language || 'ko' 
      }"
      @close="isSettingModalOpen = false"
      @save="handleSettingSave"
    />

    <!-- 로딩 상태 표시 -->
    <div v-if="isLoading" class="w-full max-w-md md:max-w-2xl lg:max-w-3xl flex flex-col items-center justify-center min-h-screen">
       <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
       <p class="text-slate-500 font-medium">데이터를 불러오는 중입니다...</p>
    </div>

    <div
      v-else
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

        <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            @click="router.push('/events/축하')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2 class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1">
                축하
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">결혼, 승진, 출산 등</p>
            </div>
            <div class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100">
              <font-awesome-icon icon="fa-solid fa-gift" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>

          <button
            @click="router.push('/events/위로')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2 class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1">
                위로
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">병문안 등 위로 상황</p>
            </div>
            <div class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100">
              <font-awesome-icon icon="fa-solid fa-bandage" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>
        </section>

        <section class="pt-2">
          <div class="text-xs md:text-sm font-bold text-slate-400 mb-3 px-1">
            최근 대화한 인물 목록
          </div>
          <div v-if="peopleData.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <button
              v-for="person in peopleData"
              :key="person.id"
              @click="goToChatList(person.id)"
              class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
            >
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 md:w-11 md:h-11 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs md:text-sm shadow-sm">
                  {{ person.name[0] }}
                </div>
                <div>
                  <h3 class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm md:text-base">
                    {{ person.name }}
                  </h3>
                  <p class="text-[11px] md:text-xs text-slate-400 mt-0.5">
                    진단 결과 {{ person.chatRooms.length }}개
                  </p>
                </div>
              </div>
              <div class="text-slate-300 group-hover:text-indigo-500 transition-colors">
                <font-awesome-icon icon="fa-solid fa-chevron-right" class="w-4 h-4" />
              </div>
            </button>
          </div>
          <div v-else class="text-center py-10 bg-slate-50/50 rounded-3xl border border-dashed border-slate-200">
            <p class="text-sm text-slate-400 font-medium">아직 대화 내역이 없습니다.</p>
          </div>
        </section>
      </div>

      <button
        @click="isInputModalOpen = true"
        class="absolute bottom-6 right-6 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-indigo-200 active:scale-95 transition-all z-40 group"
        aria-label="경조사 직접 입력"
      >
        <font-awesome-icon icon="fa-solid fa-plus" class="w-6 h-6 transition-transform group-hover:rotate-90" />
      </button>
    </div>
  </div>
</template>
