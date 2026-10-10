# 🍽️ AI Restaurant Menu Recommender

> An AI-powered restaurant menu recommender built with **Django**, **Ollama**, and **Qwen2.5**. Users describe what they want in natural language, and the AI suggests the best dishes from the menu.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1%2B-green?logo=django&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=ollama&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📖 Overview

This project is a **local, privacy-first** restaurant menu recommender. It uses a local LLM (via Ollama) to understand customer requests in **natural Persian language** and recommend suitable dishes from a restaurant's menu — without sending any data to the cloud.

**Example:**
> 👤 User: "یک غذای گیاهی و سبک می‌خواهم، زیر ۲۵۰ هزار تومان"
> 🤖 AI: Recommends "سوپ قارچ" and "پیتزا مارگاریتا" with reasons

---

## ✨ Features

- 🧠 **Local AI** — Powered by Ollama + Qwen2.5 (no cloud, no API keys)
- 🇮🇷 **Persian NLP** — Understands natural Persian requests
- 🍽️ **Menu Management** — Add/edit dishes via Django admin
- 🎯 **Smart Recommendations** — 2-3 dishes with reasons and confidence scores
- 🎨 **Modern UI** — Beautiful RTL interface with Bootstrap 5
- 🚀 **Fast** — SQLite + local LLM, no external dependencies
- 🔒 **Privacy-first** — All data stays on your machine

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.1 |
| Frontend | Django Templates + Bootstrap 5 RTL |
| LLM Runtime | Ollama |
| LLM Model | Qwen2.5-7B-Instruct (GGUF) |
| Database | SQLite |
| HTTP Client | requests |

---