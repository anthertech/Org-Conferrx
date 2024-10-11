import { defineStore } from 'pinia'

export const useOutletStore = defineStore('event', {
  state: () => ({
    event: localStorage.getItem('event') || '', // Initialize from localStorage
  }),
  actions: {
    setOutlet(value) {
      this.event = value
      localStorage.setItem('event', value) // Persist in localStorage
    },
    clearOutlet() {
      this.event = ''
      localStorage.removeItem('event') // Clear from localStorage
    }
  },
})