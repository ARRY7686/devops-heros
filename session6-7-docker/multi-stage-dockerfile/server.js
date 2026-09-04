const express = require("express");

const app = express();
const PORT = 3000;

app.get("/", (req, res) => {
  res.send("<h1>Hello World from Docker Multi-Stage Build! Aadi Gupta 24bcs10167</h1>");
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});