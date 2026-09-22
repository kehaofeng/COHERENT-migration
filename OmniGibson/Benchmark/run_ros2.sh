#!/usr/bin/env bash
set -euo pipefail

benchmark_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$benchmark_dir/../.." && pwd)"
ros2_workspace="$benchmark_dir/ros2_hademo_ws"
task_name="${1:-Merom_1_int_Task1}"

if [[ ! -f "$ros2_workspace/install/setup.bash" ]]; then
    echo "ROS 2 workspace is not built. Run: $ros2_workspace/build.sh" >&2
    exit 1
fi

export COHERENT_PATH="${COHERENT_PATH:-$repo_root}"

conda_base="${CONDA_BASE:-}"
if [[ -z "$conda_base" ]] && command -v conda >/dev/null 2>&1; then
    conda_base="$(conda info --base)"
fi
if [[ -z "$conda_base" ]] && [[ -d "$HOME/miniconda3" ]]; then
    conda_base="$HOME/miniconda3"
fi
if [[ -z "$conda_base" ]] && [[ -d "$HOME/anaconda3" ]]; then
    conda_base="$HOME/anaconda3"
fi
if [[ ! -f "$conda_base/etc/profile.d/conda.sh" ]]; then
    echo "Cannot find Conda. Set CONDA_BASE to the Miniconda/Anaconda install directory." >&2
    exit 1
fi

simulation_pid=""
bridge_pid=""
publisher_pid=""
cleanup() {
    [[ -z "$publisher_pid" ]] || kill -- "-$publisher_pid" 2>/dev/null || true
    [[ -z "$bridge_pid" ]] || kill -- "-$bridge_pid" 2>/dev/null || true
    [[ -z "$simulation_pid" ]] || kill -- "-$simulation_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Start Isaac before sourcing ROS 2 so its Python 3.7 process does not inherit
# Humble's Python 3.10 module paths.
setsid bash -c '
    set -eo pipefail
    source "$1/etc/profile.d/conda.sh"
    conda activate omnigibson
    cd "$2"
    exec python sim.py --task_name "$3"
' _ "$conda_base" "$benchmark_dir" "$task_name" &
simulation_pid=$!

set +u
source /opt/ros/humble/setup.bash
source "$ros2_workspace/install/setup.bash"
set -u

setsid "$ros2_workspace/install/hademo_nodes/lib/hademo_nodes/sim_bridge" &
bridge_pid=$!

setsid "$ros2_workspace/install/hademo_nodes/lib/hademo_nodes/action_publisher" --task_name "$task_name" &
publisher_pid=$!

set +e
wait "$simulation_pid"
simulation_status=$?
set -e
cleanup
trap - EXIT INT TERM
exit "$simulation_status"
