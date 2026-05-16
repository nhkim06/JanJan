<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md md:max-w-2xl lg:max-w-4xl bg-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <header class="flex items-center py-4 border-b border-slate-100 mb-6">
        <button
          @click="router.back()"
          class="mr-4 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
        >
          <font-awesome-icon
            icon="fa-solid fa-chevron-left"
            class="w-4 h-4"
          />
        </button>
        <h1 class="text-xl md:text-2xl font-extrabold text-slate-950">
          {{ personName }}님 관련 대화방
        </h1>
      </header>

      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="flex flex-col items-center justify-center h-64">
        <div class="w-10 h-10 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-3"></div>
        <p class="text-sm font-medium text-slate-400">대화 목록을 불러오는 중...</p>
      </div>

      <div
        v-else-if="chatRooms.length === 0"
        class="flex flex-col items-center justify-center h-64 text-slate-400"
      >
        <p class="text-sm md:text-base font-medium">진행 중인 대화방이 없습니다.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <button
          v-for="room in chatRooms"
          :key="room.roomId"
          @click="enterChatRoom(room.roomId)"
          class="w-full flex items-center justify-between p-5 bg-white rounded-2xl border border-slate-100 shadow-[0_8px_25px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left"
        >
          <div class="flex-1 min-w-0 pr-4">
            <div class="flex items-center justify-between mb-2">
              <span
                class="text-[10px] md:text-xs font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-600"
              >
                {{ room.type }}
              </span>
              <span class="text-[11px] md:text-xs text-slate-400 font-medium">{{
                room.lastTime
              }}</span>
            </div>
            <h4 class="font-bold text-slate-800 text-sm md:text-base truncate mb-0.5">
              {{ room.title }}
            </h4>
            <p class="text-xs md:text-sm text-slate-500 truncate font-medium">
              {{ room.lastMessage }}
            </p>
          </div>
          <div class="text-slate-300 group-hover:text-indigo-500 transition-colors">
            <font-awesome-icon
              icon="fa-solid fa-comment-dots"
              class="w-5 h-5 md:w-6 md:h-6"
            />
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

const personName = computed(() => route.params.personId); // Using personId as targetName
const chatRooms = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  await fetchChatRooms();
  isLoading.value = false;
});

const fetchChatRooms = async () => {
  try {
    const response = await apiClient.get('/form/list');
    if (response.data.success) {
      // Filter forms by targetName
      chatRooms.value = response.data.forms
        .filter(form => form.targetName === personName.value)
        .map(form => ({
          roomId: form.formId,
          type: form.cultureBase, // Or some other type if available
          title: `${form.targetName}님 관련 대화`,
          lastMessage: '대화 내용을 확인하세요',
          lastTime: new Date(form.updatedAt).toLocaleDateString(),
          category: '축하', // Default for now, should ideally come from form
          targetName: form.targetName,
          cultureBase: form.cultureBase
        }));
    }
  } catch (error) {
    console.error('채팅방 목록 조회 에러:', error);
  }
};

const enterChatRoom = (roomId) => {
  const room = chatRooms.value.find(r => r.roomId === roomId);
  if (room) {
    router.push({
      name: 'result',
      params: { category: room.category },
      query: { 
        targetName: room.targetName, 
        cultureBase: room.cultureBase,
        roomId: room.roomId
      }
    });
  }
};
</script>
