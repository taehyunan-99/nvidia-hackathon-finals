import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../../.agents/skills/nvidia-ui/assets/tokens.css";
import "../../.agents/skills/nvidia-ui/assets/components.css";
import "../../.agents/skills/nvidia-ui/assets/agent-flow.css";
import "./styles.css";
import App from "./App";
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
