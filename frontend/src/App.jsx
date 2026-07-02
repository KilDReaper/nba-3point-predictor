import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Player from "./pages/Player";
import Predict from "./pages/Predict";
import ShotPredictor from "./pages/ShotPredictor";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="container" style={styles.main}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/player" element={<Player />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/court" element={<ShotPredictor />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  );
}

const styles = {
  main: {
    flex: 1,
    width: "100%",
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "32px 24px",
    boxSizing: "border-box",
  }
};

export default App;