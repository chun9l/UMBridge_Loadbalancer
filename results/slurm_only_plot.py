import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

job_count = ["2", "10"]
scheduler = ["SLURM", "SLURM_UM"]
benchmark = ["gs2"]
metrics = ["makespan", "CPUTime", "Scheduler Overhead", "SLR"]
data_dict = {}


def set_fill_color(bp, color):
    plt.setp(bp['boxes'], color=color)


for s in scheduler:
    s = s.lower()
    data_dict[s] = {}
    for job in job_count:
        data_dict[s][job] = {}
        if s == "slurm_um":
            os.chdir(f"/home/ming/UMBridge_Loadbalancer/results/raw_data/umbridge/{s}/{job}jobs")
        else:
            os.chdir(f"/home/ming/UMBridge_Loadbalancer/results/raw_data/{s}/{job}jobs")
        for m in range(len(metrics)):
            data_dict[s][job][metrics[m]] = {}
            for app in benchmark:
                file = f"{app}_{s}.pkl"
                with open(f"{app}_{s}.pkl", "rb") as h:
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
for i in range(len(metrics)):
    for job in job_count:
        fig, ax = plt.subplots()
        fig.suptitle(f"{metrics[i]} {job} jobs")
        if i != 3:
            ax.set_ylabel("Time (s)")
        else:
            ax.set_ylabel("Arbitrary units")
        data_slurm = [data_dict[scheduler[0].lower()][job][metrics[i]][app] for app in benchmark]
        data_slurm_um = [data_dict[scheduler[1].lower()][job][metrics[i]][app] for app in benchmark]
        slurm = ax.boxplot(data_slurm, positions=np.array(range(len(data_slurm))) * 2 - 0.15, meanline=True,
                           showmeans=True, meanprops={"linestyle": "--", "color": "black", "linewidth": "1.5"},
                           medianprops={"linestyle": "-", "color": "black", "linewidth": "1.5"})
        slurm_um = ax.boxplot(data_slurm_um, positions=np.array(range(len(data_slurm_um))) * 2.0 + 0.15, meanline=True, showmeans=True,
                        meanprops={"linestyle": "--", "color": "black", "linewidth": "1.5"},
                        medianprops={"linestyle": "-", "color": "black", "linewidth": "1.5"})
        ax.set_xticks(range(0, len(benchmark) * 2, 2), benchmark)
        set_fill_color(slurm, "blue")
        set_fill_color(slurm_um, "darkviolet")
        plt.plot([], 'b-', linewidth=1, label="SLURM")
        plt.plot([], '-', color='darkviolet', linewidth=1, label="SLURM_UM")
        plt.plot([], 'k-', linewidth=1.5, label="Median")
        plt.plot([], 'k--', linewidth=1.5, label="Mean")
        plt.plot([], 'ko', markerfacecolor='white', label="Fliers")
        if metrics[i] != "SLR":  ax.set_yscale("log")
        plt.legend()
        # plt.show()
        plt.savefig(f"/home/ming/UMBridge_Loadbalancer/results/plots/slurm/{metrics[i]}_{job}.pdf", format="pdf")
