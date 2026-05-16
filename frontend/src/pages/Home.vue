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

const fetchFormsAndHistories = async () => {
  try {
    const [formsRes, historiesRes] = await Promise.all([
      apiClient.get('/form/list'),
      apiClient.get('/history/list')
    ]);

    const grouped: Record<string, any> = {};

    // 1. 폼 데이터 가공
    if (formsRes.data.success) {
      formsRes.data.forms.forEach((form: any) => {
        const name = form.targetName;
        if (!grouped[name]) {
          grouped[name] = { id: name, name: name, itemsCount: 0, chatRooms: [] };
        }
        grouped[name].itemsCount++;
      });
    }

    // 2. 히스토리 데이터 가공
    if (historiesRes.data.success) {
      historiesRes.data.histories.forEach((h: any) => {
        const name = h.targetName; // Serializer returns targetName
        if (!grouped[name]) {
          grouped[name] = { id: name, name: name, itemsCount: 0, chatRooms: [] };
        }
        grouped[name].itemsCount++;
      });
    }

    peopleData.value = Object.values(grouped);
  } catch (error) {
    console.error('데이터 로드 에러:', error);
  }
};

onMounted(async () => {
  if (route.query.isNewUser === 'true') {
    isSignUpModalOpen.value = true;
    router.replace({ query: {} });
  }
  
  try {
    await Promise.all([
      fetchFormsAndHistories(),
      authStore.isAuthenticated ? fetchUserProfile() : Promise.resolve()
    ]);
  } finally {
    setTimeout(() => { isLoading.value = false; }, 300);
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
    const response = await apiClient.post('/auth/register', data);
    if (response.data.success) {
      authStore.setAuthenticated(true);
      authStore.setIsRegistering(false);
      isSignUpModalOpen.value = false;
      await fetchUserProfile();
      await fetchFormsAndHistories();
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
      await fetchFormsAndHistories(); // 목록 새로고침
    }
  } catch (error) {
    console.error('경조사 입력 에러:', error);
  }
};

const handleSettingSave = async (data: any) => {
  try {
    if (authStore.isAuthenticated) {
      await fetchUserProfile();
      await fetchFormsAndHistories();
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

    <div v-if="isLoading" class="w-full max-w-md md:max-w-2xl lg:max-w-3xl flex flex-col items-center justify-center min-h-screen">
       <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
       <p class="text-slate-500 font-medium">Loading data...</p>
    </div>

    <div
      v-else
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <div class="flex flex-col h-full space-y-8">
        <button
          @click="isSettingModalOpen = true"
          class="absolute top-6 right-6 w-10 h-10 mt-3 hover:bg-slate-50 text-slate-500 hover:text-slate-700 rounded-xl flex items-center justify-center border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.02)] active:scale-95 transition-all z-40 group"
          aria-label="Settings"
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
            How can I help you?
          </h1>
          <p class="text-sm md:text-base font-medium text-slate-500/90">
            Check the appropriate etiquette and gift amounts.
          </p>
        </header>

        <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            @click="router.push('/events/Celebration')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2 class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1">
                Celebration
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">Wedding, Promotion, Birth, etc.</p>
            </div>
            <div class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100">
              <font-awesome-icon icon="fa-solid fa-gift" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>

          <button
            @click="router.push('/events/Condolence')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2 class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1">
                Condolence
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">Hospital visit, Funeral, etc.</p>
            </div>
            <div class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100">
              <font-awesome-icon icon="fa-solid fa-bandage" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>
        </section>

        <section class="pt-2">
          <div class="text-xs md:text-sm font-bold text-slate-400 mb-3 px-1">
            Recent Interactions
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
                  {{ person.name ? person.name[0] : '?' }}
                </div>
                <div>
                  <h3 class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm md:text-base">
                    {{ person.name }}
                  </h3>
                  <p class="text-[11px] md:text-xs text-slate-400 mt-0.5">
                    {{ person.itemsCount }} records
                  </p>
                </div>
              </div>
              <div class="text-slate-300 group-hover:text-indigo-500 transition-colors">
                <font-awesome-icon icon="fa-solid fa-chevron-right" class="w-4 h-4" />
              </div>
            </button>
          </div>
          <div v-else class="text-center py-10 bg-slate-50/50 rounded-3xl border border-dashed border-slate-200">
            <p class="text-sm text-slate-400 font-medium">No history yet.</p>
          </div>
        </section>
      </div>

      <button
        @click="isInputModalOpen = true"
        class="absolute bottom-6 right-6 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-indigo-200 active:scale-95 transition-all z-40 group"
        aria-label="Add record"
      >
        <font-awesome-icon icon="fa-solid fa-plus" class="w-6 h-6 transition-transform group-hover:rotate-90" />
      </button>
    </div>
  </div>
</template>
