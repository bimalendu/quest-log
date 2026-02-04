import pytest
import pandas as pd
from datetime import date, timedelta
from app import GamificationService, BossManager

# --- Fixtures ---
@pytest.fixture
def empty_tasks():
    return pd.DataFrame(columns=["Title", "Date", "Status"])

@pytest.fixture
def one_completed_task():
    return pd.DataFrame([{"Title": "Test", "Date": date.today(), "Status": True}])

# --- XP Tests ---
def test_calculate_stats_zero_xp(empty_tasks):
    stats = GamificationService.calculate_stats(empty_tasks, boss_xp=0)
    assert stats['xp'] == 0
    assert stats['level'] == 1

def test_calculate_stats_task_xp(one_completed_task):
    stats = GamificationService.calculate_stats(one_completed_task, boss_xp=0)
    assert stats['xp'] == 50

# --- Streak Tests ---
def test_streak_today_only(one_completed_task):
    assert GamificationService.calculate_streak(one_completed_task) == 1

def test_streak_broken_gap():
    today = date.today()
    three_days_ago = today - timedelta(days=3)
    df = pd.DataFrame([
        {"Date": today, "Status": True},
        {"Date": three_days_ago, "Status": True},
    ])
    assert GamificationService.calculate_streak(df) == 1

# --- Boss Tests ---
def test_boss_damage():
    boss = {"Name": "Test Boss", "MaxHP": 100, "CurrentHP": 100}
    updated_boss, dmg = BossManager.deal_damage(boss, 2)
    assert dmg == 20
    assert updated_boss['CurrentHP'] == 80