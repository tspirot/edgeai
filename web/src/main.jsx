import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import './index.css'
import { initTheme } from './lib/theme'
import App from './App'
import Home from './pages/Home'
import Projekti from './pages/Projekti'
import Projekat from './pages/Projekat'
import Uputstva from './pages/Uputstva'
import Uputstvo from './pages/Uputstvo'
import Lms from './pages/Lms'
import Lekcija from './pages/Lekcija'
import Primer from './pages/Primer'
import OProgramu from './pages/OProgramu'
import NotFound from './pages/NotFound'

initTheme()

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: 'projekti', element: <Projekti /> },
      { path: 'projekti/:slug', element: <Projekat /> },
      { path: 'uputstva', element: <Uputstva /> },
      { path: 'uputstva/:slug', element: <Uputstvo /> },
      { path: 'lms', element: <Lms /> },
      { path: 'lms/primeri/:slug', element: <Primer /> },
      { path: 'lms/:slug', element: <Lekcija /> },
      { path: 'o-programu', element: <OProgramu /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
