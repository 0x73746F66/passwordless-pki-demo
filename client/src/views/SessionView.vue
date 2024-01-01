<template>
    <div class="session-data">
      <h1>Session Information</h1>
      <button @click="submitPublicKey">Check</button>
      <div v-if="response">
          <h2>Response from Server:</h2>
          <p>{{ response }}</p>
      </div>
      <div class="data-section">
        <h2>Client ID:</h2>
        <p>{{ clientId }}</p>
      </div>
      <div class="data-section">
        <h2>Email:</h2>
        <p>{{ email }}</p>
      </div>
      <div class="data-section">
        <h2>Fingerprint:</h2>
        <pre>{{ fingerprint }}</pre>
      </div>
      <div class="data-section">
        <h2>Public Key:</h2>
        <pre>{{ publicKey }}</pre>
      </div>
      <div class="data-section">
        <h2>Private Key:</h2>
        <pre>{{ privateKey }}</pre>
      </div>
    </div>
</template>

<script setup>
import { openDB, getStore } from '@/utils/db'
import { sha1, wrapPEM } from '@/utils/crypto'
import { generateFingerprint } from '@/utils/device'
</script>

<script>
export default {
    data() {
        return {
            clientId: "Not set",
            email: "Not set",
            fingerprint: "Not set",
            publicKey: "Not set",
            privateKey: "Not set",
            response: ""
        }
    },
    async mounted() {
        const db = await openDB()

        const keyData = await getStore(db, 'encKeys', await sha1(JSON.stringify(await generateFingerprint())))
        if (keyData) {
            this.email = keyData.email || this.email
            this.clientId = keyData.clientId || this.clientId
            this.fingerprint = keyData.fingerprint || this.fingerprint
            if (keyData.publicKey) {
                this.publicKey = await wrapPEM(keyData.publicKey)
            }
            if (keyData.privateKey) {
                this.privateKey = await wrapPEM(keyData.privateKey, true)
            }
        }
    },
    methods: {
        async submitPublicKey() {
            const response = await fetch('http://localhost:8000/check-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    public_key: this.publicKey,
                    unique_id: this.email
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.response = result
                console.log('Success:', result);
            } else {
                console.error('Response Error:', response.statusText);
            }
        }
    }
}
</script>

<style scoped lang="scss">
.session-data {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  color: #1d1d1d;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

  h1 {
    text-align: center;
  }

  .data-section {
    margin-top: 20px;

    p, pre {
      background-color: #fff;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 5px;
      overflow-x: auto;
    }

    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
  button {
      border: 0;
      color: #1d1d1d;
      font-size: 1em;
      cursor: pointer;
      padding: .8em 2.5em;
      border-radius: .4em;
      background-color: teal;
  }
  button:active {
      margin: 1px 0 0 1px;
  }
}
</style>
