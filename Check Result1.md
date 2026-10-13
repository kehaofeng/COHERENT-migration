# OmniGibson 模型库检查结果与差异对照


77 种找到同名模型类别，13 种通过不同叫法找到候选，35 种需要确认具体选型，4 种需要定义组合，1 种遥控器未找到本地候选，另有 1 种车库地面区域。

## 一、名称中的模型编号有问题

| 任务里的物品 | 模型库的实际情况 | 涉及任务 |
| --- | --- | --- |
| 苹果 `apple_brkitw_0` | `brkitw` 属于鸡蛋；可选苹果模型，例如 `apple/agveuv` | env2：7—8、15、19 |
| 苹果 `apple_brkitw_1` | `brkitw` 属于鸡蛋；可选苹果模型，例如 `apple/agveuv` | env2：1—2、13、17—18 |
| 苹果 `apple_brkitw_2` | `brkitw` 属于鸡蛋；可选苹果模型，例如 `apple/agveuv` | env2：16、19 |
| 香蕉 `banana_brkitw_2` | `brkitw` 属于鸡蛋；可选香蕉模型，例如 `banana/verqwv` | env2：7、12 |
| 香蕉 `banana_brkitw_3` | `brkitw` 属于鸡蛋；可选香蕉模型，例如 `banana/verqwv` | env2：19 |
| 手巾 `hand_towel_buerfv_0` | `buerfv` 未找到；有手巾模型 `hand_towel/klevhj` | env1：10、16 |

这些物品类别都有模型，不能因为名称中的编号不合适就判定整个类别缺失。

## 二、不同叫法找到候选：全部 13 种

| 任务里的物品（中文／原名） | 模型库中找到的候选类别 | 不同之处／待确认内容 | 环境：任务编号 |
| --- | --- | --- | --- |
| 饼干 `biscuits` | `biscuit` | 复数与单数叫法 | env2：4—5、8—9、12、14、18 |
| 现金 `cash` | `money` | 叫法不同，现金的形式仍需确认 | env3：14 |
| 咖啡机 `coffeemachine` | `coffee_maker` | 叫法不同 | env0：4 |
| 叉子 `fork` | `tablefork` | 库中按餐叉分类 | env1：13、20 |
| 热狗 `hot dog` | `hotdog` | 单词写法不同 | env3：18—19<br>env4：12 |
| 肉丸 `meat ball` | `meatball` | 单词写法不同 | env1：10、12、14—15、19 |
| 牛奶盒 `milkbox` | `milk_carton`、`carton_of_milk`、`box_of_milk` | 包装类别不同，需要选型 | env0：2、15 |
| 纸币 `paper money` | `money` | 库中归到 money，需选择纸币模型 | env2：0—3、6、8—10、14—18<br>env3：0—19 |
| 银币 `silver coin` | `silver_coins` | 单复数叫法，需核对数量 | env0：3 |
| 袜子 `socks` | `sock` | 单复数叫法，需核对数量 | env0：0、8、12、15 |
| 卫生纸 `toilet tissue` | `toilet_paper` | 叫法不同 | env2：0、3、7、14 |
| 餐桌 `dining table` | `breakfast_table` | 库中可用早餐桌类候选，需核对尺寸用途 | env0：0—20<br>env1：0—20<br>env3：0—19<br>env4：0—19 |
| 吧台 `bar counter` | `bar` | 叫法不同 | env3：0—19 |

## 三、有相关模型，但需确认选型：全部 35 种

| 任务里的物品（中文／原名） | 模型库中找到的候选类别 | 不同之处／待确认内容 | 环境：任务编号 |
| --- | --- | --- | --- |
| 书 `book` | `hardback`、`paperback_book`、`textbook`、`comic_book` | 书的种类未明确 | env4：8、17 |
| 盒子 `box` | `packing_box`、`storage_box`、`gift_box` | 包装箱、收纳盒、礼品盒用途不同 | env0：0、3、9、12、17、20 |
| 面包 `bread` | `bread_slice`、`baguette`、`sourdough`、`pack_of_bread` | 面包片、法棍、整块或袋装面包需选择 | env0：0—2、10—11、13—14、16、20<br>env1：6、8、14、20<br>env3：2—3、8、12 |
| 柜子 `cabinet` | `bottom_cabinet`、`top_cabinet`、`wardrobe` | 地柜、吊柜、衣柜不同 | env0：0—20 |
| 椅子 `chair` | `straight_chair`、`armchair`、`folding_chair`、`swivel_chair` | 普通椅、扶手椅、折叠椅、转椅不同 | env1：0—20 |
| 收银台 `checkout counter` | `checkout_counter`、`bar` | 收银台有同名类别；吧台仅为相关候选 | env2：0—19 |
| 巧克力 `chocolate` | `chocolate_bar`、`white_chocolate` | 条状巧克力、白巧克力需选择 | env4：4 |
| 硬币 `coin` | `nickel`、`silver_coins` | 硬币种类和数量需选择 | env2：12、14 |
| 食谱书 `cookbook` | `hardback`、`paperback_book` | 书模型存在，但不证明内容是食谱 | env1：6—7、9、12、14 |
| 曲奇饼干 `cookie` | `sugar_cookie`、`butter_cookie`、`chocolate_chip_cookie`、`spice_cookie` | 饼干种类需选择 | env3：17 |
| 烹饪锅 `cooking pot` | `saucepot`、`stockpot`、`copper_pot` | 锅的类型和大小需选择 | env1：18—19 |
| 展示货箱 `display bin` | `grocery_shelf`、`storage_box`、`display_case` | 货架、收纳箱、展示柜不一定符合货箱含义 | env2：0—19 |
| 展示桌 `display table` | `breakfast_table`、`pedestal_table`、`console_table` | 桌子模型存在，展示用途和尺寸需确认 | env2：0—19 |
| 饮料 `drinks` | `bottle_of_water`、`bottle_of_orange_juice`、`can_of_soda` | 饮料种类和包装未明确 | env4：13 |
| 空瓶 `empty bottle` | `bottle_of_water`、`beer_bottle`、`bottle_of_milk` | 有瓶子模型，不能直接认定为空瓶 | env1：3—4、8、15、20 |
| 空盒 `empty box` | `packing_box`、`storage_box` | 有盒子模型，需确认内容和状态 | env2：1、5、10 |
| 车库桌子 `garage table` | `breakfast_table`、`console_table`、`desk` | 需选桌型；在车库摆放不由类别保证 | env4：0—19 |
| 烧烤桌 `grill table` | `pedestal_table`、`breakfast_table`、`countertop` | 桌面尺寸、用途需确认 | env4：0—19 |
| 厨房高桌 `high kitchen table` | `countertop`、`commercial_kitchen_table`、`breakfast_table` | 需确认桌高和用途 | env0：0—20 |
| 高桌 `high table` | `breakfast_table`、`console_table`、`desk` | 有桌子模型，不能直接认定高度符合 | env0：0—20 |
| 果酱 `jam` | `jar_of_jam`、`jam_dispenser` | 罐装果酱和果酱分配器不同 | env3：18 |
| 果汁 `juice` | `bottle_of_orange_juice`、`bottle_of_apple_juice`、`carton_of_orange_juice` | 瓶装、纸盒装或液体果汁的含义需确认 | env3：18<br>env4：3、15 |
| 厨房桌子 `kitchen table` | `countertop`、`commercial_kitchen_table`、`breakfast_table` | 操作台和餐桌的用途不同 | env0：0—20<br>env1：0—20 |
| 刀 `knife` | `table_knife`、`carving_knife`、`utility_knife` | 餐刀、切肉刀、多用刀需选择 | env0：3、5、9、11、13、16<br>env1：1、5、13、17—18 |
| 草坪上的桌子 `lawn table` | `breakfast_table`、`pedestal_table` | 需选桌型；在草坪摆放不由类别保证 | env4：0—19 |
| 矮书架 `low bookshelf` | `bookcase`、`book_case`、`shelf` | 有架子模型，需确认高度和用途 | env1：0—20 |
| 肉 `meat` | `steak`、`chicken_breast`、`kebab` | 牛排、鸡胸肉、烤串不同 | env4：19 |
| 餐巾 `napkin` | `dinner_napkin`、`paper_towel` | 餐巾和纸巾不一定等价 | env3：7、15 |
| 储物架 `storage shelf` | `shelf`、`grocery_shelf`、`wall_mounted_shelf` | 落地架、货架、壁架用途不同 | env1：0—20 |
| 秋千旁的桌子 `swing table` | `breakfast_table`、`pedestal_table` | 需选桌型并确定摆放位置 | env4：0—19 |
| 糖浆 `syrup` | `sugar_syrup_bottle`、`bottle_of_maple_syrup`、`maple_syrup_jar` | 糖浆类型和容器需确认 | env3：8 |
| 餐具回收台 `tableware recycling table` | `commercial_kitchen_table`、`countertop`、`breakfast_table` | 相关台面模型不一定具有回收台的功能 | env3：9 |
| 番茄 `tomato` | `beefsteak_tomato`、`cherry_tomato` | 大番茄、樱桃番茄需选择 | env1：2、4—5、11、13 |
| 毛巾 `towel` | `hand_towel`、`dishtowel` | 擦手巾、擦碗巾用途不同 | env4：11 |
| 水杯 `water cup` | `water_glass`、`cup` | 杯型及是否有水需确认 | env4：7 |

## 四、组合物品：全部 4 种

| 任务里的物品（中文／原名）            | 模型库中找到的候选类别                                        | 不同之处／待确认内容          | 环境：任务编号           |
| ------------------------ | -------------------------------------------------- | ------------------- | ----------------- |
| 清洁用品 `cleaning supplies` | `bottle_of_cleaner`、`bottle_of_detergent`、`sponge` | 需确定清洁剂、洗涤剂、海绵的组成和数量 | env1：6—7、10、14、18 |
| 旧衣服 `old clothes`        | `t_shirt`、`pants`、`sock`                           | 衣服种类、数量和新旧状态需确认     | env1：1、3、6        |
| 水果碗 `fruit bowl`         | `bowl`、`apple`、`banana`                            | 需明确是空碗还是装水果的组合      | env1：0、7、9        |
| 餐具套装 `cutlery set`       | `tablefork`、`table_knife`、`tablespoon`             | 需明确叉、刀、勺的组成和数量      | env1：0、5、15、17、19 |

## 五、未找到与区域项

| 任务里的内容 | 模型库检查结果 | 环境：任务编号 |
| --- | --- | --- |
| 遥控器 `remote control` | 本机暂未找到可识别的模型候选，不能据此断言其他版本也没有 | env1：4、9 |
| 车库地面 `garage floor` | 有地板类 `floors` 模型；任务要求的是车库的地面区域，需要单独指定范围 | env4：0—19 |
