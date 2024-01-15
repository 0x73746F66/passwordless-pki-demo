import { sha1 } from '@/utils/crypto'

export const generateFingerprint = async () => {
  const fingerprintText = 'passwordless-pki-demo'
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
    webGLHash = debugInfo
      ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
      : 'WebGL Not Supported'
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

export default {
  generateFingerprint
}
