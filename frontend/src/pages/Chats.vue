<template>
  <div class="flex justify-center bg-gray-50 min-h-screen pb-20">
    <div
      class="w-full max-w-md bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <div v-if="!selectedPerson" class="flex flex-col h-full space-y-6">
        <header>
          <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight mb-2">
            채팅
          </h1>
          <p class="text-sm font-medium text-slate-500/90">
            최근 대화한 인물 목록입니다.
          </p>
        </header>

        <section class="space-y-3">
          <button
            v-for="person in peopleData"
            :key="person.id"
            @click="selectedPerson = person"
            class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
          >
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs shadow-sm"
              >
                {{ person.name[0] }}
              </div>
              <div>
                <h3
                  class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm"
                >
                  {{ person.name }}
                </h3>
                <p class="text-[11px] text-slate-400 mt-0.5">
                  참여 대화방 {{ person.chatRooms.length }}개
                </p>
              </div>
            </div>
            <div class="text-slate-300 group-hover:text-indigo-500 transition-colors">
              <font-awesome-icon icon="comment" class="w-4 h-4" />
            </div>
          </button>
        </section>
      </div>

      <div v-else class="flex flex-col h-full space-y-4">
        <header class="flex items-center py-2 border-b border-slate-100">
          <button
            @click="selectedPerson = null"
            class="mr-3 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-8 h-8 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
          >
            <font-awesome-icon icon="house" class="w-3 h-3" />
          </button>
          <h1 class="text-xl font-extrabold text-slate-950">
            {{ selectedPerson.name }}님 대화방
          </h1>
        </header>

        <div
          v-if="selectedPerson.chatRooms.length === 0"
          class="flex flex-col items-center justify-center h-64 text-slate-400"
        >
          <p class="text-sm font-medium">진행 중인 대화방이 없습니다.</p>
        </div>

        <div v-else class="space-y-3 pt-2">
          <button
            v-for="room in selectedPerson.chatRooms"
            :key="room.roomId"
            @click="enterChatRoom(room.roomId)"
            class="w-full flex items-center justify-between p-5 bg-white rounded-2xl border border-slate-100 shadow-[0_8px_25px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left"
          >
            <div class="flex-1 min-w-0 pr-4">
              <div class="flex items-center justify-between mb-2">
                <span
                  class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-600"
                >
                  {{ room.type }}
                </span>
                <span class="text-[11px] text-slate-400 font-medium">{{
                  room.lastTime
                }}</span>
              </div>
              <h4 class="font-bold text-slate-800 text-sm truncate mb-0.5">
                {{ room.title }}
              </h4>
              <p class="text-xs text-slate-500 truncate font-medium">
                {{ room.lastMessage }}
              </p>
            </div>
            <div class="text-slate-300">
              <font-awesome-icon icon="comment" class="w-5 h-5" />
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 하단 네비게이션 바 -->
    <footer
      class="fixed bottom-0 w-full max-w-md bg-white border-t border-slate-100 flex justify-around py-3 px-2 z-50 shadow-[0_-5px_20px_rgb(0,0,0,0.02)]"
    >
      <router-link to="/" class="flex flex-col items-center text-slate-300 hover:text-indigo-500 transition-colors" active-class="!text-indigo-600">
        <font-awesome-icon icon="user" class="w-5 h-5 mb-1" />
        <span class="text-[10px] font-bold">친구</span>
      </router-link>

      <router-link to="/chats" class="flex flex-col items-center text-slate-300 hover:text-indigo-500 transition-colors" active-class="!text-indigo-600">
        <font-awesome-icon icon="comment" class="w-5 h-5 mb-1" />
        <span class="text-[10px] font-bold">채팅</span>
      </router-link>

      <router-link to="/" class="flex flex-col items-center text-slate-300 hover:text-indigo-500 transition-colors" active-class="!text-indigo-600">
        <font-awesome-icon icon="house" class="w-5 h-5 mb-1" />
        <span class="text-[10px] font-bold">홈</span>
      </router-link>

      <router-link to="/forms" class="flex flex-col items-center text-slate-300 hover:text-indigo-500 transition-colors" active-class="!text-indigo-600">
        <font-awesome-icon icon="file-lines" class="w-5 h-5 mb-1" />
        <span class="text-[10px] font-bold">기록</span>
      </router-link>

      <router-link to="/login" class="flex flex-col items-center text-slate-300 hover:text-indigo-500 transition-colors" active-class="!text-indigo-600">
        <font-awesome-icon icon="ellipsis" class="w-5 h-5 mb-1" />
        <span class="text-[10px] font-bold">더보기</span>
      </router-link>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedPerson = ref(null);

const peopleData = ref([
  {
    id: 1,
    name: '김철수',
    chatRooms: [
      {
        roomId: 101,
        type: '축하',
        title: '철수형 결혼 축의금 의논방',
        lastMessage: '축의금 10만원 정도가 적당할까?',
        lastTime: '방금 전',
      },
      {
        roomId: 102,
        type: '축하',
        title: '김철수 과장 승진 축하 모임',
        lastMessage: '선물 어떤 거 준비하시나요?',
        lastTime: '어제',
      },
    ],
  },
  {
    id: 2,
    name: '이영희',
    chatRooms: [
      {
        roomId: 201,
        type: '위로',
        title: '영희 부친상 조문방',
        lastMessage: '부의금 봉투 작성하는 법 물어볼게',
        lastTime: '3일 전',
      },
    ],
  },
  {
    id: 3,
    name: '박민수',
    chatRooms: [],
  },
]);

const enterChatRoom = (roomId) => {
  alert(`대화방 ID: ${roomId} 로 진입합니다.`);
};
</script>
