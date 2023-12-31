const createStores = db => {
    if (!db.objectStoreNames.contains('encKeys')) {
        const encKeys = db.createObjectStore("encKeys", { keyPath: "clientId" })
        encKeys.createIndex("clientId-index", "clientId", { unique: true })
    }
}
export const openDB = (databaseName = "PasswordlessDemo", version = 1) => {
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
export const putStore = (db, storeName, data) => {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName], "readwrite")
        transaction.onerror = event => {
            console.error("Database error: ", event.target.error)
            reject(event.target.error)
        }
        const objectStore = transaction.objectStore(storeName)
        console.log(data)
        const request = objectStore.put(data)
        request.onsuccess = event => {
            resolve(event.target.result)
        }
    })
}
export const getStore = (db, storeName, keyId) => {
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

export default {
    getStore,
    putStore,
    openDB
}
