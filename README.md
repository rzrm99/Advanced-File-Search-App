# Advanced-File-Search-App
A user-friendly desktop tool that allows users to search for files in a selected directory based on multiple filters:      File name (query string)      File size range (with unit selection: KB, MB, GB)      File extension(s)      Date modified (before and/or after specific dates)


# 🔍 Advanced File Search App

A powerful desktop GUI application to search for files with multiple filters — including name, size, type, and modification date — all wrapped in a clean, responsive interface built with **PyQt5**.

---

## ✨ Features

- 📁 **Directory selection** with easy browsing
- 🔍 **Search by name** (partial or full filename match)
- 🧩 **File extension filter** (e.g., `pdf`, `txt`, `png`)
- 📏 **File size range filter** (in KB, MB, or GB)
- 📆 **Date modified filter** with calendar pickers
- 🧠 **Multithreaded search** – UI remains responsive
- 📋 **Interactive results list**:
  - Open file
  - Open file location
  - Copy file path
- 💾 **Save search results** to a `.txt` file
- 📊 **Real-time progress bar**

---

## 🛠 Requirements

- Python 3.6+
- PyQt5

Install dependencies:

```bash
pip install PyQt5
