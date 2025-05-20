## 📘 `README.md` — Retention Incentive Simulator


# 🎓 Retention Incentive Simulator

This project models and compares learner retention across multiple scenarios using incentive-based interventions. It combines an interactive **Streamlit app**, a **custom CSV uploader**, and an **explanatory Jupyter notebook** to help decision-makers evaluate the financial and behavioral impact of incentive strategies.

---

## 📂 Project Structure

.
├── main.py                 # Streamlit app for scenario simulation
├── custom\_csv.py          # Streamlit app for CSV-based retention modeling
├── retention\_analysis.ipynb  # Jupyter notebook with visual and financial analysis
├── requirements.txt       # Project dependencies
├── README.md              # You are here
└── sample\_dropoffs.csv    # (Optional) Example custom drop-off input

---

## 🚀 Features

- 📊 Simulates learner retention over time
- 💸 Quantifies revenue, incentive cost, and net financial impact
- 📈 Interactive plots using Plotly
- 📁 Supports custom drop-off CSV uploads
- 🧠 Auto-generated executive recommendations
- 📘 Includes a well-documented analysis notebook

---

## ⚙️ Setup Instructions

### 🐍 1. Clone the repository

```bash
git clone https://github.com/yourusername/retention-incentive-simulator.git
cd retention-incentive-simulator
````

### 🔧 2. Create & activate environment

Using Conda:

```bash
conda create -n stlit_env python=3.9
conda activate stlit_env
pip install -r requirements.txt
```

Or with `venv`:

```bash
python -m venv stlit_env
source stlit_env/bin/activate  # Use `.\stlit_env\Scripts\activate` on Windows
pip install -r requirements.txt
```

---

## 🖥 Run the App

### ✅ Run scenario-based Streamlit simulator

```bash
streamlit run 1_Retention_Incentive_Simulator.py
```

---

## 📓 Open the Jupyter Notebook

```bash
jupyter notebook retention_analysis.ipynb
```


## 🧾 Sample CSV Format for Drop-offs

Upload a CSV like this for the custom scenario:

```csv
Month,Drop-off Rate (%)
1,5
2,5
3,25
4,10
5,10
6,10
7,10
8,10
```

---

## 🧠 Authors & Attribution

* **Author**: \Oludare Adekunle
* Based on assignment from the **ALX Rewards Modelling Specialist Program**
* Developed with ❤️ using Python, Streamlit, and Plotly

---