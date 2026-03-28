"use client";

import { useMemo, useState, useEffect } from "react";
import { FarmingEnvClient } from "../lib/farmingEnvClient";

const ACTIONS = ["water", "plant", "harvest", "wait"];

function WeatherTag({ weather }) {
  const pretty =
    weather === "sunny" ? "Sunny" : weather === "rainy" ? "Rainy" : weather === "hot" ? "Hot" : weather;

  const tagClass = weather === "sunny" ? "tagSunny" : weather === "rainy" ? "tagRainy" : "tagHot";

  return (
    <span className={`tag ${tagClass}`}>
      Weather: <span style={{ color: "#fff" }}>{pretty}</span>
    </span>
  );
}

function MoistureBar({ value }) {
  // 0..1 => percent
  const pct = Math.round(value * 100);
  const red = value < 0.25 || value > 0.85;
  const barClass = red ? "bar red" : "bar blue";
  return (
    <div>
      <div className="muted" style={{ marginBottom: 6 }}>
        Soil moisture: <strong>{pct}%</strong>
      </div>
      <div className={barClass}>
        <div style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function CropStageTag({ crop_stage }) {
  if (crop_stage === 0) {
    return (
      <span className="tag tagEmpty">
        Crop stage: <span style={{ color: "#fff" }}>Field empty</span>
      </span>
    );
  }

  if (crop_stage === 1) {
    return (
      <span className="tag tagSeed">
        Crop stage: <span style={{ color: "#fff" }}>Seed</span>
      </span>
    );
  }

  if (crop_stage === 2) {
    return (
      <span className="tag tagGrowing">
        Crop stage: <span style={{ color: "#fff" }}>Growing</span>
      </span>
    );
  }

  return (
    <span className="tag tagMature">
      Crop stage: <span style={{ color: "#fff" }}>Mature</span>
    </span>
  );
}

function RewardExplanation() {
  return (
    <div className="rewardCard">
      <div className="rewardTitle">Reward Logic</div>

      <div className="rewardRow">
        <span className="rewardKey">Good crop health</span>
        <span className="rewardVal positive">Positive reward (+)</span>
      </div>
      <div className="rewardRow">
        <span className="rewardKey">Successful harvest</span>
        <span className="rewardVal positive">High reward (+)</span>
      </div>
      <div className="rewardRow">
        <span className="rewardKey">Overwatering or dry soil</span>
        <span className="rewardVal negative">Negative reward (-)</span>
      </div>
    </div>
  );
}

export default function Page() {
  const envSeed = 0;

  const env = useMemo(() => {
    return new FarmingEnvClient({ maxDays: 30, seed: envSeed });
  }, []);

  const [state, setState] = useState(() => env.reset({ seed: envSeed }));
  const [reward, setReward] = useState(0.0);
  const [done, setDone] = useState(false);
  const [totalReward, setTotalReward] = useState(0.0);
  const [action, setAction] = useState("wait");
  const [logs, setLogs] = useState([]);
  const [running, setRunning] = useState(false);

  const policy = () => {
    // Same simple policy as your rule_agent_demo.
    if (state.crop_stage === 0) return "plant";
    if (state.soil_moisture < 0.30) return "water";
    if (state.crop_stage >= 3) return "harvest";
    return "wait";
  };

  const addLog = (log) => {
    setLogs((prev) => {
      const next = [...prev, log];
      // Keep logs small for readability.
      return next.slice(Math.max(0, next.length - 60));
    });
  };

  const resetEpisode = () => {
    setDone(false);
    setRunning(false);
    setTotalReward(0.0);
    setReward(0.0);
    setLogs([]);
    const s = env.reset({ seed: envSeed });
    setState(s);
    setAction("wait");
  };

  const stepOnce = (a) => {
    if (done) return;

    const [nextState, r, nextDone, info] = env.step(a);
    setState(nextState);
    setReward(r);
    setDone(nextDone);
    setTotalReward((t) => t + r);

    addLog({
      day: nextState.day,
      weather: nextState.weather,
      soil: nextState.soil_moisture,
      stage: nextState.crop_stage,
      health: nextState.health,
      action: a,
      reward: r,
      detail: info?.action_detail || "",
    });
  };

  useEffect(() => {
    // Stop auto-run if episode ends.
    if (done) setRunning(false);
  }, [done]);

  useEffect(() => {
    if (!running) return;

    const t = setInterval(() => {
      if (done) return;
      stepOnce(policy());
    }, 650);

    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, done, state]);

  const actionExplain = () => {
    const soilPct = Math.round(state.soil_moisture * 100);
    const stage = state.crop_stage;

    if (action === "plant") {
      return `Crop field is empty (crop_stage == 0), so plant is applied.`;
    }
    if (action === "water") {
      return `Soil is too dry (<30%), now ${soilPct}%, so watering is applied.`;
    }
    if (action === "harvest") {
      return `Crop is ready (crop_stage >= 3, now ${stage}), so harvest is applied.`;
    }
    return `No urgent needs: soil ${soilPct}% and crop_stage ${stage}. Waiting is applied.`;
  };

  const today = state.day;

  return (
    <div className="container">
      <h1 className="title">AI Farming Environment Simulator (OpenEnv)</h1>
      <div className="muted" style={{ marginBottom: 16 }}>
        An OpenEnv-style environment designed for AI agents. Visualize daily transitions using
        <span style={{ fontFamily: "monospace" }}> reset()</span>, <span style={{ fontFamily: "monospace" }}>step()</span>, and{" "}
        <span style={{ fontFamily: "monospace" }}>state()</span>.
      </div>

      <div className="grid">
        <div className="panel">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <WeatherTag weather={state.weather} />
            <CropStageTag crop_stage={state.crop_stage} />
          </div>

          <div style={{ marginTop: 14 }}>
            <MoistureBar value={state.soil_moisture} />
          </div>

          <div style={{ marginTop: 12 }}>
            <div className="muted" style={{ marginBottom: 6 }}>
              Health: <strong>{Math.round(state.health)}</strong>
            </div>
            <div className="bar">
              <div style={{ width: `${Math.round(state.health)}%` }} />
            </div>
          </div>

          <div style={{ marginTop: 14 }} className="muted">
            Day: <strong>{today}</strong> / 30
          </div>

          <div style={{ marginTop: 18 }} className="row">
            <button onClick={resetEpisode}>Reset</button>

            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              disabled={done || running}
            >
              {ACTIONS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>

            <button onClick={() => stepOnce(action)} disabled={done || running}>
              Step
            </button>

            <button
              onClick={() => {
                if (!running) setRunning(true);
              }}
              disabled={done || running}
            >
              {running ? "Running..." : "Run (rule policy)"}
            </button>
            <button onClick={() => setRunning(false)} disabled={!running}>
              Stop
            </button>
          </div>

          <div style={{ marginTop: 12 }} className="muted">
            <div className="infoBox">
              <div className="infoBoxTitle">Why this action was taken</div>
              <p className="infoBoxText">
                {actionExplain()}
              </p>
            </div>
          </div>

          <RewardExplanation />

          <div style={{ marginTop: 10 }} className="muted">
            Latest reward: <strong>{reward.toFixed(2)}</strong> | Total reward:{" "}
            <strong>{totalReward.toFixed(2)}</strong>
          </div>

          {done ? (
            <div style={{ marginTop: 14 }} className="badge">
              Episode finished (day limit reached)
            </div>
          ) : null}
        </div>

        <div className="panel">
          <div className="title" style={{ fontSize: 18 }}>
            Day-wise log
          </div>
          <div className="muted" style={{ marginBottom: 10 }}>
            Shows action + reward for the most recent steps.
          </div>
          <div className="log">
            {logs.length === 0 ? (
              <div className="logLine muted">No steps yet. Click “Step” or “Run”.</div>
            ) : null}
            {logs
              .slice()
              .reverse()
              .map((l, idx) => (
                <div className="logLine" key={`${l.day}-${idx}`}>
                  <div className="logHeader">
                    <span className="logDay">
                      <strong>Day {l.day}</strong>
                    </span>
                    <span className="muted">{l.weather}</span>
                  </div>
                  <div>
                    soil={l.soil.toFixed(2)} | stage={l.stage} | health={l.health.toFixed(0)} | action=
                    <span className="actionChip">
                      <strong>{l.action}</strong>
                    </span>{" "}
                    | reward=
                    <span className={l.reward >= 0 ? "rewardTextPos" : "rewardTextNeg"}>
                      {l.reward.toFixed(2)}
                    </span>
                    {l.detail ? ` | ${l.detail}` : ""}
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

