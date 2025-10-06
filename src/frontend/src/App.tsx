import logo from './logo.svg';
import './App.css';

import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/hello/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => console.error("Error fetching:", err));
  }, []);

  return <h1>{message || "Loading..."}</h1>;
}

export default App;

//ignore

