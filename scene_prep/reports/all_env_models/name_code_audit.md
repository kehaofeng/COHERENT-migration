# 名称编号匹配模型：27 项静态核对

核对日期：2026-10-09。这里只检查规划物体名中的编号、候选模型类别、磁盘入口和规划属性；没有启动三维预览。现有场景只用来证明某型号曾被配置过，不能说明该场景对应某个规划环境。

**结果：27 项均有非空模型入口文件，涉及 21 个不同型号；18 项类别名称直接一致，9 项属于类别含义替代。没有任何一项凭这些证据自动升级为最终选型。**

| 环境和物体 | 编号指向的模型 | 类别关系 | 其他基础场景使用同型号 | 规划要求仍需验证 |
| --- | --- | --- | ---: | --- |
| env1 · `salad_nffvob_0` | `salad/nffvob` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env1 · `tomato_sauce_jar_krfzqk_0` | `tomato_sauce_jar/krfzqk` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env1 · `dining_table_uhrsex_0` | `breakfast_table/uhrsex` | 替代类别，需核对 | 5 | 尺寸/支撑或着陆 |
| env1 · `frying_pan_aewpzn_0` | `frying_pan/aewpzn` | 同类别 | 0 | 开合/容纳、抓取/移动、桌面放置 |
| env2 · `cash_register_strtoe_0` | `cash_register/strtoe` | 同类别 | 0 | 开合/容纳、桌面放置 |
| env2 · `bottle_of_apple_juice_pttzdw_0` | `bottle_of_apple_juice/pttzdw` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env2 · `carton_of_milk_aginyz_0` | `carton_of_milk/aginyz` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env2 · `checkout_counter_cowjqr_0` | `bar/cowjqr` | 替代类别，需核对 | 1 | 尺寸/支撑或着陆 |
| env2 · `display_bin_prtqlw_0` | `grocery_shelf/prtqlw` | 替代类别，需核对 | 3 | 开合/容纳、桌面放置 |
| env2 · `display_bin_prtqlw_1` | `grocery_shelf/prtqlw` | 替代类别，需核对 | 3 | 开合/容纳、桌面放置 |
| env2 · `display_bin_prtqlw_2` | `grocery_shelf/prtqlw` | 替代类别，需核对 | 3 | 开合/容纳、桌面放置 |
| env2 · `lettuce_orsjxq_0` | `lettuce/orsjxq` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env2 · `lettuce_orsjxq_1` | `lettuce/orsjxq` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env3 · `cash_register_strtoe_0` | `cash_register/strtoe` | 同类别 | 0 | 开合/容纳、桌面放置 |
| env3 · `coffee_maker_artpwc_0s` | `coffee_maker/artpwc` | 同类别 | 0 | 开合/容纳、桌面放置 |
| env3 · `beer_bottle_nigfha_0` | `beer_bottle/nigfha` | 同类别 | 0 | 内容状态、抓取/移动、桌面放置 |
| env3 · `dining_table_hmzwxn_0` | `breakfast_table/hmzwxn` | 替代类别，需核对 | 8 | 尺寸/支撑或着陆 |
| env3 · `dining_table_hmzwxn_1` | `breakfast_table/hmzwxn` | 替代类别，需核对 | 8 | 尺寸/支撑或着陆 |
| env3 · `money_atvcng_0` | `money/atvcng` | 替代类别，需核对 | 0 | 抓取/移动 |
| env3 · `beer_glass_lymciz_0` | `beer_glass/lymciz` | 同类别 | 0 | 内容状态、抓取/移动、桌面放置 |
| env3 · `coffee_cup_ckkwmj` | `coffee_cup/ckkwmj` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env4 · `soccer_ball_ikagkc_0` | `soccer_ball/ikagkc` | 同类别 | 0 | 抓取/移动 |
| env4 · `bottle_of_water_atvnqy_0` | `bottle_of_water/atvnqy` | 同类别 | 0 | 抓取/移动、桌面放置 |
| env4 · `mailbox_bktljr_0` | `mailbox/bktljr` | 同类别 | 0 | 开合/容纳、尺寸/支撑或着陆 |
| env4 · `dining_table_hmzwxn_0` | `breakfast_table/hmzwxn` | 替代类别，需核对 | 8 | 尺寸/支撑或着陆 |
| env4 · `mail_azunex_0` | `mail/azunex` | 同类别 | 0 | 抓取/移动 |
| env4 · `rag_oocmed_0` | `rag/oocmed` | 同类别 | 0 | 抓取/移动 |

## 九项替代类别的具体疑问

- `dining table` → `breakfast_table`（4 项）：早餐桌模型能否满足规划中的高桌面、支撑和无人机着陆要求？场景中出现过同型号，也不能直接证明高度或落点。
- `checkout counter` → `bar`（1 项）：吧台外形、台面和收银用途是否符合“收银台”？
- `display bin` → `grocery_shelf`（3 项）：货架是否能作为开放的展示货箱来容纳物品？三个规划实例可以复用一个型号，但需三份独立实例。
- `paper money` → `money`（1 项）：该型号是否呈现纸币，而不是硬币或其他形式？

## 使用方式

先把 18 项同类别候选作为优先核查对象；九项替代类别先确认语义。看到模型外形并核对必要功能前，不要仅因编号存在就修改 `scene_prep/config/model_selections.json`。完整的任务出现位置和候选列表仍以 `model_mapping.json` 为准。
