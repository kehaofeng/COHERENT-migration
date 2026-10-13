# 离线整理三维场景和资产

这组工具用于第一轮整理：读取规划任务、扫描模型和已有场景、生成带证据的对应工作表。只依赖 Python 3.10 标准库，不需要激活 OmniGibson 环境。

## 当前优先任务：五个环境的物体与模型对应

先看 [全量模型对应进度](../../scene_prep/reports/all_env_models/README.md) 和 [工作日志](../../scene_prep/WORK_LOG.md)。这条流程不要求五个规划环境先与已有三维场景对应。

对名称中恰好含有有效模型编号的 27 项，另有[逐项静态核对表](../../scene_prep/reports/all_env_models/name_code_audit.md)。编号和文件匹配仅作为线索，不自动确认最终型号。

```bash
python3 tools/scene_prep/map_all_models.py
```

脚本读取 `env/env0.json` 到 `env/env4.json`、本地模型库、旧候选类别报告，以及原任务配置与数据集基础场景中的同名实例。生成 `scene_prep/reports/all_env_models/` 下的 CSV、JSON、目录清单和汇总。**CSV 和报告是自动生成的，不要在里面填写最终选型。**

需要人工选定模型时，编辑 `scene_prep/config/model_selections.json` 中的 `selections`。对应键可直接复制 CSV 第一列。例如：

```json
{
  "schema_version": 1,
  "selections": {
    "env4|Food|kebab_cewhbv_0": {
      "category": "kebab",
      "model": "ezgwob",
      "evidence": "核对原演示配置及任务需要后人工确认"
    }
  }
}
```

这只是格式示例。当前选型文件已记录 22 项原项目同名实例使用的型号，其余条目待核对。修改后重新运行脚本；程序会检查所选模型入口文件是否存在。`source_backed` 表示原配置有同名实例使用该型号，仍需核对它是否适合规划物体；`selection_recorded` 表示另行记录了有依据的选型。两者均不表示仿真加载成功，也不说明原场景对应某个规划环境。

## 先看结果

当前试点是 **env0 / task_id=1：无人机降落到餐桌上**。

- [中文核对报告](../../scene_prep/reports/env0_task1/README.md)
- [全部节点及初始关系](../../scene_prep/reports/env0_task1/inventories/task_entities.md)
- [对应候选，含位置和文件依据](../../scene_prep/reports/env0_task1/mapping_candidates.json)
- [可编辑的候选规则和逐物品备注](../../scene_prep/config/env0_task1_review.json)

## 重新生成

在仓库根目录运行：

```bash
python3 tools/scene_prep/inspect_pilot.py
python3 tools/scene_prep/validate_worksheet.py
```

第一个命令会重新生成 `scene_prep/reports/env0_task1/` 中的派生清单和报告；需要保留的人工备注应修改 `scene_prep/config/env0_task1_review.json`，不要直接修改生成结果。

第二个命令检查工作表是否完整、原始文件是否已变化、候选入口是否仍存在。退出码 0 只表示工作表检查通过；正式任务配置和三维加载状态仍分别为“待补齐”和“未验证”。失败时退出码为 1，原因写入 `worksheet_validation.json`。

脚本自动根据自身位置定位仓库，不依赖当前工作目录。迁移到服务器后可继续使用相同相对目录；也可用 `--repo-root` 指定另一个包含同样结构的项目副本。资产应放到所记录的数据目录中。

## 单独提取其他任务

```bash
python3 tools/scene_prep/extract_task_entities.py --env env0 --task-id 2
```

`--task-id` 指 JSON 里的任务编号。程序会检查编号是否唯一存在，并额外记录它的列表下标；不会悄悄把编号当成下标。

```bash
python3 tools/scene_prep/inventory_assets.py
```

这个命令单独扫描模型库及默认 Merom 场景。可通过 `--scene`、`--demo` 替换数据来源。

`inspect_pilot.py` 的人工说明和机器人参考目前针对 env0/task1，不能只改环境编号就把整份解释套到其他任务；扩展任务时还需要相应的核对规则和报告说明。

## 如何读结果

1. `task_entities.json` 保留所有节点，包括非目标物品、机器人和房间。`initial_relations` 是最初状态，不是任务完成后的状态。
2. `scene_or_demo_candidates` 表示已有场景或演示中的候选对应；`model_candidates` 是类别选型范围，数量多不等于这些模型都满足任务要求。
3. `entry_status: found` 只表示模型入口文件找到。数据集的 `.encrypted.usd` 也会被识别；不读取或公开解密密钥内容。
4. `position` 若来自场景 JSON，是该候选物品原有坐标。`unresolved_expression` 表示配置依赖其他变量或函数，尚未当作数值解析。
5. `mapping_status: candidate` 不表示已确认。`selected_candidate` 当前为空，`ready_to_generate` 当前固定为 false：首轮工具不会生成未经确认的可执行场景。
6. 第二台机械臂可以复用模型，但必须新增独立实例。工作表用 `reuse_instance: false` 区分这种情况。

## 已实现与后续内容

| 内容 | 当前状态 |
| --- | --- |
| 规划任务完整提取、根目录与 PEFA 数据副本比较 | 已实现 |
| 数据集入口、场景对象和演示配置静态扫描 | 已实现 |
| env0/task1 全部节点的候选和差异报告 | 已实现 |
| 工作表来源、节点覆盖与记录文件复查 | 已实现 |
| 明确每个物品最终选型、位置和状态 | 待逐项落实 |
| 正式任务配置生成器、仿真加载入口 | 后续实现 |
| USD 内部依赖、物理效果、机器人动作验证 | 待仿真服务器验证 |

## 验证脚本

```bash
python3 -m unittest discover -s tools/scene_prep -p 'test_*.py' -v
```

覆盖：加密入口、名字与模型编号不一致、配置不会被执行、关系循环/悬空节点、保留背景物品、任务编号与下标不同、第二台机械臂不误绑定、过期或不完整工作表。
