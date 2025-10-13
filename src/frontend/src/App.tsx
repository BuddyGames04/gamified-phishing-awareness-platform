import logo from './logo.svg';
import React, { useEffect, useState } from "react";
import "./App.css";
import InboxView from "./components/InboxView";
import ArcadeMode from "./components/ArcadeMode";

const App: React.FC = () => {
 const [mode, setMode] = useState<"inbox" | "arcade">("inbox");
  return (
    <div className="App">
      <h1>Phishing Awareness Platform</h1>
      <button onClick={() => setMode("inbox")}>Inbox Mode</button>
      <button onClick={() => setMode("arcade")}>Arcade Mode</button>
      {mode === "inbox" ? <InboxView /> : <ArcadeMode />}
    </div>
  );
};

export default App;


