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
      <p>{{ storeData.clientId || 'Not set' }}</p>
    </div>
    <div class="data-section">
      <h2>Unique ID:</h2>
      <p>{{ storeData.uniqueId || 'Not set' }}</p>
    </div>
    <div class="data-section">
      <h2>Fingerprint:</h2>
      <pre>{{ storeData.fingerprint || 'Not set' }}</pre>
    </div>
    <div class="data-section">
      <h2>Public Key:</h2>
      <pre>{{ storeData.publicKey || 'Not set' }}</pre>
    </div>
    <div class="data-section">
      <h2>Private Key:</h2>
      <pre>{{ storeData.privateKey || 'Not set' }}</pre>
    </div>
  </div>
</template>

<script setup>
import App from '@/utils/app'
import { wrapPEM } from '@/utils/crypto'
</script>

<script>
const app = new App()
export default {
  data() {
    return {
        storeData: {
            clientId: 'Not Set',
            uniqueId: 'Not Set',
            fingerprint: 'Not Set',
            publicKey: 'Not Set',
            privateKey: 'Not Set',
        },
        response: ''
    }
  },
  async mounted() {
      const storeData = await app.data()
      this.storeData.clientId = storeData.clientId
      this.storeData.uniqueId = storeData.uniqueId
      this.storeData.fingerprint = storeData.fingerprint
      this.storeData.publicKey = await wrapPEM(storeData.publicKey)
      this.storeData.privateKey = await wrapPEM(storeData.privateKey, true)
  },
  methods: {
    async submitPublicKey() {
        this.response =  await app.check(this.storeData.publicKey, this.storeData.uniqueId)
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

    p,
    pre {
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
    padding: 0.8em 2.5em;
    border-radius: 0.4em;
    background-color: teal;
  }
  button:active {
    margin: 1px 0 0 1px;
  }
}
</style>
