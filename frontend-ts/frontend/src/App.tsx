import { Routes, Route } from "react-router-dom";
import { useState } from 'react'
//import reactLogo from './assets/react.svg'
//import viteLogo from '/vite.svg'


  
import './App.css'
import IntroAnimation from "./IntroAnimation";
function App() {
  const [count, setCount] = useState(0)

  return (
    <>

      <IntroAnimation></IntroAnimation> 
    </>
  )
}

export default App
