# COHERENT 复现问题与环境准备

记录日期：2026-09-17。依据本地源码和 README 静态检查；尚未运行付费模型调用或物理仿真。下述问题尚未修复。

## 1. 项目运行链路

| 路径 | 用途 |
| --- | --- |
| `src/experiment/PEFA/` | 主方法：任务分配、执行、反馈、调整 |
| `src/experiment/PEFA_wo_history/` | 去掉历史信息的消融实验 |
| `src/experiment/CRMS/`、`DRMS/`、`mcts/` | 对比方法 |
| `env/` | 场景图、任务目标、GT 最优步数；各方法另有数据副本 |
| `OmniGibson/Benchmark/` | 三维仿真、机器人控制、ROS 通信 |

PEFA 调用顺序：`main.py` 加载任务 → `LLM_oracle.py` 分配子任务 → `LLM_agent.py` / `LLM.py` 选择动作 → `get_env_info.py` 更新场景图并判断目标 → 反馈与下一轮规划。

规划实验通过规则更新 JSON 场景图，可以独立于 Isaac Sim 运行。PEFA 超过两倍 GT 步数时判定失败。物理仿真的演示成功不等于规划实验指标复现成功。

## 2. 已发现的问题

### 2.1 主程序结束时日志参数错误（已确认）

位置：`src/experiment/PEFA/main.py:113-115`。

`write_log_to_file(log_message, file_name=...)` 的第二个参数是文件路径，但调用传入了平均步数、成功列表和失败列表，导致统计输出阶段报错。应将统计值格式化进第一个字符串参数。还应检查其他方法是否有同类问题。

### 2.2 实验任务数量不一致（已确认，原因待核对）

README 描述 100 个任务，但根目录与 PEFA 的场景数据均为：

| 环境 | 记录数 |
| --- | ---: |
| env0 | 21 |
| env1 | 21 |
| env2 | 20 |
| env3 | 20 |
| env4 | 20 |
| 合计 | 102 |

PEFA `main.py` 注释称论文使用以下 40 个任务；这一注释尚未与论文实验设置核对：

```text
env0: 2, 4, 9, 10, 11, 15, 16, 20
env1: 1, 3, 7, 8, 11, 10, 16, 20
env2: 3, 5, 6, 7, 10, 11, 16, 17
env3: 2, 4, 6, 7, 10, 16, 17, 19
env4: 0, 1, 7, 10, 12, 17, 18, 19
```

`--task` 用作 JSON 列表索引，从 0 开始。正式评测前需要确定任务集合、重复次数、失败处理和指标统计口径。

### 2.3 依赖与模型配置（已确认配置，兼容性待验证）

- 根目录文件名为 `requirement.txt`，不是 `requirements.txt`，未锁定依赖版本。
- PEFA 直接导入 `numpy` 和 `yaml`，但清单未直接列出 `numpy`、`PyYAML`；不应依赖间接安装保证环境完整。
- 默认模型为 `gpt-4-0125-preview`，需验证目标接口是否支持；更换模型应记录为不同实验条件。
- API key 和 organization 默认空字符串；尚未配置和测试。
- PEFA 的 API 重试装饰器未指定重试次数或时间上限，应在批量运行前检查异常退出行为。
- 模型调用费用按少量旧模型名称硬编码；更换模型后不能依赖现有费用统计。

### 2.4 运行目录与日志（已确认）

主方法使用 `./env/`、`./prompt/`、`./log/` 相对路径，应先进入 `src/experiment/PEFA` 再运行。现有日志包含作者结果且采用追加写入；正式复现应使用独立输出目录，避免混合新旧结果。

修复与配置完成后的单任务入口：

```bash
cd /home/kehaofeng/COHERENT/src/experiment/PEFA
python main.py --env env0 --task 2
```

此命令会调用模型，不是离线测试；原始代码的默认凭据不足以直接运行。

### 2.5 仿真演示使用预定义动作（已确认）

`OmniGibson/Benchmark/ros_hademo_ws/src/hademo/src/action_publisher.py` 内置 `Merom_1_int_Task1_TextPlanList` 和 `house_double_floor_lower_Task1_TextPlanList`，并根据任务名称读取。

`run.sh` 启动该发布器和仿真器。此入口不是直接运行 PEFA 在线规划；如要验证完整闭环，需要继续检查并接通规划输出、仿真动作、执行结果及状态反馈。

### 2.6 旧版仿真环境与路径（已确认）

- README 指定作者修改版 Isaac Sim 2022.2.0 和修改版 OmniGibson 0.2.1。
- 作者环境为 Ubuntu 20.04 / ROS1 Noetic；还需外部机器人资产与场景数据。
- `ros_hademo_ws/devel/_setup_util.py` 包含 `/home/pjlab/...` 绝对路径。应检查 ROS 依赖并在本机重新构建工作空间，不能假定已有构建产物可迁移。
- README 的 `cd Banchmark` 应为 `cd Benchmark`。
- `run.sh` 使用 `gnome-terminal` 和 `conda activate`，需要桌面环境及正确的 shell 初始化；纯 SSH 环境需要调整启动方式。
- `scripts/setup.sh` 会创建单独的仿真环境，其 Python 版本从 Isaac Sim 获取；不要直接将规划环境的 Python 3.10 要求套用到仿真环境。

## 3. 本机检查快照

| 项目 | 当前检查结果 |
| --- | --- |
| 系统 / 架构 | Ubuntu 20.04.6 LTS / x86_64 |
| Conda | 当前 shell 未找到命令，常见安装目录未发现；不排除其他自定义位置 |
| 当前 Python | 缺少 numpy、openai、backoff、torch、scipy、tqdm、sentence_transformers；yaml 可找到 |
| NVIDIA | `nvidia-smi` 无法连接驱动，原因待诊断，不能据此断定没有 GPU |
| Isaac Sim / ROS | 未发现标准路径下的指定 Isaac Sim 和 `/opt/ros/noetic` |
| 数据 / 资产 | 未发现 `OmniGibson/omnigibson/data` 和 `OmniGibson/Benchmark/assets` |

## 4. 推荐复现顺序

1. 安装编辑器和 Miniconda，建立 Python 3.10 规划环境。
2. 修复日志错误、补齐依赖，配置模型接口与独立日志目录。
3. 运行 `env0/task2`，检查动作解析、状态更新、终止条件和实际调用量。
4. 确定论文评测任务集合，保存模型、提示词、参数、依赖版本与代码提交号。
5. 批量运行主方法，再运行对比方法和消融实验。
6. 排查 GPU 驱动，准备作者指定仿真软件与资产，重新构建 ROS 工作空间。
7. 先验证预定义动作演示，再接入在线规划闭环。

## 5. Ubuntu x86_64 安装 VS Code

以下命令由用户在终端执行；本文整理过程未实际安装软件。

```bash
sudo apt update
sudo apt install -y wget ca-certificates
mkdir -p ~/Downloads
cd ~/Downloads
wget -O vscode.deb 'https://update.code.visualstudio.com/latest/linux-deb-x64/stable'
sudo apt install ./vscode.deb
code --version
```

也可从 [VS Code 下载页](https://code.visualstudio.com/download) 选择 Linux `.deb` x64，在下载目录使用 `sudo apt install ./实际文件名.deb`。安装方式见 [官方 Linux 安装指南](https://code.visualstudio.com/docs/setup/linux)。

在有桌面环境的终端打开项目：

```bash
code /home/kehaofeng/COHERENT
```

## 6. 安装 Miniconda（本项目推荐）

Miniconda 提供 Conda、Python 和基础依赖，适合按项目创建环境；Anaconda 预装更多科学计算工具。二选一即可。本项目建议 Miniconda，按需安装依赖。参见 [Conda 安装说明](https://docs.conda.io/projects/conda/en/stable/user-guide/install/)。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
wget -O Miniconda3-latest-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

根据提示阅读协议；同意后输入 `yes`，安装目录可保留默认的 `~/miniconda3`。询问是否初始化 shell 时选择 `yes`。安装 Miniconda 不要加 `sudo`。

关闭并重新打开终端，或在 Bash 中执行：

```bash
source ~/.bashrc
conda --version
conda config --set auto_activate_base false
conda create -n coherent python=3.10
conda activate coherent
python --version
```

若 `conda` 仍找不到，且使用了默认安装目录：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda init bash
source ~/.bashrc
```

上述创建的是规划实验环境。完整项目依赖安装、代码修复和 API 验证属于后续步骤。

官方参考：[安装向导](https://www.anaconda.com/docs/getting-started/installation)、[Linux 安装流程](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html)。

## 7. 如果选择 Anaconda

从 [官方安装包目录](https://repo.anaconda.com/archive/) 下载所选版本的 `Anaconda3-版本号-Linux-x86_64.sh`。在下载目录执行 `bash 实际安装包文件名.sh`，按提示安装和初始化 shell；默认目录通常是 `~/anaconda3`。

重新打开终端后，同样使用 `conda create -n coherent python=3.10` 和 `conda activate coherent`。不必再安装 Miniconda。参考 [Anaconda Linux 安装指南](https://www.anaconda.com/docs/getting-started/anaconda/install/linux-install)。
