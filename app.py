from flask import Flask, render_template, request
import pandas as pd
from io import TextIOWrapper
import numpy as np

app = Flask(__name__)

last_rep_col_users = None  # Keep track of rep column name for CSV export

# --- Column detection helpers ---
def detect_column(df, possible_names):
    for col in df.columns:
        if any(name.lower() in col.lower() for name in possible_names):
            return col
    return None

def detect_rep_column(df):
    return detect_column(df, ["Sale Rep", "Rep", "SalesRep", "Agent"])

def detect_team_column(df):
    return detect_column(df, ["Team", "Team Name", "Sales Team"])

def detect_manager_column(df):
    return detect_column(df, ["Manager", "Sales Manager"])

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    global last_rep_col_users
    report_data = None
    error = None

    if request.method == "POST":
        try:
            # Read uploaded files
            raw_file = request.files.get("raw_csv")
            users_file = request.files.get("users_csv")
            if not raw_file or not users_file:
                raise ValueError("Please upload both required CSV files.")

            raw_df = pd.read_csv(TextIOWrapper(raw_file, encoding='utf-8'))
            users_df = pd.read_csv(TextIOWrapper(users_file, encoding='utf-8'))

            # Detect columns
            rep_col_raw = detect_rep_column(raw_df)
            rep_col_users = detect_rep_column(users_df)
            team_col = detect_team_column(users_df)
            manager_col = detect_manager_column(users_df)

            if not rep_col_raw or not rep_col_users:
                raise ValueError("Could not find a Sales Rep column in one of the files.")

            last_rep_col_users = rep_col_users

            # Count installs per rep
            rep_counts = raw_df[rep_col_raw].value_counts().reset_index()
            rep_counts.columns = ["Rep", "Installs"]

            # Merge with user data
            merged = pd.merge(users_df, rep_counts, how="left",
                              left_on=rep_col_users, right_on="Rep")
            merged["Installs"] = merged["Installs"].fillna(0).astype(int)

            merged[rep_col_users] = merged[rep_col_users].replace({np.nan: None})
            if manager_col:
                merged[manager_col] = merged[manager_col].replace({np.nan: None})

            # Top reps (excluding 0 installs)
            top_reps = merged[merged["Installs"] > 0].sort_values(
                "Installs", ascending=False
            )

            # Zero install reps
            zero_reps = merged[merged["Installs"] == 0].sort_values(rep_col_users)

            # Team breakdown
            team_breakdown = []
            if team_col and manager_col:
                for team_name, team_df in merged.groupby(team_col):
                    manager = team_df[manager_col].iloc[0]
                
                    # 🚫 Skip Michael Grabowski and his team
                    if str(manager).strip().lower() == "michael grabowski".lower():
                        continue
                
                    manager_installs = team_df.loc[
                        team_df[rep_col_users] == manager, "Installs"
                    ].sum()
                
                    total_team_installs = team_df["Installs"].sum()
                
                    reps_sorted = team_df[
                        team_df[rep_col_users] != manager
                    ].sort_values("Installs", ascending=False)[[rep_col_users, "Installs"]]
                    reps_sorted = reps_sorted.rename(columns={rep_col_users: "Rep"})  # normalize column
                    reps_sorted = reps_sorted.replace({np.nan: None})
                
                    team_breakdown.append({
                        "team": team_name,
                        "manager": manager,
                        "manager_installs": int(manager_installs) if pd.notna(manager_installs) else 0,
                        "total": int(total_team_installs),
                        "reps": reps_sorted.to_dict(orient="records")
                    })

            report_data = {
                "top_reps": top_reps.replace({np.nan: None}).to_dict(orient="records"),
                "zero_reps": [z if z else "" for z in zero_reps[rep_col_users].tolist()],
                "team_breakdown": team_breakdown
            }

        except Exception as e:
            error = str(e)

    return render_template("index.html", report_data=report_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
