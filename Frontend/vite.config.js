import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts: ['rybmw.space', 'k8s-default-appingre-6d548e4681-582162090.eu-north-1.elb.amazonaws.com', 'A38DE3240DFC949A0901DEF83763D152.gr7.eu-north-1.eks.amazonaws.com', 'localhost'] 
  },
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'https://rybmw.space')
  }
})
