<template>
    <div class="session-list">
        <h2>Sessions</h2>
        <div v-for="session in sessions" :key="session.client_id" :class="{ 'current-session': session.client_id === clientId, 'other-session': session.client_id !== clientId }">
        <div>
            <span>Client ID: {{ session.client_id }}</span>
            <span>Unique ID: {{ session.email }}</span>
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
import { openDB, getStore } from '@/utils/db'
import { sha1 } from '@/utils/crypto'
import { generateFingerprint } from '@/utils/device'
</script>

<script>
export default {
    name: 'SessionList',
    data() {
        return {
            clientId: null,
            response: "",
            sessions: []
        };
    },
    async mounted() {
        this.fetchSessions()
        const db = await openDB()
        const keyData = await getStore(db, 'encKeys', await sha1(JSON.stringify(await generateFingerprint())))
        if (keyData) {
            console.log(keyData)
            this.clientId = keyData.clientId || this.clientId
        }
    },
    methods: {
        async fetchSessions() {
            const response = await fetch('http://localhost:8000/list-keys')
            if (!response.ok) throw new Error('Error fetching session data')
            const data = await response.json()
            this.sessions = data.records
        },
        async revokeSession(client_id) {
            const response = await fetch('http://localhost:8000/revoke-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({client_id})
            })
            if (response.ok) {
                const result = await response.json()
                this.response = result
                console.log('Success:', result)
                this.sessions = this.sessions.filter(session => session.client_id !== client_id)
            } else {
                console.error('Response Error:', response.statusText)
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
  