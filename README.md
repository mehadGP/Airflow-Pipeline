# 🚀 Airflow CSV ETL Project

## 📌 Project Description
This project uses **Apache Airflow** with **PySpark** to perform ETL operations on CSV files stored in HDFS.  
The main tasks include:

1️⃣ Checking the existence of the source folder on HDFS.  
2️⃣ Validating that CSV files match the expected schema.  
3️⃣ Creating a backup of the CSV files.  
4️⃣ Copying the files to the destination folder on HDFS.  
5️⃣ Sending an email notification upon successful completion.  

---

## ⚙️ How Airflow Works with This Project

- **🗄️ Airflow Database**:  
  Airflow uses a database (SQLite by default) to track **DAGs** and **task instances**.  
  It stores metadata like task status (✅ success, ❌ failed, ⏳ running) and execution timestamps.  
  It does **not store CSV data**; data remains in HDFS.

- **📂 HDFS**:  
  Used to store CSV files, archive copies, and destination files.  
  Airflow and Spark only read/write data from/to HDFS.

- **⚡ Spark**:  
  Used to process CSV files, validate schema, and transform data if needed.  
  The Spark job is called from Airflow via `PythonOperator`.

---

## 📁 Project Structure
```
Airflow-Pipeline/
├── dags/
│   └── airflow_project.py       # DAG code calling Spark and HDFS operations
├── requirements.txt             # Python dependencies
├── README.md                    # Project description and usage scenario
```

---

## How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Airflow Database
```bash
airflow db init
```
- Initializes the Airflow database to track DAGs and task instances.
- Required before running any DAGs.

### 3. Run Airflow
```bash
# Start scheduler
airflow scheduler 

# Start webserver
airflow webserver -p 8080
```

### 4. Add the DAG
Place `airflow_project.py` in the `dags/` folder.

### 5. Usage Scenario
1. Airflow checks that `/user/bank/` exists on HDFS.
2. Spark validates that CSV files match the expected schema.
3. Airflow backs up files to `/user/bank/archive_new/`.
4. Airflow copies files to `/user/hadoop/destination_csv/`.
5. Airflow sends a success email notification.

---

## Important Notes
- Airflow tracks only **task execution and status**, not actual CSV data.
- Spark reads/writes data from HDFS.
- Ensure Gmail allows less secure apps for email notifications.
- Modify HDFS paths in the DAG according to your environment.
