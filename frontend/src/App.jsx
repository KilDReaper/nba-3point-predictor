import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/model-info")
      .then((res) => {
        setModelInfo(res.data);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <h1>Loading...</h1>;
  }

  return (
    <div style={{ padding: "40px", color: "white" }}>
      <h1>🏀 NBA 3PT Predictor</h1>

      <h2>Backend Connected ✅</h2>

      <p>
        <strong>Model:</strong> {modelInfo.model_type}
      </p>

      <p>
        <strong>MAE:</strong> {modelInfo.mae}
      </p>

      <p>
        <strong>R²:</strong> {modelInfo.r2}
      </p>

      <p>
        <strong>Training Seasons:</strong> {modelInfo.seasons}
      </p>

      <p>
        <strong>Training Rows:</strong> {modelInfo.training_rows}
      </p>

      <p>
        <strong>Features:</strong> {modelInfo.features.length}
      </p>
    </div>
  );
}

export default App;