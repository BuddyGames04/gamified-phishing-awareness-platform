import logo from './logo.svg';
import React, { useEffect, useState } from "react";
import "./App.css";
import InboxView from "./components/InboxView";

const App: React.FC = () => {
  return (
    <div className="App">
      <h1>Inbox Simulation</h1>
      <InboxView />
    </div>
  );
};

export default App;


