<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md bg-white flex flex-col min-h-screen shadow-lg relative pb-16 select-none"
    >
      <header
        class="flex items-center px-5 py-4 border-b border-slate-50 min-h-[64px]"
      >
        <button
          v-if="selectedPerson"
          @click="selectedPerson = null"
          class="mr-3 text-slate-600 hover:text-slate-900 active:scale-95 transition"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2.5"
            stroke="currentColor"
            class="w-6 h-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15.75 19.5 8.25 12l7.5-7.5"
            />
          </svg>
        </button>

        <h1 class="text-xl font-extrabold text-slate-950">
          {{
            selectedPerson
              ? `${selectedPerson.name}님과의 대화방`
              : '인물 리스트'
          }}
        </h1>
      </header>

      <main class="flex-1 overflow-y-auto p-4">
        <div v-if="!selectedPerson" class="space-y-3">
          <p class="text-xs font-semibold text-slate-400 px-1 mb-2">
            인물을 선택하면 관련 채팅방 목록을 볼 수 있습니다.
          </p>

          <button
            v-for="person in peopleData"
            :key="person.id"
            @click="selectPerson(person)"
            class="w-full flex items-center justify-between p-4 bg-slate-50/60 rounded-2xl border border-slate-100 hover:bg-slate-50 hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
          >
            <div class="flex items-center space-x-3">
              <div
                class="w-11 h-11 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm shadow-sm"
              >
                {{ person.name[0] }}
              </div>
              <div>
                <h3
                  class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors"
                >
                  {{ person.name }}
                </h3>
                <p class="text-xs text-slate-400 mt-0.5">
                  총 {{ person.chatRooms.length }}개의 대화방
                </p>
              </div>
            </div>

            <div
              class="text-slate-300 group-hover:text-indigo-500 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2.5"
                stroke="currentColor"
                class="w-5 h-5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="m8.25 4.5 7.5 7.5-7.5 7.5"
                />
              </svg>
            </div>
          </button>
        </div>

        <div v-else class="space-y-3">
          <div
            v-if="selectedPerson.chatRooms.length === 0"
            class="flex flex-col items-center justify-center h-64 text-slate-400"
          >
            <p class="text-sm font-medium">진행 중인 대화방이 없습니다.</p>
          </div>

          <button
            v-for="room in selectedPerson.chatRooms"
            :key="room.roomId"
            @click="enterChatRoom(room.roomId)"
            class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left"
          >
            <div class="flex-1 min-w-0 pr-4">
              <div class="flex items-center justify-between mb-1">
                <span
                  class="text-[11px] font-bold px-2 py-0.5 rounded-md"
                  :class="getTagStyle(room.type)"
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
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2"
                stroke="currentColor"
                class="w-5 h-5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
                />
              </svg>
            </div>
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 1. 선택된 인물 상태 관리 (null이면 리스트, 데이터가 있으면 해당 채팅방 목록 조회)
const selectedPerson = ref(null);

// 2. 가상 데이터 (인물 및 각 인물별 종속된 채팅방 리스트)
const peopleData = ref([
  {
    id: 1,
    name: '김철수',
    chatRooms: [
      {
        roomId: 101,
        type: '결혼식',
        title: '철수형 결혼 축하 모임',
        lastMessage: '축의금은 얼마로 하는 게 좋을까?',
        lastTime: '방금 전',
      },
      {
        roomId: 102,
        type: '승진',
        title: '김철수 대리 승진 톡방',
        lastMessage: '축하드려요 대리님!! 🎉',
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
        type: '출산',
        title: '영희 순산 기원 방',
        lastMessage: '아기 너무 예쁘다 고생했어!',
        lastTime: '2일 전',
      },
    ],
  },
  {
    id: 3,
    name: '박민수',
    chatRooms: [], // 대화방이 없는 경우 테스트용
  },
]);

// 3. 인물 선택 함수
const selectPerson = (person) => {
  selectedPerson.value = person;
};

// 4. 최종 대화방 진입 함수
const enterChatRoom = (roomId) => {
  alert(`대화방 ID: ${roomId}번 방으로 진입합니다.`);
  // 실제 프로젝트에서는 router.push(`/chat/${roomId}`) 등으로 연동하시면 됩니다.
};

// 5. 방 유형별 태그 디자인 매칭
const getTagStyle = (type) => {
  switch (type) {
    case '결혼식':
      return 'bg-rose-50 text-rose-600';
    case '승진':
      return 'bg-emerald-50 text-emerald-600';
    case '출산':
      return 'bg-indigo-50 text-indigo-600';
    default:
      return 'bg-slate-50 text-slate-600';
  }
};
</script>
