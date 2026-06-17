from src.analyze import load_data, explore, integrate, compute_job_metrics


def main():
    power, vibration, production_log = load_data()
    integrated, job_configs = integrate(power, vibration, production_log)

    explore(integrated, job_configs)    
    job_metrics = compute_job_metrics(integrated, job_configs)
    print(job_metrics)
    job_metrics.to_csv("output/job_metrics.csv", index=False)


if __name__ == "__main__":
    main()