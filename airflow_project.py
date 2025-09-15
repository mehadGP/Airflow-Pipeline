from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess
import smtplib
import logging
from email.message import EmailMessage
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, DateType

# -----------------------------
# Default DAG settings
# -----------------------------
default_args = {
    'owner': 'Mehad',
    'start_date': datetime(2025, 9, 15),
    'retries': 1
}

# -----------------------------
# Define DAG
# -----------------------------
dag = DAG(
    'airflow_project',
    default_args=default_args,
    description='Validate CSVs, backup, copy to HDFS, send email',
    schedule_interval=None,
)

# -----------------------------
# Step 1: Check Source Folder in HDFS
# -----------------------------
def check_source_folder():
    source_folder = "/user/bank/"
    result = os.system(f"hdfs dfs -test -d {source_folder}")
    if result != 0:
        raise FileNotFoundError(f"[ERROR] {source_folder} does not exist in HDFS")
    print(f"[OK] Source folder {source_folder} exists in HDFS")

check_folder_task = PythonOperator(
    task_id='check_source_folder',
    python_callable=check_source_folder,
    dag=dag
)

# -----------------------------
# Step 2: Validate CSVs with Spark
# -----------------------------
def validate_csvs():
    spark = SparkSession.builder \
        .appName("Validate CSVs") \
        .master("local[1]") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    expected_schema = StructType([
        StructField("transaction_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("transaction_date", DateType(), True),
        StructField("amount", DoubleType(), True),
        StructField("transaction_type", StringType(), True)
    ])

    source_path = "hdfs:///user/bank/*.csv"
    df = spark.read.csv(source_path, header=True, schema=expected_schema)

    if df.schema != expected_schema:
        raise ValueError(f"[ERROR] Schema of CSV files does NOT match the expected schema!")

    logging.info(f"[OK] All CSV files in HDFS match the expected schema")
    spark.stop()

validate_csv_task = PythonOperator(
    task_id='validate_csvs',
    python_callable=validate_csvs,
    dag=dag
)

# -----------------------------
# Step 3: Backup CSVs in HDFS
# -----------------------------
def backup_csvs():
    source_path = "/user/bank/"
    archive_path = "/user/bank/archive_new0/"
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", archive_path], check=True)

    result = subprocess.run(["hdfs", "dfs", "-ls", source_path], capture_output=True, text=True, check=True)
    files = [line.split()[-1] for line in result.stdout.strip().split("\n") if line.endswith(".csv")]

    for file in files:
        subprocess.run(["hdfs", "dfs", "-cp", file, archive_path], check=True)
        logging.info(f"[BACKUP] {file} copied to archive folder")

backup_task = PythonOperator(
    task_id='backup_csvs',
    python_callable=backup_csvs,
    dag=dag
)

# -----------------------------
# Step 4: Copy CSVs to Destination in HDFS
# -----------------------------
def copy_to_hdfs():
    destination_path = "/user/hadoop/destination0_csv/"
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", destination_path], check=True)
    subprocess.run(["hdfs", "dfs", "-cp", "/user/bank/*.csv", destination_path], check=True)
    logging.info(f"[HDFS] Files copied to {destination_path}")

copy_hdfs_task = PythonOperator(
    task_id='copy_to_hdfs',
    python_callable=copy_to_hdfs,
    dag=dag
)

# -----------------------------
# Step 5: Send Success Email
# -----------------------------
def send_success_email():
    msg = EmailMessage()
    msg.set_content("✅ CSV processing completed successfully and files are copied to HDFS destination.")
    msg['Subject'] = "ETL Process Success"
    msg['From'] = "your_email@gmail.com"
    msg['To'] = "your_email@gmail.com"

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("your_email@gmail.com", "your-app-password")
        server.send_message(msg)

    print("[EMAIL] Success email sent")

send_email_task = PythonOperator(
    task_id='send_success_email',
    python_callable=send_success_email,
    dag=dag
)

# -----------------------------
# Define Task Dependencies
# -----------------------------
check_folder_task >> validate_csv_task >> backup_task >> copy_hdfs_task >> send_email_task