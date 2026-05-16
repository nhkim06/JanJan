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

      <div
        v-if="chatRooms.length === 0"
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
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { peopleData } from '../data/mockData';

const route = useRoute();
const router = useRouter();

const personId = computed(() => parseInt(route.params.personId));
const person = computed(() => peopleData.find(p => p.id === personId.value));

const personName = computed(() => person.value ? person.value.name : '알 수 없음');
const chatRooms = computed(() => person.value ? person.value.chatRooms : []);

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
