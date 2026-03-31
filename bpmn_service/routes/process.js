"use strict";

const express = require("express");
const { Engine } = require("bpmn-engine");
const { v4: uuidv4 } = require("uuid");
const fs = require("fs");
const path = require("path");

const router = express.Router();

// In-memory instance store. Replace with Redis/Postgres for production.
const instances = new Map();

// ── Load BPMN definitions from disk ──────────────────────────────────────────

const DEFINITIONS_DIR = path.join(__dirname, "../definitions");

function loadDefinition(processId) {
  const filePath = path.join(DEFINITIONS_DIR, `${processId}.bpmn`);
  if (!fs.existsSync(filePath)) {
    const err = new Error(`Process definition not found: ${processId}`);
    err.status = 404;
    throw err;
  }
  return fs.readFileSync(filePath, "utf-8");
}

// ── POST /process/start ───────────────────────────────────────────────────────

router.post("/start", async (req, res) => {
  const { processId, variables = {} } = req.body;
  if (!processId) {
    return res.status(400).json({ error: "processId is required" });
  }

  const source = loadDefinition(processId);
  const instanceId = uuidv4();
  const correlationId = req.headers["x-correlation-id"] || instanceId;

  const engine = new Engine({
    name: processId,
    source,
    variables: { ...variables, instanceId, correlationId },
  });

  const stateSnapshot = {
    instanceId,
    processId,
    correlationId,
    status: "running",
    startedAt: new Date().toISOString(),
    variables: { ...variables, instanceId, correlationId },
    pendingActivities: [],
    engine, // hold reference for signal calls
  };

  instances.set(instanceId, stateSnapshot);

  // Start execution without blocking the response
  engine
    .execute()
    .then(() => {
      const inst = instances.get(instanceId);
      if (inst) inst.status = "completed";
    })
    .catch((err) => {
      console.error(`[BPMN] Instance ${instanceId} failed:`, err.message);
      const inst = instances.get(instanceId);
      if (inst) {
        inst.status = "error";
        inst.error = err.message;
      }
    });

  res.status(201).json({
    instanceId,
    processId,
    correlationId,
    status: "running",
    startedAt: stateSnapshot.startedAt,
  });
});

// ── GET /process/:instanceId/state ────────────────────────────────────────────

router.get("/:instanceId/state", (req, res) => {
  const inst = instances.get(req.params.instanceId);
  if (!inst) return res.status(404).json({ error: "Instance not found" });

  const { engine, ...safeState } = inst;
  res.json(safeState);
});

// ── POST /process/:instanceId/signal ─────────────────────────────────────────

router.post("/:instanceId/signal", async (req, res) => {
  const inst = instances.get(req.params.instanceId);
  if (!inst) return res.status(404).json({ error: "Instance not found" });

  const { signal, data = {} } = req.body;
  if (!signal) return res.status(400).json({ error: "signal is required" });

  // Update variables with signal data
  inst.variables = { ...inst.variables, ...data, lastSignal: signal };

  // Signal the engine if it supports it
  if (inst.engine && typeof inst.engine.signal === "function") {
    inst.engine.signal(signal, data);
  }

  res.json({
    instanceId: req.params.instanceId,
    signal,
    acknowledged: true,
    timestamp: new Date().toISOString(),
  });
});

// ── GET /process/:instanceId/variables ───────────────────────────────────────

router.get("/:instanceId/variables", (req, res) => {
  const inst = instances.get(req.params.instanceId);
  if (!inst) return res.status(404).json({ error: "Instance not found" });

  res.json({ instanceId: req.params.instanceId, variables: inst.variables });
});

// ── PUT /process/:instanceId/variables ───────────────────────────────────────

router.put("/:instanceId/variables", (req, res) => {
  const inst = instances.get(req.params.instanceId);
  if (!inst) return res.status(404).json({ error: "Instance not found" });

  inst.variables = { ...inst.variables, ...req.body };
  res.json({ instanceId: req.params.instanceId, variables: inst.variables });
});

// ── GET /process/definitions ──────────────────────────────────────────────────

router.get("/definitions", (_req, res) => {
  const definitions = fs
    .readdirSync(DEFINITIONS_DIR)
    .filter((f) => f.endsWith(".bpmn"))
    .map((f) => ({ processId: f.replace(".bpmn", ""), file: f }));
  res.json({ definitions });
});

module.exports = router;
