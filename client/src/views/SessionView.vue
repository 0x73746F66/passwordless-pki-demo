<template>
  <div class="session">
        <h1>Session data</h1>
        <div><div class="label">Client ID: </div>{{ clientId }}</div>
        <div><div class="label">Email: </div>{{ email }}</div>
        <div class="label">Fingerprint: </div><pre>{{ fingerprint }}</pre>
        <div class="label">Public Key: </div><pre>{{ publicKey }}</pre>
        <div class="label">Private Key: </div><pre>{{ privateKey }}</pre>
        <div>
          <button @click="submitPublicKey">Save</button>
        </div>
      </div>
</template>

<script scoped>
export default {
    data() {
        return {
            clientId: "Not set",
            email: "Not set",
            fingerprint: "Not set",
            publicKey: "Not set",
            privateKey: "Not set",
        }
    },
    async mounted() {
        const db = await openDB()

        const keyData = await getStore(db, 'encKeys', await sha1(JSON.stringify(await generateFingerprint())))
        console.log('keyData', keyData)
        this.clientId = keyData.clientId || this.clientId
        this.fingerprint = keyData.fingerprint || this.fingerprint
        if (keyData.publicKey) {
            this.publicKey = await wrapPEM(keyData.publicKey)
        }
        if (keyData.privateKey) {
            this.privateKey = await wrapPEM(keyData.privateKey, true)
        }
    },
    methods: {
        submitPublicKey: async function() {
            try {
                const response = await fetch('http://localhost:8000/submit-key', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        client_id: this.clientId,
                        fingerprint: this.fingerprint,
                        public_key: this.publicKey,
                        email: null
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log('Success:', result);
                } else {
                    console.error('Response Error:', response.statusText);
                }
            } catch (error) {
                console.error('Network Error:', error.message);
            }
        }
    }
}
</script>

<style scoped lang="scss">
@media (min-width: 1024px) {
  .session {
    .label {
        font-weight: 600;
    }
    min-height: 100vh;
    > pre {
        white-space: pre-wrap;
    }
    button {
        border: 0;
        cursor: pointer;
        padding: 0.4em 2em;
        background-color: teal;
    }
    button:active {
        margin: 1px 0 0 1px;
    }
  }
}
</style>
