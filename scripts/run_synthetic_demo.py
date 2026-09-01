from mortgagelab.demo import synthetic_demo
if __name__ == "__main__":
    _, _, metrics = synthetic_demo()
    print("Synthetic demonstration only; no empirical claim.")
    print(metrics)
