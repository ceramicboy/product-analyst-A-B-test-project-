from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "charts"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    "A": "#667085",
    "B": "#0F766E",
    "accent": "#D97706",
    "grid": "#E4E7EC",
    "text": "#1D2939",
}


def save_figure(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.labelcolor": COLORS["text"],
        "xtick.color": COLORS["text"],
        "ytick.color": COLORS["text"],
        "text.color": COLORS["text"],
        "axes.edgecolor": COLORS["grid"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": COLORS["grid"],
        "grid.linewidth": 0.8,
        "axes.grid.axis": "y",
    }
)


# 1. Main conversion comparison.
groups = ["A\nКонтроль", "B\nАвтозаполнение"]
conversion = [65.78, 80.40]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(groups, conversion, color=[COLORS["A"], COLORS["B"]], width=0.58)
ax.set_title("Конверсия в успешную оплату")
ax.set_ylabel("Конверсия, %")
ax.set_ylim(0, 100)
for bar, value in zip(bars, conversion):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 2,
        f"{value:.1f}%",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
ax.text(
    0.98,
    0.06,
    "Эффект: +14,62 п.п. | uplift: +22,2%",
    transform=ax.transAxes,
    ha="right",
    color=COLORS["accent"],
    fontsize=10,
)
save_figure("conversion_comparison.png")


# 2. Normalized funnel by experiment group.
steps = ["Открытие", "Ввод\nреквизитов", "Подтверждение", "Успешная\nоплата"]
funnel_a = [100.0, 89.5, 89.5 * 81.7 / 100, 65.78]
funnel_b = [100.0, 94.3, 94.3 * 91.1 / 100, 80.40]

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(steps, funnel_a, marker="o", markersize=7, linewidth=2.5, color=COLORS["A"], label="A: контроль")
ax.plot(steps, funnel_b, marker="o", markersize=7, linewidth=2.5, color=COLORS["B"], label="B: автозаполнение")
ax.set_title("Воронка оплаты относительно открывших форму")
ax.set_ylabel("Доля пользователей, %")
ax.set_ylim(0, 105)
ax.legend(frameon=False, loc="lower left")
for x, value in enumerate(funnel_b):
    ax.annotate(f"{value:.1f}%", (x, value), xytext=(0, 10), textcoords="offset points", ha="center", color=COLORS["B"])
save_figure("funnel_comparison.png")


# 3. Effect size with confidence interval.
effect = 14.62
ci_low = 10.20
ci_high = 19.05

fig, ax = plt.subplots(figsize=(8, 2.8))
ax.errorbar(
    effect,
    0,
    xerr=[[effect - ci_low], [ci_high - effect]],
    fmt="o",
    markersize=9,
    capsize=7,
    linewidth=2.5,
    color=COLORS["B"],
)
ax.axvline(0, color=COLORS["A"], linewidth=1.2, linestyle="--")
ax.set_yticks([0])
ax.set_yticklabels(["Разница B - A"])
ax.set_xlabel("Абсолютный эффект, процентные пункты")
ax.set_title("Оценка эффекта и 95%-й доверительный интервал")
ax.set_xlim(0, 22)
ax.set_ylim(-0.45, 0.45)
ax.text(effect, 0.18, "+14,62 п.п.", ha="center", color=COLORS["B"], fontweight="bold")
ax.text(ci_low, -0.22, "+10,2", ha="center", color=COLORS["text"], fontsize=9)
ax.text(ci_high, -0.22, "+19,0", ha="center", color=COLORS["text"], fontsize=9)
fig.subplots_adjust(left=0.24, right=0.98, top=0.78, bottom=0.30)
fig.savefig(OUTPUT_DIR / "effect_confidence_interval.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close(fig)


# 4. Step-level conversion uplift.
labels = ["Открытие → ввод", "Ввод → подтверждение", "Подтверждение → успех"]
uplift = [4.8, 9.4, 3.6]

fig, ax = plt.subplots(figsize=(8.5, 4.6))
bars = ax.barh(labels, uplift, color=[COLORS["B"], COLORS["accent"], COLORS["B"]], height=0.52)
ax.set_title("Прирост конверсии на отдельных этапах")
ax.set_xlabel("Разница между B и A, п.п.")
ax.set_xlim(0, 11)
for bar, value in zip(bars, uplift):
    ax.text(value + 0.25, bar.get_y() + bar.get_height() / 2, f"+{value:.1f} п.п.", va="center", fontweight="bold")
save_figure("step_uplift.png")

