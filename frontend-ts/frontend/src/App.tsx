import { Routes, Route } from "react-router-dom";
import { useState } from 'react'
//import reactLogo from './assets/react.svg'
//import viteLogo from '/vite.svg'


  
import './App.css'
import Dashbord from './dashboard/Dashboard'
function App() {
  const [count, setCount] = useState(0)

  return (
    <>

      <Dashbord></Dashbord> 
    </>
  )
}

export default App
