<template>
  <div class="session">
    <h1>Session data</h1>
    <div>{{ clientId }}</div>
    <pre>{{ fingerprint }}</pre>
    <pre>{{ publicKey }}</pre>
    <pre>{{ privateKey }}</pre>
  </div>
</template>

<script scoped>
export default {
    data() {
        return {
            clientId: 'null',
            fingerprint: 'null',
            publicKey: 'null',
            privateKey: 'null',
        }
    },
    async mounted() {
        const db = await openDB()

        const keyData = await getStore(db, 'encKeys', await sha1(JSON.stringify(await generateFingerprint())))
        console.log('keyData', keyData)
        this.clientId = keyData.clientId
        this.fingerprint = keyData.fingerprint
        this.publicKey = await wrapPEM(keyData.publicKey)
        this.privateKey = await wrapPEM(keyData.privateKey, true)
    }
}
</script>

<style scoped lang="scss">
@media (min-width: 1024px) {
  .session {
    min-height: 100vh;
    > pre {
        white-space: pre-wrap;
    }
  }
}
</style>
