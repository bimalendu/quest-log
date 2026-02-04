# ⚔️ QuestLog: Gamified Task Planner

QuestLog is a Streamlit-based productivity application that turns your daily to-do list into an RPG game. Earn XP, maintain streaks, and defeat bosses by completing your real-world tasks.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)

## ✨ Features

* **📝 Interactive Task Board:** Edit tasks, times, and completion status on the fly.
* **📅 Calendar View:** Visual timeline of your schedule using `streamlit-calendar`.
* **🔥 Streak System:** Tracks consecutive days of productivity.
* **🛡️ XP & Leveling:** Earn 50 XP per task and level up.
* **👹 Boss Battles:** Summon custom bosses (e.g., "The Thesis Monster") and deal damage by finishing tasks.
* **💾 Save/Load System:** Export your game state to JSON and restore it anytime.

## 🚀 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/bimalendu/quest-log.git](https://github.com/bimalendu/quest-log.git)
    cd quest-log
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🧪 Running Tests

This project uses `pytest` to ensure the gamification logic (Streaks, XP, Boss Math) is accurate.

```bash
pytest test_app.py
```

## 🏗️ Architecture
The codebase follows SOLID principles and Clean Architecture:

GamificationService: Pure logic for stats and streaks (Business Layer).

StateRepository: Handles DataFrames and JSON serialization (Data Layer).

UI: Handles Streamlit rendering (Presentation Layer).

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
MIT