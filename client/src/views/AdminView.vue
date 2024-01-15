<template>
  <div class="session-list">
    <h2>Sessions</h2>
    <div
      v-for="session in sessions"
      :key="session.client_id"
      :class="{
        'current-session': session.client_id === clientId,
        'other-session': session.client_id !== clientId
      }"
    >
      <div>
        <span>Client ID: {{ session.client_id }}</span>
        <span>Unique ID: {{ session.unique_id }}</span>
        <span>User-Agent: {{ session.fingerprint.ua }}</span>
      </div>
      <div v-if="session.client_id !== clientId">
        <button @click="revokeSession(session.client_id)">Revoke</button>
      </div>
    </div>
  </div>
  <div v-if="response">
    <h2>Response from Server:</h2>
    <p>{{ response }}</p>
  </div>
</template>

<script setup>
import App from '@/utils/app';
</script>

<script>
const app = new App()
export default {
    name: 'SessionList',
    data() {
        return {
            clientId: null,
            response: '',
            sessions: []
        }
    },
    async mounted() {
        this.fetchSessions()        
        const storeData = await app.data()
        this.clientId = storeData.clientId
    },
    methods: {
        async fetchSessions() {
            const data = await app.listKeys()
            if (data?.records) {
                this.sessions = data.records
            } else {
                this.response = data || "No Sessions"
            }
        },
        async revokeSession(client_id) {
            const result = await app.revokeKey(client_id)
            if (result) {
                this.sessions = this.sessions.filter((session) => session.client_id !== client_id)
            } else {
                this.response = "Failed to revoke session"
            }

        }
    }
}
</script>

<style lang="scss">
.session-list {
  max-width: 600px;
  margin: auto;
  color: #1d1d1d;

  h2 {
    color: #d1d1d1;
    text-align: center;
  }

  .current-session {
    background-color: #d1e7dd;
    border: 1px solid #badbcc;
  }

  .other-session {
    background-color: #f8f6d7;
    border: 1px solid #f8f6d7;
  }

  div {
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;

    span {
      display: block;
    }

    button {
      margin-top: 2px;
      padding: 5px 10px;
      background-color: #dc3545;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;

      &:hover {
        background-color: #c82333;
      }
    }
  }
}
</style>
