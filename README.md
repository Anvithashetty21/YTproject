# YouTube Data Harvesting and Warehousing Project

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-App-red) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen) ![SQL Server](https://img.shields.io/badge/SQL-Server-orange)

## 📋 Project Overview

This project is an end-to-end **YouTube Data Harvesting and Warehousing** solution built using **Python**, **Streamlit**, **MongoDB**, and **SQL Server**.
It allows you to:

* ✅ Extract channel, video, and comment data from the YouTube API.
* ✅ Store raw JSON data in **MongoDB Atlas** (Data Lake).
* ✅ Migrate selected channel data from **MongoDB** to **SQL Server** (Data Warehouse).
* ✅ Perform analytics and visualizations via an interactive **Streamlit** app.

---

## ⚡️ Features

* ✅ Enter YouTube Channel ID(s) to fetch and save data.
* ✅ Extract channel statistics, video metadata, and comments.
* ✅ Store data in **MongoDB Atlas**.
* ✅ Export data to **SQL Server** for relational analytics.
* ✅ Run built-in SQL queries for:

  * Most viewed videos and their channel names
  * Videos with the highest likes and comments
  * Channels with the most videos
  * Average video duration across channels
  * Channels that published in a specific year
* ✅ Interactive Streamlit app for seamless exploration.

---

## 🛠️ Tech Stack

* **Backend**: Python, Pandas, SQLAlchemy
* **Database**: MongoDB Atlas (Data Lake), SQL Server (Data Warehouse)
* **UI Framework**: Streamlit
* **Deployment**: Local / Streamlit Cloud

---

## ⚡️ Getting Started

### Prerequisites

* Python 3.9+
* YouTube API Key
* SQL Server + ODBC Driver
* MongoDB Atlas Account

### Install Dependencies

```bash
pip install streamlit pandas pymongo sqlalchemy pyodbc streamlit-option-menu
```

---

### 👇 Directory Structure

```
youtube_data_harvesting/
├─ app.py               # Main Streamlit app
├─ youtube_utils.py      # YouTube, MongoDB & SQL utilities
├─ requirements.txt
├─ README.md
```

---

### 🚀 Usage

1️⃣ Run Streamlit App:

```bash
streamlit run app.py
```

2️⃣ Enter one or more YouTube Channel ID(s) to fetch & save data in **MongoDB**.
3️⃣ Migrate selected channel data from **MongoDB** ➔ **SQL Server**.
4️⃣ Perform SQL queries via Streamlit for analytics.

---

## 🎥 Demo Video

👉 [Watch Demo Here](https://www.linkedin.com/posts/anvitha-shetty-82852718b_youtube-data-harvesting-and-warehousing-activity-7343306701833457664-7Edl)

---

## 🌟 Skills Gained

✅ Python Scripting
✅ YouTube API Integration
✅ MongoDB Atlas (Data Lake)
✅ SQL Server (Data Warehouse)
✅ Streamlit Development
✅ End-to-End Data Architecture & Analysis

---

## 📋 Project Evaluation

✅ Maintainable and Modular Architecture
✅ Created Detailed Documentation and Demo Video
✅ Enables Interactive SQL Analysis via Streamlit
✅ Provides End-to-End Solution from Data Ingestion to Visualization

---

## 🙌 Acknowledgements

Developed as a Capstone Project for the **Master Data Science Program** by GUVI.
Thank you for checking out this project!
Connect with me:

* 💼 [LinkedIn](https://www.linkedin.com/in/anvitha-shetty/)
* 💻 [GitHub]((https://github.com/Anvithashetty21))



