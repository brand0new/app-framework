"use strict";

require("express-async-errors");

const express = require("express");
const morgan = require("morgan");
const processRoutes = require("./routes/process");

const PORT = process.env.PORT || 3001;

const app = express();

app.use(express.json({ limit: "10mb" }));
app.use(morgan("combined"));

// ── Routes ────────────────────────────────────────────────────────────────────

app.use("/process", processRoutes);

app.get("/health", (_req, res) => {
  res.json({ status: "ok", version: "2.0.0", engine: "bpmn-engine@25.0.1" });
});

// ── Global error handler ──────────────────────────────────────────────────────

// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error("[BPMN Service Error]", err.message, err.stack);
  res.status(err.status || 500).json({
    error: err.message || "Internal server error",
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`[BPMN Service] Listening on port ${PORT}`);
});

module.exports = app;
