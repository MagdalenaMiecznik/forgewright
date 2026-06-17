"""
Forgewright Manufacturing CNC Tool-Wear Analysis

Starter scaffold. Fill in the stages. You're free to restructure entirely —
this is just a starting point so the repo runs from a single command.

Usage:
    python src/analyze.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 


def load_data(data_dir: str = "data"):
    """Load the three source files."""
    power = pd.read_csv(f"{data_dir}/power.csv")
    vibration = pd.read_csv(f"{data_dir}/vibration.csv")
    production_log = pd.read_csv(f"{data_dir}/production_log.csv")
    return power, vibration, production_log


def _get_the_subset(df: pd.DataFrame, machine_id: str, job_id: str, part_type: str, start_time: str, end_time: str) -> pd.DataFrame:
    """
    Get the subset of the dataframe based on the given parameters.

    Args:
        df (pd.DataFrame): The dataframe to filter.
        machine_id (str): The machine ID to filter by.
        job_id (str): The job ID to filter by.
        part_type (str): The part type to filter by.
        start_time (str): The start time to filter by.
        end_time (str): The end time to filter by.

    Returns:
        pd.DataFrame: The filtered dataframe.
    """
    return df[(df['machine_id'] == machine_id) & 
              (df['job_id'] == job_id) & 
              (df['part_type'] == part_type) & 
              (df['start_time'] == start_time) & 
              (df['end_time'] == end_time)].sort_values(by='timestamp_vibration').reset_index(drop=True)



def integrate(power, vibration, production_log):
    """
    Combine the three sources so you can compute per-job metrics.
    """
    # unify datetime columns
    power['timestamp'] = pd.to_datetime(power['timestamp'])
    production_log['start_time'] = pd.to_datetime(production_log['start_time'])
    production_log['end_time'] = pd.to_datetime(production_log['end_time'])
    vibration['timestamp'] = pd.to_datetime(vibration['timestamp'])
    production_log['start_time'] = production_log['start_time'].dt.tz_localize('UTC')
    production_log['end_time'] = production_log['end_time'].dt.tz_localize('UTC')

    # merge power and production
    df_power_and_production = power.merge(production_log, on = ['machine_id'])

    # filter out records with consistent time ranges
    df_power_and_production_filtered = df_power_and_production[(df_power_and_production['timestamp']>=df_power_and_production['start_time']) & (df_power_and_production['timestamp']<=df_power_and_production['end_time'])]

    # merge vibration
    df_power_and_production_and_vibration = df_power_and_production_filtered.merge(vibration, on = ['machine_id'], suffixes=('_power', '_vibration'))

    # filter against datetime
    df_power_and_production_and_vibration_filtered = df_power_and_production_and_vibration[(df_power_and_production_and_vibration['timestamp_vibration']>=df_power_and_production_and_vibration['start_time']) & (df_power_and_production_and_vibration['timestamp_vibration']<=df_power_and_production_and_vibration['end_time'])]

    # remove outliers -> most prbably missing values replacmented with 9999
    df_power_and_production_and_vibration_filtered = df_power_and_production_and_vibration_filtered[df_power_and_production_and_vibration_filtered['power_kw']<9999]

    job_configs = list(df_power_and_production_and_vibration_filtered[['machine_id','job_id','part_type','start_time','end_time']].value_counts().index)

    return df_power_and_production_and_vibration_filtered, job_configs


def explore(integrated, job_configs):
    """
    Look at the data before doing anything else.
    """
    for i in range(len(job_configs)):
        machine_id = job_configs[i][0]
        job_id = job_configs[i][1]
        part_type = job_configs[i][2]
        start_time = job_configs[i][3]
        end_time = job_configs[i][4]

        df_job = _get_the_subset(integrated, machine_id, job_id, part_type, start_time, end_time)

        g = sns.pairplot(df_job[['power_kw','vibration_rms_g','vibration_peak_g']])
        g.savefig(f"plots/pairplot_results_{job_id}.png", dpi=300, bbox_inches="tight")
    pass


def _calculate_outliers(df_job):
    # 1. Calculate quantails Q1 (25%) i Q3 (75%)
    Q1 = df_job['power_kw'].quantile(0.25)
    Q3 = df_job['power_kw'].quantile(0.75)

    # 2. Calcluate  (IQR)
    IQR = Q3 - Q1

    # 3. Set boundaries
    # lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # 4.We want to detect too high power consumption
    outliers = df_job[
        (df_job['power_kw'] > upper_bound)
    ]
    return outliers.shape[0]

def compute_job_metrics(integrated, job_configs):
    """
    For each job: average power draw, peak vibration, and whatever else you
    need to assess tool wear.
    """

    metrics = {}
    avg_powers = []
    numer_of_outliers_in_power = []
    flagged_jobs = []
    ranked_jobs = []
    peak_vibrations = []

    for i in range(len(job_configs)):
        machine_id = job_configs[i][0]
        job_id = job_configs[i][1]
        part_type = job_configs[i][2]
        start_time = job_configs[i][3]
        end_time = job_configs[i][4]

        df_job = _get_the_subset(integrated, machine_id, job_id, part_type, start_time, end_time)

        # get outliers in power consumtion as a potential indicator of tool wear
        outliers = _calculate_outliers(df_job)
        numer_of_outliers_in_power.append(outliers)

        avg_power = round(df_job.power_kw.mean(),2)
        avg_powers.append(avg_power)
        if outliers > 0:
            flagged_jobs.append(True)
        else:            
            flagged_jobs.append(False)
        
        if outliers ==0:
            ranked_jobs.append(1)
        elif outliers/df_job.shape[0] <= 0.005:
            ranked_jobs.append(2)
        else:
            ranked_jobs.append(3)

        peak_vibrations.append(np.max(df_job['vibration_peak_g']))

    jobs = [job_configs[i][1] for i in range(len(job_configs))]
    machines = [job_configs[i][0] for i in range(len(job_configs))]

    metrics['job_id'] = jobs
    metrics['machine_id'] = machines
    metrics['avg_power_kw'] = avg_powers
    metrics['peak_vibration_g'] = peak_vibrations
    metrics['number_of_outliers_in_power'] = numer_of_outliers_in_power
    metrics['flagged_for_tool_wear'] = flagged_jobs
    metrics['rank'] = ranked_jobs

    return pd.DataFrame(metrics)


# def detect_tool_wear(job_metrics):
#     """
#     Identify jobs with elevated vibration relative to power.
#     Return a ranked list.
#     """
#     pass



