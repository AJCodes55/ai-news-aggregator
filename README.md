# AI News Digest Agent

An automated AI-powered system that continuously scans, summarizes, and delivers the most important updates in Artificial Intelligence from YouTube, X (Twitter), and leading research organizations — straight to your inbox every day.

---

## Overview

The AI News Digest Agent is designed to reduce information overload by collecting high-signal AI content from trusted sources, summarizing it using a large language model, and delivering a ranked daily digest.

The system runs fully automated on scheduled jobs and maintains structured historical data for further analysis.

---

## System Architecture

The project is composed of multiple specialized agents working together.

---

## 1. Data Collection Agents

### YouTube Scanner
- Scans selected AI-focused YouTube channels from the last 24 hours  
- Extracts video transcripts  
- Stores raw transcripts and metadata in PostgreSQL  

### X (Twitter) Scanner
- Monitors curated AI-focused X accounts  
- Extracts relevant AI-related posts  
- Stores post content and metadata in PostgreSQL  

### Research & News Fetcher
- Fetches latest articles, announcements, and research from:
  - OpenAI
  - Anthropic  
- Stores full content and metadata in PostgreSQL  

---

## 2. Digest AI Agent

- Powered by **Gemini Flash 2.5**
- Processes:
  - YouTube transcripts
  - Research articles
  - X posts
- Generates concise, high-signal summaries
- Stores summaries in a dedicated **Digests** table
- Focuses on:
  - Key insights
  - Novel announcements
  - Practical implications

---

## 3. Email Agent

- Runs once every 24 hours
- Pulls all digests generated in the last day
- Ranks items by relevance and importance
- Sends a daily email containing:
  - Top 10 AI updates
  - Clean, readable summaries

---

## Tech Stack

- **Language:** Python  
- **Containerization:** Docker  
- **Database:** PostgreSQL  
- **LLM:** Gemini Flash 2.5 API  
- **Deployment:** Render  
- **Scheduling:** Render scheduled jobs / cron-based execution  

---

## Data Flow

1. Scheduled job triggers data collection agents  
2. Raw content is stored in PostgreSQL  
3. Digest AI Agent summarizes content using Gemini Flash 2.5  
4. Summaries are stored in the Digests table  
5. Email Agent ranks and sends daily updates  

---

## Key Features

- Fully automated AI news aggregation  
- Multi-source ingestion (YouTube, X, research labs)  
- High-signal LLM-based summarization  
- Persistent database for historical analysis  
- Daily ranked email digest  
- Scalable and containerized deployment  

---

## Use Cases

- Staying updated with AI research and product launches  
- Reducing noise from social media and long-form content  
- Tracking trends across multiple AI platforms  
- Building a personal or team AI intelligence feed  

---

## Deployment

The system is deployed on **Render** using Docker containers and scheduled background jobs. PostgreSQL is used as the primary data store.

---
