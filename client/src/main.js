import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.mount('#app')

window.wrapPEM = async function(key, isPrivate = false) {
    const keyType = !!isPrivate ? "PRIVATE" : "PUBLIC"
    let exportedKey = await crypto.subtle.exportKey(isPrivate ? "pkcs8" : "spki", key)
    const exportedAsString = String.fromCharCode.apply(null, new Uint8Array(exportedKey))
    const exportedAsBase64 = window.btoa(exportedAsString)
    const pemExported = `-----BEGIN ${keyType} KEY-----\n${exportedAsBase64}\n-----END ${keyType} KEY-----`
    return pemExported
}
window.generateKeyPair = async function() {
    try {
        const keyPair = await crypto.subtle.generateKey({
            name: "RSA-OAEP",
            modulusLength: 4096,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-512",
        }, true, ["encrypt", "decrypt"])
        return keyPair
    } catch (error) {
        console.error("Error generating and exporting public key: ", error)
        throw error
    }
}
window.sha1 = async function(data) {
    const buffer = new TextEncoder().encode(data)
    const digest = await crypto.subtle.digest('SHA-1', buffer)
    return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('')
}
window.generateFingerprint = async function() {
    const fingerprintText = "passwordless-pki-demo"
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    ctx.textBaseline = 'top'
    ctx.font = '14px Arial'
    ctx.textBaseline = 'alphabetic'
    ctx.fillRect(125, 1, 62, 20)
    ctx.fillStyle = '#069'
    ctx.fillText(fingerprintText, 2, 15)
    const canvasHash = await sha1(canvas.toDataURL())
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    let webGLHash = ''
    if (gl && gl instanceof WebGLRenderingContext) {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
        webGLHash = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'WebGL Not Supported'
    } else {
        webGLHash = 'WebGL Not Supported'
    }
    const ua = navigator.userAgent
    const lang = navigator.language
    const tz = new Date().getTimezoneOffset()
    const deviceMemory = navigator.deviceMemory || 'Not Supported'
    const hardwareConcurrency = navigator.hardwareConcurrency || 'Not Supported'
    const platform = navigator.platform || navigator.userAgentData.platform

    return {
        ua,
        lang,
        tz,
        canvasHash,
        webGLHash,
        deviceMemory,
        hardwareConcurrency,
        platform
    }
}
const createStores = db => {
    if (!db.objectStoreNames.contains('encKeys')) {
        const encKeys = db.createObjectStore("encKeys", { keyPath: "clientId" })
        encKeys.createIndex("clientId-index", "clientId", { unique: true })
    }
}
window.openDB = (databaseName = "PasswordlessDemo", version = 1) => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(databaseName, version)
        request.onerror = event => {
            console.error("Database error: ", event.target.error)
            reject(event.target.error)
        }
        request.onsuccess = event => {
            const db = event.target.result
            createStores(db)
            resolve(db)
        }
        request.onupgradeneeded = event => {
            createStores(event.target.result)
        }
    })
}
window.putStore = (db, storeName, data) => {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName], "readwrite")
        transaction.onerror = event => {
            console.error("Database error: ", event.target.error)
            reject(event.target.error)
        }
        const objectStore = transaction.objectStore(storeName)
        const request = objectStore.put(data)
        request.onsuccess = event => {
            resolve(event.target.result)
        }
    })
}
window.getStore = (db, storeName, keyId) => {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName])
        const objectStore = transaction.objectStore(storeName)
        const request = objectStore.get(keyId)
        request.onerror = event => {
            console.error("Database error: ", event.target.error)
            reject(event.target.error)
        }
        request.onsuccess = event => {
            resolve(event.target.result)
        }
    })
}

(async function main() {
    const db = await openDB()
    const fingerprint = await generateFingerprint()
    const clientId = await sha1(JSON.stringify(fingerprint))
    let keyData = await getStore(db, 'encKeys', clientId)
    if (!keyData) {
        console.log(`GENERATING KEYS`)
        const keyPair = await generateKeyPair()
        const publicKey = keyPair.publicKey
        const privateKey = keyPair.privateKey
        keyData = { clientId, fingerprint, publicKey, privateKey }
        await putStore(db, 'encKeys', keyData)
    }
})()