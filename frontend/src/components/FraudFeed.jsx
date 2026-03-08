import React, { useEffect, useState } from "react";

export default function FraudFeed() {

  const [events, setEvents] = useState([]);

  useEffect(() => {

    const interval = setInterval(async () => {

      try {

        const response = await fetch("http://localhost:8000/fraud/stream");

        const data = await response.json();

        if (data.events) {

          setEvents(prev => {

            const merged = [...data.events, ...prev];

            return merged.slice(0, 25); // keep last 25 events

          });

        }

      } catch (err) {
        console.error("Feed error:", err);
      }

    }, 2000); // refresh every 2s

    return () => clearInterval(interval);

  }, []);

  return (
    <div style={{
      background: "#0f1624",
      padding: "15px",
      borderRadius: "8px",
      height: "400px",
      overflowY: "auto"
    }}>
      <h3 style={{ marginBottom: "10px" }}>⚡ Real-Time Fraud Feed</h3>

      {events.map((event, i) => (

        <div key={i} style={{
          padding: "8px",
          borderBottom: "1px solid #1e2a3a",
          fontSize: "13px"
        }}>

          <div><b>{event.type}</b></div>
          <div>tx: {event.transaction_id}</div>
          <div>risk: {(event.score || 0).toFixed(2)}</div>

        </div>

      ))}

    </div>
  );
}