export const wrapPEM = async (key, isPrivate = false) => {
  const keyType = isPrivate ? 'PRIVATE' : 'PUBLIC'
  let exportedKey = await crypto.subtle.exportKey(isPrivate ? 'pkcs8' : 'spki', key)
  const exportedAsString = String.fromCharCode.apply(null, new Uint8Array(exportedKey))
  const exportedAsBase64 = btoa(exportedAsString)
  return `-----BEGIN ${keyType} KEY-----\n${exportedAsBase64}\n-----END ${keyType} KEY-----`;
}
export const pemToArrayBuffer = (pem) => {
  const b64Lines = pem.split('\n').filter((line) => line.trim() && !line.includes('---'))
  const b64String = b64Lines.join('')
  return base64ToArrayBuffer(b64String)
}
export const base64ToArrayBuffer = (base64) => {
  const binaryString = atob(base64)
  const bytes = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i)
  }
  return bytes.buffer
}
export const generateKeyPair = async () => {
  try {
    return await crypto.subtle.generateKey(
      {
        name: 'RSA-OAEP',
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: 'SHA-512'
      },
      true,
      ['encrypt', 'decrypt']
    )
  } catch (error) {
    console.error('Error generating and exporting public key: ', error)
    throw error
  }
}
export const arrayBufferToBase64 = (buffer) => {
  let binary = ''
  let bytes = new Uint8Array(buffer)
  let len = bytes.byteLength
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}
export const uint8ArrayToHex = (buffer) => {
  let hex = ''
  for (const element of buffer) {
    let byte = element.toString(16)
    if (byte.length === 1) {
      byte = '0' + byte // Ensure each byte is represented by two characters
    }
    hex += byte
  }
  return hex
}
export const signMessage = async (privateKey, message) => {
  const encoder = new TextEncoder()
  const encodedMessage = encoder.encode(message)
  if (typeof privateKey === 'string') {
    // Convert the PEM formatted private key to a format usable by the Web Crypto API
    privateKey = await crypto.subtle.importKey( // sourcery skip: dont-reassign-parameters
      'pkcs8',
      pemToArrayBuffer(privateKey),
      {
        name: 'RSA-PSS',
        hash: 'SHA-512'
      },
      false,
      ['sign']
    )
  }
  const signature = await crypto.subtle.sign(
    {
      name: 'RSA-PSS',
      saltLength: 32 // Length of the salt
    },
    privateKey, // from generateKey or importKey
    encodedMessage
  )
  return uint8ArrayToHex(new Uint8Array(signature))
}
export const sha1 = async (data) => {
  const buffer = new TextEncoder().encode(data)
  const digest = await crypto.subtle.digest('SHA-1', buffer)
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}
export const decryptMessage = async (encryptedMessageBase64, privateKey) => {
  if (typeof privateKey === 'string') {
    // Convert the PEM formatted private key to a format usable by the Web Crypto API
    privateKey = await crypto.subtle.importKey( // sourcery skip: dont-reassign-parameters
      'pkcs8',
      pemToArrayBuffer(privateKey),
      {
        name: 'RSA-OAEP',
        hash: 'SHA-512'
      },
      false,
      ['decrypt']
    )
  }
  // Decode the base64 encrypted message
  const encryptedMessage = base64ToArrayBuffer(encryptedMessageBase64)
  // Decrypt the message
  const decrypted = await crypto.subtle.decrypt(
    {
      name: 'RSA-OAEP'
    },
    privateKey,
    encryptedMessage
  )

  return new TextDecoder().decode(decrypted)
}
export default {
  decryptMessage,
  sha1,
  generateKeyPair,
  base64ToArrayBuffer,
  pemToArrayBuffer,
  wrapPEM
}
