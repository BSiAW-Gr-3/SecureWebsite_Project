export const API_URL = import.meta.env.VITE_API_URL || 'https://rybmw.space';
export const WS_URL = API_URL.replace('https://', 'wss://').replace('http://', 'ws://');