---
title: Cyber War Env
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Cyber War Environment

## Overview
This is a cybersecurity simulation environment built using OpenEnv.

An AI agent acts as a security analyst and takes actions to handle cyber threats.

## Objective
The agent must:
- Detect attacks
- Prevent malicious activity
- Avoid blocking normal users

## Observation
The agent receives:
- alerts
- system_load
- threat_level

## Actions
- block_ip
- investigate
- rate_limit
- ignore

## Goal
Maximize reward by correctly handling threats.

## Run
uvicorn server.app:app --reload