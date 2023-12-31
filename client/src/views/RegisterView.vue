<template>
  <div>
    <form class="form-container" @submit.prevent="register">
      <h1>Register with server</h1>
      <FormHelpDescription text="Send the device public key to the server with a unique client ID" />
      <div>
        <label for="email">Unique client ID:</label>
        <input type="email" id="email" placeholder="Use email or something else that the server has never seen" v-model="formData.uniqueId" required>
      </div>
      <button type="submit">Register Client</button>
    </form>

    <div v-if="response">
      <h2>Response from Server:</h2>
      <p>{{ response }}</p>
    </div>
  </div>

</template>

<script setup>
import FormHelpDescription from '@/components/FormHelpDescription.vue';
</script>

<script>
export default {
    components: {
        FormHelpDescription
    },
    data() {
        return {
            formData: {
                uniqueId: "",
            },
            keyData: {
                clientId: null,
                fingerprint: null,
                publicKey: null,
                privateKey: null
            },
            response: null
        };
    },
    async mounted() {
        const db = await openDB()
        this.keyData.fingerprint = await generateFingerprint()
        this.keyData.clientId = await sha1(JSON.stringify(this.keyData.fingerprint))
        const keyData = await getStore(db, 'encKeys', this.keyData.clientId)
        if (keyData?.privateKey) {
            this.keyData.publicKey = keyData.publicKey
            this.keyData.privateKey = keyData.privateKey
        } else {
            console.log(`GENERATING KEYS`)
            const keyPair = await generateKeyPair()
            this.keyData.publicKey = keyPair.publicKey
            this.keyData.privateKey = keyPair.privateKey
        }
    },
    methods: {
        async register() {
            const response = await fetch('http://localhost:8000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    client_id: this.keyData.clientId,
                    fingerprint: this.keyData.fingerprint,
                    public_key: await wrapPEM(this.keyData.publicKey),
                    unique_id: this.formData.uniqueId
                })
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.response = data;
            const db = await openDB()
            await putStore(db, 'encKeys', {
                clientId: this.keyData.clientId,
                email: this.formData.uniqueId,
                fingerprint: JSON.parse(JSON.stringify(this.keyData.fingerprint)),
                publicKey: this.keyData.publicKey,
                privateKey: this.keyData.privateKey
            })
        }
    }
};
</script>

<style scoped lang="scss">
$form-background: #f5f5f5;
$form-border-color: #ddd;
$form-border-radius: 5px;
$button-color: teal;
$button-hover-color: darken($button-color, 10%);
$label-spacing: 5px;

.form-container {
  background-color: $form-background;
  border: 1px solid $form-border-color;
  border-radius: $form-border-radius;
  padding: 20px;
  margin: 0 auto;
  color: #1a1a1a;

  label {
    display: block;
    margin-bottom: $label-spacing;
  }

  input[type="email"],
  textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid $form-border-color;
    border-radius: $form-border-radius;
    margin-bottom: 10px;
  }
  textarea {
    height: 150px;
  }

  button {
    background-color: $button-color;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: $form-border-radius;
    cursor: pointer;

    &:hover {
      background-color: $button-hover-color;
    }
  }
}
</style>
