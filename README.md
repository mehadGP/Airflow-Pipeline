# Airflow-Pipeline

## Project Description
This project uses **Apache Airflow** with **PySpark** to perform ETL operations on CSV files stored in HDFS.  
The main tasks include:

1. Checking the existence of the source folder on HDFS.
2. Validating that CSV files match the expected schema.
3. Creating a backup of the CSV files.
4. Copying the files to the destination folder on HDFS.
5. Sending an email notification upon successful completion.

---

## Project Structure
```
Airflow-Pipeline/
├── dags/
│   └── airflow_project.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Project Requirements
- Python 3.9 or higher
- Apache Airflow 2.7.0
- PySpark 3.5.0
- Access to HDFS
- Gmail account for sending email notifications (allow less secure apps)

---

## How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Airflow
```bash
# Initialize the Airflow database
airflow db init

# Start the scheduler
airflow scheduler &

# Start the webserver
airflow webserver -p 8080
```

### 3. Add the DAG
Place the `airflow_project.py` file inside the `dags/` folder of your Airflow project.

---

## Usage Scenario

1. Check that the `/user/bank/` folder exists on HDFS.
2. Validate that all CSV files match the expected schema.
3. Copy files to `/user/bank/archive_new/` as a backup.
4. Copy files to `/user/hadoop/destination_csv/` on HDFS.
5. Send a success email once the process completes.
