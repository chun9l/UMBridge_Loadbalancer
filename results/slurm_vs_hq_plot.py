import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

job_count = ["2", "10"]
scheduler = ["SLURM", "HQ"]
benchmark = ["eigen_100", "eigen_5000", "gs2", "gp"]
metrics = ["makespan", "CPUTime", "Scheduler Overhead", "SLR"]
data_dict = {}


def set_fill_color(bp, color):
    plt.setp(bp['boxes'], color=color)


for s in scheduler:
    s = s.lower()
    data_dict[s] = {}
    for job in job_count:
        os.chdir(f"/home/ming/{job}jobs")
        data_dict[s][job] = {}
        for m in range(len(metrics)):
            data_dict[s][job][metrics[m]] = {}
            for app in benchmark:
                file = f"{app}-{s}.pkl"
                with open(f"{app}-{s}.pkl", "rb") as h:
                    data = pickle.load(h)
                if m == 0:
                    metric = "makespan"
                elif m == 1:
                    metric = "cpu-time"
                elif m == 2:
                    metric = "lag"
                elif m == 3:
                    metric = "slr"
                data_dict[s][job][metrics[m]][app] = [data[i][metric] for i in data]
os.chdir("/home/ming/slurm_vs_hq/")
for i in range(len(metrics)):
    for job in job_count:
        fig, ax = plt.subplots()
        fig.suptitle(f"{metrics[i]} {job} jobs")
        if i != 3:
            ax.set_ylabel("Time (s)")
        else:
            ax.set_ylabel("Arbitrary units")
        data_slurm = [data_dict[scheduler[0].lower()][job][metrics[i]][app] for app in benchmark]
        data_hq = [data_dict[scheduler[1].lower()][job][metrics[i]][app] for app in benchmark]
        slurm = ax.boxplot(data_slurm, positions=np.array(range(len(data_slurm))) * 2 - 0.4, meanline=True,
                           showmeans=True, meanprops={"linestyle": "--", "color": "black", "linewidth": "1.5"},
                           medianprops={"linestyle": "-", "color": "black", "linewidth": "1.5"})
        hq = ax.boxplot(data_hq, positions=np.array(range(len(data_hq))) * 2.0 + 0.4, meanline=True, showmeans=True,
                        meanprops={"linestyle": "--", "color": "black", "linewidth": "1.5"},
                        medianprops={"linestyle": "-", "color": "black", "linewidth": "1.5"})
        ax.set_xticks(range(0, len(benchmark) * 2, 2), benchmark)
        set_fill_color(slurm, "blue")
        set_fill_color(hq, "red")
        plt.plot([], 'b-', linewidth=1, label="SLURM")
        plt.plot([], 'r-', linewidth=1, label="HQ")
        plt.plot([], 'k-', linewidth=1.5, label="Median")
        plt.plot([], 'k--', linewidth=1.5, label="Mean")
        plt.plot([], 'ko', markerfacecolor='white', label="Fliers")
        if metrics[i] != "SLR":  ax.set_yscale("log")
        plt.legend()
        # plt.show()
        # plt.savefig(f"{metrics[i]}_{job}.pdf", format="pdf")
