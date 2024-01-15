
import { generateFingerprint } from '@/utils/device'
import { signMessage, sha1, decryptMessage, wrapPEM, generateKeyPair } from '@/utils/crypto'
import { openDB, getStore, putStore } from '@/utils/db'

export default class App {
    static #urlPrefix = 'http://localhost:8000'
    static #dbStore = 'encKeys'
    #db = null
    #fingerprint = null
    #clientId = null
    async fingerprint() {
        if (this.#fingerprint) {
            return this.#fingerprint
        }
        const fingerprint = await generateFingerprint()
        this.#fingerprint = JSON.parse(JSON.stringify(fingerprint))
        return this.#fingerprint
    }
    async clientId() {
        if (this.#clientId) {
            return this.#clientId
        }
        const fingerprint = await this.fingerprint()
        this.#clientId = await sha1(JSON.stringify(fingerprint))
        return this.#clientId
    }
    async getDatabase() {
        if (this.#db) {
            return this.#db
        }
        this.#db = await openDB()
        return this.#db
    }
    async listKeys() {
        const params = await this.signRequest('', 'GET')
        const response = await fetch(`${App.#urlPrefix}/list-keys`, params)
        if (!response.ok) {
            return `HTTP error! status: ${response.status}`
        }
        return response.json()
    }
    async revokeKey(client_id) {
        const params = await this.signRequest(client_id)
        params.body = JSON.stringify({ client_id })
        const response = await fetch(`${App.#urlPrefix}/revoke-key`, params)
        if (!response.ok) {
            return `HTTP error! status: ${response.status}`
        }
        return response.json()
    }
    async check(publicKey, uniqueId) {
        const response = await fetch(`${App.#urlPrefix}/check-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                public_key: publicKey,
                unique_id: uniqueId
            })
        })
        if (!response.ok) {
            return `HTTP error! status: ${response.status}`
        }
        return response.json()
    }
    async signRequest(body = null, method = "POST") {
        const {privateKey, uniqueId} = await this.data()
        const timestamp = Math.floor(Date.now() / 1000)
        let message = `${timestamp}|${uniqueId}`
        if (body) {
            message = `${message}|${body}`
        }
        const b64digest = await signMessage(await wrapPEM(privateKey, true), message)
        const params = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Digest sig="${b64digest}" ts="${timestamp}" id="${uniqueId}"`,
            }
        }
        if (!['HEAD', 'GET'].includes(method.toUpperCase())) {
            params.body = body
        }
        return params
    }
    async sendMessage(message) {
        const params = await this.signRequest(message)
        params.body = JSON.stringify({ message })
        try {
            const response = await fetch(`${App.#urlPrefix}/encrypt-message`, params)
            if (!response.ok) {
                return `HTTP error! status: ${response.status}`
            }
            const data = await response.json()
            const {privateKey} = await this.data()
            if (data.encrypted_message) {
                data.decrypted_message = await decryptMessage(data.encrypted_message, privateKey)
            }
            return data
        } catch ({ name, message }) {
            return `${name}: ${message}`
        }
    }
    async register(uniqueId) {
        const {fingerprint, clientId, publicKey, privateKey} = await this.data()
        const response = await fetch(`${App.#urlPrefix}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fingerprint,
                client_id: clientId,
                public_key: await wrapPEM(publicKey),
                unique_id: uniqueId
            })
        })
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        await putStore(await this.getDatabase(), App.#dbStore, {
            clientId,
            uniqueId,
            fingerprint,
            publicKey,
            privateKey
        })
        return response.json()
    }
    async data() {
        const fingerprint = await this.fingerprint()
        const clientId = await this.clientId()
        const storeData = await getStore(await this.getDatabase(), App.#dbStore, clientId)
        let {publicKey, privateKey, uniqueId} = {publicKey: storeData?.publicKey, privateKey: storeData?.privateKey, uniqueId: storeData?.uniqueId}
        if (!privateKey) {
            console.log(`generating key pair`)
            const keyPair = await generateKeyPair()
            publicKey = keyPair.publicKey
            privateKey = keyPair.privateKey
            await putStore(await this.getDatabase(), App.#dbStore, {
                clientId,
                fingerprint,
                publicKey,
                privateKey
            })
        }
        return { publicKey, privateKey, clientId, fingerprint, uniqueId }
    }
}
