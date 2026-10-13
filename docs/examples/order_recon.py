from airflow.sdk import DAG
import datetime as _dq_dt
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.standard.operators.email import EmailOperator


def extract_orders():
    print("extract orders")


def choose_path():
    return "recon_fast"


with DAG(dag_id="order_recon", schedule="17 9 * * *",
         start_date=_dq_dt.datetime(2026, 1, 1), catchup=False) as dag:
    start = EmptyOperator(task_id="start")
    extract = PythonOperator(task_id="extract_orders", python_callable=extract_orders)
    branch = BranchPythonOperator(task_id="choose_path", python_callable=choose_path)
    recon_fast = BashOperator(task_id="recon_fast", bash_command="python /jobs/recon.py --mode fast")
    recon_full = BashOperator(task_id="recon_full", bash_command="python /jobs/recon.py --mode full")
    notify = EmailOperator(task_id="notify_team", to=["data-team@example.com"], subject="recon done", html_content="done")
    end = EmptyOperator(task_id="end")

    start >> extract >> branch
    branch >> [recon_fast, recon_full]
    [recon_fast, recon_full] >> notify >> end
