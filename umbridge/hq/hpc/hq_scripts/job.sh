#! /bin/bash
#HQ --nodes=1
#HQ --time-limit=5m
#HQ --time-request=1m

# Launch model server, send back server URL
# and wait to ensure that HQ won't schedule any more jobs to this allocation.

function get_available_port {
    # Define the range of ports to select from
    MIN_PORT=1024
    MAX_PORT=65535

    # Generate a random port number
    port=$(shuf -i $MIN_PORT-$MAX_PORT -n 1)

    # Check if the port is in use
    until ./is_port_free $port; do
        # If the port is in use, generate a new random port number
        port=$(shuf -i $MIN_PORT-$MAX_PORT -n 1)
    done

    echo $port
}


# Assume that server sets the port according to the environment variable 'PORT'.
. /home/mghw54/.bashrc
conda activate python3.9
# module load gcc openmpi

unset SLURM_CPU_BIND SLURM_CPU_BIND_VERBOSE SLURM_CPU_BIND_LIST SLURM_CPU_BIND_TYPE
export PYTHONUNBUFFERED=TRUE

# python ~/benchmarks/models/gs2/server-fast.py & # CHANGE ME!
port=$(get_available_port)
export PORT=$port
python /nobackup/mghw54/slurm_vs_hq/umbridge/hq/servers/eigen.py &
# python /nobackup/mghw54/slurm_vs_hq/hq/servers/gs2.py &

host=$(hostname -I | awk '{print $1}')

echo $host
echo $port
echo "Waiting for model server to respond at $host:$port..."
while ! curl -s "http://$host:$port/Info" > /dev/null; do
    sleep 0.01
done
echo "Model server responded"

# Write server URL to file identified by HQ job ID.
mkdir -p $UMBRIDGE_LOADBALANCER_COMM_FILEDIR
echo "http://$host:$port" > "$UMBRIDGE_LOADBALANCER_COMM_FILEDIR/url-$HQ_JOB_ID.txt"

sleep infinity # keep the job occupied
