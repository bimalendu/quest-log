import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional, Any
from streamlit_calendar import calendar

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
class GameConfig:
    XP_PER_TASK = 50
    BOSS_DMG_PER_TASK = 10
    LEVEL_BASE_XP = 500
    BOSS_BONUS_XP = 500
    
    DEFAULT_TASK = {
        "Title": "Install Streamlit", 
        "Description": "pip install streamlit", 
        "Date": date.today(), 
        "Start": time(9, 0), 
        "End": time(10, 0), 
        "Status": True, 
        "Color": "#33B679"
    }

# ==========================================
# 2. DOMAIN MODEL & LOGIC (Service Layer)
# ==========================================
class GamificationService:
    """Handles XP, Levels, and Streak Logic. Pure Python, no UI code."""
    
    @staticmethod
    def calculate_stats(df: pd.DataFrame, boss_xp: int) -> Dict[str, Any]:
        completed_count = df['Status'].sum() if not df.empty else 0
        current_xp = (completed_count * GameConfig.XP_PER_TASK) + boss_xp
        level = (current_xp // GameConfig.LEVEL_BASE_XP) + 1
        progress = (current_xp % GameConfig.LEVEL_BASE_XP) / GameConfig.LEVEL_BASE_XP
        
        return {
            "xp": current_xp,
            "level": level,
            "progress": progress
        }

    @staticmethod
    def calculate_streak(df: pd.DataFrame) -> int:
        """Calculates consecutive days ending today or yesterday."""
        if df.empty: return 0
        
        # Filter for completed tasks only
        completed = df[df['Status'] == True]
        if completed.empty: return 0
        
        # Get unique dates sorted descending
        dates = sorted(completed['Date'].unique(), reverse=True)
        
        today = date.today()
        if not dates: return 0
        
        # Streak broken if last task was before yesterday
        if (today - dates[0]).days > 1: return 0
        
        streak = 1
        current_date = dates[0]
        
        for i in range(1, len(dates)):
            if (current_date - dates[i]).days == 1:
                streak += 1
                current_date = dates[i]
            else:
                break
        return streak

class BossManager:
    """Manages Boss state and combat logic."""
    @staticmethod
    def deal_damage(boss: Dict, hit_count: int) -> tuple[Dict, int]:
        """Deals damage and returns (updated_boss, damage_dealt)."""
        damage = hit_count * GameConfig.BOSS_DMG_PER_TASK
        boss['CurrentHP'] -= damage
        return boss, damage

# ==========================================
# 3. DATA PERSISTENCE (Repository Layer)
# ==========================================
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time)):
            return obj.isoformat()
        return super().default(obj)

class StateRepository:
    """Handles saving/loading and Session State management."""
    
    @staticmethod
    def initialize_session():
        if 'tasks' not in st.session_state:
            st.session_state.tasks = pd.DataFrame([GameConfig.DEFAULT_TASK])
        if 'boss_xp' not in st.session_state:
            st.session_state.boss_xp = 0
        if 'active_boss' not in st.session_state:
            st.session_state.active_boss = None

    @staticmethod
    def export_data() -> str:
        data = {
            "tasks": st.session_state.tasks.to_dict(orient="records"),
            "boss_xp": st.session_state.boss_xp,
            "active_boss": st.session_state.active_boss
        }
        return json.dumps(data, cls=DateEncoder)

    @staticmethod
    def load_data(json_data: Dict):
        try:
            st.session_state.boss_xp = json_data.get("boss_xp", 0)
            st.session_state.active_boss = json_data.get("active_boss", None)
            
            tasks = json_data.get("tasks", [])
            if tasks:
                df = pd.DataFrame(tasks)
                df['Date'] = df['Date'].apply(lambda x: date.fromisoformat(x))
                df['Start'] = df['Start'].apply(lambda x: time.fromisoformat(x))
                df['End'] = df['End'].apply(lambda x: time.fromisoformat(x))
                st.session_state.tasks = df
            else:
                st.session_state.tasks = pd.DataFrame(columns=GameConfig.DEFAULT_TASK.keys())
            
            st.success("✅ Save file loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Corrupt save file: {str(e)}")

# ==========================================
# 4. UI COMPONENTS (Presentation Layer)
# ==========================================
class UI:
    
    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.title("💾 System")
            
            # Save/Load
            json_str = StateRepository.export_data()
            st.download_button("📥 Save Game", json_str, f"questlog_{date.today()}.json", "application/json")
            
            uploaded = st.file_uploader("📤 Load Game", type=["json"])
            if uploaded and st.button("Restore"):
                StateRepository.load_data(json.load(uploaded))
            
            st.divider()
            
            # Add Task Form
            st.header("➕ New Quest")
            with st.form("new_quest"):
                title = st.text_input("Title")
                desc = st.text_area("Details")
                d = st.date_input("Date", date.today())
                t_s = st.time_input("Start", time(9,0))
                t_e = st.time_input("End", time(10,0))
                color = st.color_picker("Color", "#3788d8")
                
                if st.form_submit_button("Add"):
                    new_row = {"Title": title, "Description": desc, "Date": d, "Start": t_s, "End": t_e, "Status": False, "Color": color}
                    st.session_state.tasks = pd.concat([st.session_state.tasks, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Added!")
            
            # Boss Form
            st.header("👹 Boss")
            if not st.session_state.active_boss:
                with st.form("summon"):
                    name = st.text_input("Name", "Entropy Dragon")
                    hp = st.slider("HP", 50, 500, 100)
                    if st.form_submit_button("Summon"):
                        st.session_state.active_boss = {"Name": name, "MaxHP": hp, "CurrentHP": hp, "Image": "🐉"}
                        st.rerun()
            else:
                if st.button("Flee Battle"):
                    st.session_state.active_boss = None
                    st.rerun()

    @staticmethod
    def render_hud(stats: Dict, streak: int):
        c1, c2, c3, c4 = st.columns([1, 1, 3, 1])
        c1.metric("🛡️ Level", stats['level'])
        c2.metric("🔥 Streak", f"{streak} Days")
        with c3:
            st.write(f"**XP Progress ({stats['xp']} / {stats['level'] * GameConfig.LEVEL_BASE_XP})**")
            st.progress(stats['progress'])
        c4.metric("✨ XP", stats['xp'])

    @staticmethod
    def render_boss_arena():
        boss = st.session_state.active_boss
        if not boss: return

        st.markdown("---")
        b1, b2 = st.columns([1, 6])
        with b1: st.markdown(f"<h1 style='text-align: center;'>{boss['Image']}</h1>", unsafe_allow_html=True)
        with b2:
            st.subheader(f"⚔️ BOSS: {boss['Name']}")
            hp_pct = max(0, boss['CurrentHP'] / boss['MaxHP'])
            st.progress(hp_pct)
            st.caption(f"HP: {boss['CurrentHP']} / {boss['MaxHP']}")

        if boss['CurrentHP'] <= 0:
            st.balloons()
            st.success(f"🏆 VICTORY! +{GameConfig.BOSS_BONUS_XP} XP!")
            st.session_state.boss_xp += GameConfig.BOSS_BONUS_XP
            st.session_state.active_boss = None
            st.button("Collect Loot")

    @staticmethod
    def render_task_editor():
        st.subheader("📝 Quest Log")
        
        col_config = {
            "Title": st.column_config.TextColumn(required=True),
            "Status": st.column_config.CheckboxColumn(help="Mark done for XP"),
            "Color": st.column_config.ColorPickerColumn()
        }
        
        edited_df = st.data_editor(
            st.session_state.tasks,
            column_config=col_config,
            use_container_width=True,
            num_rows="dynamic",
            key="quest_editor"
        )
        return edited_df

    @staticmethod
    def render_calendar():
        st.subheader("📅 Timeline")
        events = []
        for _, row in st.session_state.tasks.iterrows():
            events.append({
                "title": f"{'✅' if row['Status'] else '⬜'} {row['Title']}",
                "start": datetime.combine(row['Date'], row['Start']).isoformat(),
                "end": datetime.combine(row['Date'], row['End']).isoformat(),
                "backgroundColor": row['Color'],
                "borderColor": row['Color'],
            })
        
        calendar(
            events=events, 
            options={
                "initialView": "timeGridWeek", 
                "headerToolbar": {"left": "prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"}
            }
        )

# ==========================================
# 5. MAIN CONTROLLER
# ==========================================
def main():
    st.set_page_config(page_title="QuestLog", page_icon="⚔️", layout="wide")
    
    StateRepository.initialize_session()
    UI.render_sidebar()
    
    stats = GamificationService.calculate_stats(st.session_state.tasks, st.session_state.boss_xp)
    streak = GamificationService.calculate_streak(st.session_state.tasks)
    
    UI.render_hud(stats, streak)
    UI.render_boss_arena()
    
    new_df = UI.render_task_editor()
    
    if not new_df.equals(st.session_state.tasks):
        old_completed = st.session_state.tasks['Status'].sum()
        new_completed = new_df['Status'].sum()
        
        st.session_state.tasks = new_df
        
        if new_completed > old_completed:
            diff = new_completed - old_completed
            st.toast(f"Quest Complete! +{diff * GameConfig.XP_PER_TASK} XP")
            
            if st.session_state.active_boss:
                boss, dmg = BossManager.deal_damage(st.session_state.active_boss, diff)
                st.session_state.active_boss = boss
                st.toast(f"⚔️ Critical Hit! -{dmg} HP")
        
        st.rerun()

    st.divider()
    UI.render_calendar()

if __name__ == "__main__":
    main()