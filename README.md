# 🧑‍💻 Intern Management Dashboard – Streamlit App

A role-based dashboard built using **Streamlit** for managing AI Developer interns and Tech Leads across colleges, including task assignments, progress tracking, and data insights.

---

## 🚀 Features

### 👨‍🏫 Tech Lead Dashboard
- View AI Developers from your college
- Track and manage project issues
- Claim, submit, and complete tasks
- View and respond to help requests
- Raise new issues with difficulty tags
- Visual insights using charts

### 👩‍💻 AI Developer Dashboard *(Pluggable)*
- Claim issues, submit merge requests, and mark tasks as done
- Request help from Tech Leads
- View assigned and completed issues
- Monitor progress with graphs

---

## 📁 Folder Structure
```
intern-dashboard/
│
├── main.py
├── dashboards/
│   ├── tech_lead_dashboard.py
│   └── ai_developer_dashboard.py  # Optional or under development
│
├── data/
│   ├── users.csv
│   ├── issues.csv
│   └── help_requests.csv
│
├── requirements.txt
└── README.md
```
## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/intern-dashboard.git
cd intern-dashboard
```

### 2. Install required Python packages

```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

## 📊 CSV Data Format

### `users.csv`
| name   | email              | college      | role        |
|--------|--------------------|--------------|-------------|
| Alice  | alice@example.com  | XYZ College  | AI Developer |
| Bob    | bob@example.com    | XYZ College  | Tech Lead    |

### `issues.csv`
| id | title           | description         | difficulty | status                | assigned_to         | submitter |
|----|------------------|----------------------|------------|------------------------|----------------------|-----------|
| 1  | Bug in login     | Login not working    | Medium     | Open                   |                      | Alice     |

### `help_requests.csv`
| developer | email             | query                  |
|-----------|-------------------|------------------------|
| Alice     | alice@example.com | Need help with setup   |

## 📦 Requirements

- Python 3.8+
- Streamlit
- Pandas
- Altair

Install them with:

```bash
pip install streamlit pandas altair
```

## 💡 Built With

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Altair](https://altair-viz.github.io/)

## 🧑‍🔧 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.


## 📞 Contact

Built with ❤️ by [Swecha.AI](https://swecha.ai)  
Have ideas or need support? Connect with the team!
