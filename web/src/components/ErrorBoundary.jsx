import { Component } from 'react'

/** Хвата грешке у подстаблу (нпр. WebGL недоступан) и приказује `fallback`. */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { failed: false }
  }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  componentDidCatch(err) {
    if (import.meta.env.DEV) console.warn('ErrorBoundary:', err)
  }
  render() {
    if (this.state.failed) return this.props.fallback ?? null
    return this.props.children
  }
}
