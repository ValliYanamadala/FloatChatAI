import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Explorer from "./pages/Explorer";
import FloatDetails from "./pages/FloatDetails";
import Analytics from "./pages/Analytics";
import QueryExplanation from "./pages/QueryExplanation";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/explorer" element={<Explorer />} />
        <Route path="/float-details" element={<FloatDetails />} />
        <Route path="/float/:id" element={<FloatDetails />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route
          path="/query-explanation"
          element={<QueryExplanation />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;