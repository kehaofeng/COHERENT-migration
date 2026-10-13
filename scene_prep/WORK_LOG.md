# 场景与资产工作日志

本日志区分人工输入、自动生成结果和待实现内容。当前优先目标是给五个规划环境的物体确定具体模型；场景布置和坐标稍后处理。

## 2026-10-12：env0/task1 入门阅读图

新增 `tools/scene_prep/build_first_lesson_images.py`，从 `env/env0.json` 的 `task_id=1` 和现有全量模型候选报告生成三张教学示意图，保存在 `output/learning/env0_task1/`：任务初始关系与目标、两个静态分析脚本的独立数据流、`sunglasses_0` 的四个候选型号。图中无人机、餐桌和太阳镜均为符号，**不是三维模型预览**；房间位置不表示真实几何布局。生成时核对了示意图使用的节点、关系、太阳镜候选数和当前状态。另实际执行 `python3 tools/scene_prep/extract_task_entities.py --env env0 --task-id 1 --output output/learning/env0_task1/extracted`，得到 31 个节点、34 条关系及对应 JSON/Markdown。上述脚本均不启动仿真，也不修改模型选型。

## 2026-10-11：52 项非普通物品节点的处理清单

新增 `tools/scene_prep/map_special_entities.py`，生成 `scene_prep/config/special_entities_v1.json` 和 `scene_prep/SPECIAL_ENTITIES_V1.md`。把 52 项按房间 13、地面 13、花园子区域 2、机器人 19、无人机附属篮子 5 分类，逐项连到当前二维布局的区域、暂定工作位或父机器人。所有键均已对应上现有布局，但没有因此确认三维资产、碰撞、姿态或可达性。代码里存在 `Crazyflie/cf2x_with_basket.usda` 路径线索，本机尚未验证资产可加载，篮子是否已包含于 USD 也待核对。另发现 `lawn_ogzsvf_0` 在旧场景确有 `lawn/ogzsvf` 模型，但原包围盒约 46 x 23 m，与新草坪区暂定的 4 x 4 m 不匹配，须单独核对尺寸和用法。

## 2026-10-11：供学长核对的五环境资产 PDF

新增 `tools/scene_prep/export_asset_review_pdf.py`，生成 `output/pdf/five_env_asset_review.pdf`。报告含五个环境的二维布局、262 项完整规划实体清单、任务出现次数、布局标记、模型状态及已有的 22 项原配置选型；待选项仅列候选数量，完整候选型号保留在映射报告中。报告明确说明坐标是草案，模型尺寸、碰撞、朝向和机器人可达性仍需三维仿真核对。本机无 SimSun，PDF 中文使用宋体风格的 AR PL UMing CN，英文使用 Arial。已检查全部条目均出现于 PDF，并渲染逐页核对版式。

## 2026-10-11：五环境资产核对可视化

新增 `tools/scene_prep/build_asset_visualization.py` 和 `scene_prep/asset_visualization.template.html`，从全量映射报告及布局初稿生成五环境交互式俯视图与资产清单。每个环境可查看全部规划实体的标识、类别、类名、出现任务数、当前模型状态、候选模型和原配置依据；图上展示固定物体、门及机器人初始区。env2 两个同名垃圾桶按规划类别分别标示。字体指定英文 Arial、中文 SimSun（本机无 SimSun 时回退到 Noto Serif CJK SC 宋体风格字体）。页面是核对资料，不代表模型已加载成功。

## 2026-10-09：七场景布局 PDF

使用 `python3 tools/scene_prep/export_layouts_pdf.py output/pdf/seven_scene_layouts.pdf` 生成 A4 纵向七页 PDF：前两页是原有 Merom 与 house_double_floor_lower 的数据集底图和主要家具坐标，后五页是规划环境设计草图。第二版加大图面，统一标题、图例和颜色，并分别采用适合中文和英文的字体；重叠的机器人标记也作了错位显示。已使用系统 Poppler 渲染全部七页逐页检查，并核对 PDF 页数、字体与文本提取。PDF 仍是二维说明图，不是仿真运行截图。

## 2026-10-09：原有两场景与五个新布局的俯视图

新增 `tools/scene_prep/build_layout_visualization.py` 与 `scene_prep/layout_visualization.template.html`，从数据集的房间分割图和对应任务场景文件提取原有 `Merom_1_int`、`house_double_floor_lower` 的二维房间轮廓和选定的主要家具位置；从 `scene_layouts_v1.json` 绘制五个规划环境的设计初稿。生成的可切换七场景可视化保存在本任务的可视化目录。原有图是数据集底图，五个新图是临时设计坐标，两种来源不可当作同等真实性。

发现原任务配置 `house_double_floor_lower_Task1.py` 声明的 `scene_model` 为 `grocery_store_cafe`，但它传入的 `house_double_floor_lower_best_Task1.json` 中有花园、车库、汽车、灌木等房屋场景物体。两者明显不一致，因此第二张原有图画的是**对象文件对应的** `house_double_floor_lower` 数据集底图，并明确标出任务代码的配置冲突。当前不能声称原任务 2 可直接正确加载。

## 2026-10-09：五环境场景布局初稿

依据五份 `env` 的 102 条任务，编写 [场景设计 v1](SCENE_DESIGN_V1.md) 与 [机器可读布局](config/scene_layouts_v1.json)。分别设计四房住宅、厨房/客厅/杂物间、单间超市、单间餐厅、双生活区/走廊/花园；每个环境一套固定布局，任务启动时再从对应 `init_graph` 装载小物件与目标关系。布局含临时米制坐标与固定物体/门锚点，尚未转换为 OmniGibson 可运行配置，未验证资产大小、碰撞、机器人可达性，也未新增模型选型。

静态检查：JSON 可解析；5 环境、102 任务；布局中的所有区域、门、固定物体、任务附加物及机器人名称都存在于各自源文件。新增发现：`env2` 每条任务有两只均名为 `trash_can_0` 的桶，节点 ID 为 23 和 38，应作为两个实例；`env3/task18` 重复节点 ID 24 的问题仍待解决。为减小本机内存压力，后续先用简单几何体与单个物体检查最小场景，再逐件替换已选模型；不能承诺 15 GiB 内存本机可启动 Isaac Sim。

## 2026-10-09：远程预览可行性调查

官方新版 OmniGibson 支持在服务器运行仿真、通过 WebRTC 在本地浏览器看画面，使用 `OMNIGIBSON_REMOTE_STREAMING=webrtc`。本项目的本地 OmniGibson 为 0.2.1：`omnigibson/__init__.py` 仅把 `headless` 等配置传给 `SimulationApp`，`macros.py` 没有读取该远程推流变量。因此不能把新版的环境变量直接当作本项目已支持的功能。

本机 Isaac Sim 2022.2.0 已安装 `isaac-sim.headless.webrtc.sh`、`omni.isaac.sim.headless.webrtc.kit` 与 `omni.services.streamclient.webrtc-1.3.6`。其扩展文档给出浏览器入口 `/streaming/webrtc-client`，Isaac Sim 默认 HTTP 端口 8211；`SimulationApp` 接受自定义 `experience` 参数。推断这为本项目集成远程预览提供了技术基础，但尚未在服务器上做端到端验证；单独启动 Isaac Sim 的 WebRTC 应用也不会自动加载 OmniGibson 的模型预览脚本。下一步在有足够内存和显存的服务器上，将该 WebRTC 扩展接到同版本 OmniGibson 启动流程，核对端口和网络访问，再实际加载一个模型并从本地浏览器连接。当前 15 GiB 内存本机曾在启动中 OOM，仅在本机打开 WebRTC 仍会由本机承担仿真内存，不能解决这一问题。

参考：[OmniGibson 官方远程推流教程](https://behavior.stanford.edu/tutorials/remote_streaming.html)、[NVIDIA Isaac Sim 远程客户端说明](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/manual_livestream_clients.html)。两者所述版本均新于本地安装，具体参数需在本地 2022.2.0 和服务器上验证。

## 2026-10-09：本机尝试预览太阳镜模型

按用户要求，在当前电脑运行 `conda run --no-capture-output -n omnigibson python OmniGibson/omnigibson/examples/objects/visualize_object.py`。Isaac Sim 启动并进入光线追踪着色器编译，但尚未出现类别/型号选择提示时，进程被系统杀死，退出码 137。内核日志明确记录 `Out of memory: Killed process 10582 (python)`；当时进程匿名内存约 7.8 GB，机器总内存 15 GiB、无交换空间。**因此本次没有预览到任何 `sunglasses` 模型，也没有新增模型选择。**完整图形预览需在内存更充足的机器进行，或另行探索更轻量的预览方式；仅看纹理图片不足以确认三维外形。

## 2026-10-09：核对 27 项名称编号线索

生成 [逐项静态核对表](reports/all_env_models/name_code_audit.md)。27 项共涉及 21 个型号，所有编号都能在候选类别下找到非空 USD 入口；其中 18 项的物体名称与模型类别一致，9 项使用替代类别（餐桌→早餐桌、收银台→吧台、展示货箱→货架、纸币→money）。8 项条目的候选型号还在数据集基础场景中出现过，但这不建立“场景对应规划环境”的关系。规划要求的开合、容纳、抓取、大小、着陆和空满状态仍未通过三维验证。**这 27 项继续保持候选状态，没有凭编号自动写入选型文件。**

## 2026-10-09：改为全量物体与模型对应

### 输入和人工维护文件

| 文件 | 作用 | 是否自动覆盖 |
| --- | --- | --- |
| `env/env0.json`—`env/env4.json` | 五个环境、102 条规划任务 | 否 |
| `Check Result1.md` | 旧报告中的同名及近似模型类别线索 | 否 |
| `scene_prep/config/model_selections.json` | 已核对的具体 `category/model` 及依据；当前有 22 项原配置同名实例对应 | 否 |

### 本次编写和生成

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `tools/scene_prep/map_all_models.py` | 扫描五个环境、模型库和原项目中同名实例的明确配置 | 已实现 |
| `scene_prep/reports/all_env_models/model_mapping.csv` | 262 项对应条目的便读总表；含出现任务数和候选数 | 自动生成 |
| `scene_prep/reports/all_env_models/model_mapping.json` | 全部候选型号、原配置证据、每次任务出现位置和数据问题 | 自动生成 |
| `scene_prep/reports/all_env_models/model_catalog.json` | 数据集类别、型号和实际 USD 入口文件目录 | 自动生成 |
| `scene_prep/reports/all_env_models/README.md` | 全量进度与问题汇总 | 自动生成 |

运行：从仓库根目录执行 `python3 tools/scene_prep/map_all_models.py`。脚本仅静态读文件，不启动仿真。自动生成的四个文件会在重跑时被覆盖；人工决定只写到 `model_selections.json`。

本次口径：102 条任务共 3069 次规划节点出现；按“环境＋规划类别＋物体标识”合并为 262 项。扫描原项目任务配置及数据集的 22 份基础场景配置后，找到 22 项同名实例的明确 `category/model`，已据此写入选型文件；其余 187 项有普通模型候选、1 项（遥控器）在当前类别规则下没有候选，52 项是房间、区域、机器人或工具，需专门处理。49 项的名字中含有候选模型的有效编号，但名字编号本身不作为最终依据。其中 `kebab_cewhbv_0` 的编号对应模型文件确实存在，原演示却使用另一型号 `kebab/ezgwob`，已按原配置记录并在总表标为冲突。**目前记录了 22 项有原配置依据的模型对应；这些仍需核对是否适合规划物体，尚未仿真加载，也未确定五个环境的场景。**旧报告的 210 项使用不同去重方式，不能与 262 直接比较。

发现数据问题：`env3/task18` 中 `jam_abc` 和 `hot_dog_prefab` 共用节点 ID 24。两个节点都保留在新清单中；后续需要修复源任务或明确如何解释其关系，不能按节点 ID 把其中一个覆盖。

遥控器：已按 `remote`、`controller` 在本地 OmniGibson 数据集和 Benchmark 资产路径中查找文件名，未找到可直接对应的资产；仍可能需要外部资产或人工制作。

### 此前已生成、仍可参考

| 文件 | 作用 | 当前边界 |
| --- | --- | --- |
| `tools/scene_prep/extract_task_entities.py` | 提取任意一条任务的节点及关系 | 逐任务工具，不做全量模型选型 |
| `tools/scene_prep/inventory_assets.py` | 扫描指定场景和模型库 | 所选场景不代表五个规划环境 |
| `tools/scene_prep/inspect_pilot.py` | 生成 `env0/task1` 候选工作表 | 只覆盖单条试点任务 |
| `tools/scene_prep/validate_worksheet.py` | 核查上述工作表与来源文件 | 通过不等于模型已确认或仿真成功 |
| `scene_prep/config/env0_task1_review.json` | 单任务候选规则与备注 | 不是全量选型表 |
| `scene_prep/reports/env0_task1/` | 单任务分析结果 | 不作为五环境完成率 |

### 接下来的任务

1. 逐项核对剩余 187 项普通模型候选，把最终选择和依据写进 `model_selections.json`。同一模型可供多个实例使用，但每个不同规划标识要明确记录。
2. 处理遥控器：继续搜索其他可用资产或记录需要新模型，不能把“无当前候选”误写成“模型一定不存在”。
3. 为机器人、工具和房间区域建立单独的资产/语义对应表；它们不应强行选普通物品模型。
4. 修复或明确 `env3/task18` 的重复节点 ID。
5. 模型对应完成后，再讨论各环境的基础场景、坐标和三维加载。

## 2026-10-04：先前的单任务试点

选取 `env0/task1`“无人机降落到餐桌上”，生成 31 节点、34 关系的候选报告。检查过 Merom 场景和模型入口文件，发现无人机起点、第二机械臂、餐桌区域和面包位置等未决项。未生成正式三维任务配置，也未实际运行仿真。
