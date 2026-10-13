# env0 / task1 规划物品与初始关系

目标：The <quadrotor>(22) lands on the <dining table>(13).

此清单保留全部节点。房间、地面和机器人也在其中，不能把节点总数当作普通物品数。

关系词：ON＝在上面；INSIDE＝在里面；LEADING TO＝门连接到房间；WITH＝带有工具。

| ID | 名称 | 规划标识 | 类型 | 初始关系 | 推得的房间 | 目标直接涉及 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | bedroom | bedroom_0 | Rooms | 未提供 | bedroom_0 | 否 |
| 1 | bedroom floor | bedroom_0_floor | Floor | INSIDE → bedroom(0) | bedroom_0 | 否 |
| 2 | childroom | childroom_0 | Rooms | 未提供 | childroom_0 | 否 |
| 3 | childroom floor | childroom_0_floor | Floor | INSIDE → childroom(2) | childroom_0 | 否 |
| 4 | livingroom | livingroom_0 | Rooms | 未提供 | livingroom_0 | 否 |
| 5 | livingroom floor | livingroom_0_floor | Floor | INSIDE → livingroom(4) | livingroom_0 | 否 |
| 6 | kitchen | kitchen_0 | Rooms | 未提供 | kitchen_0 | 否 |
| 7 | kitchen floor | kitchen_0_floor | Floor | INSIDE → kitchen(6) | kitchen_0 | 否 |
| 8 | door | Door_0_4 | Doors | LEADING TO → bedroom(0); LEADING TO → livingroom(4) | 未推得 | 否 |
| 9 | door | Door_2_4 | Doors | LEADING TO → childroom(2); LEADING TO → livingroom(4) | 未推得 | 否 |
| 10 | door | Door_4_6 | Doors | LEADING TO → livingroom(4); LEADING TO → kitchen(6) | 未推得 | 否 |
| 11 | sofa | sofa_0 | Furniture | ON → livingroom floor(5) | livingroom_0 | 否 |
| 12 | coffee table | coffeetable_0 | Furniture | ON → livingroom floor(5) | livingroom_0 | 否 |
| 13 | dining table | diningtable_0 | Furniture | ON → livingroom floor(5) | livingroom_0 | 是 |
| 14 | fridge | fridge_0 | Appliances | ON → kitchen floor(7) | kitchen_0 | 否 |
| 22 | quadrotor | quadrotor_0 | Agents | ON → childroom floor(3); INSIDE → childroom(2); WITH → basket(25) | childroom_0 | 是 |
| 23 | robot dog | aliengo_0 | Agents | ON → livingroom floor(5); INSIDE → livingroom(4) | livingroom_0 | 否 |
| 24 | robot arm | franka_0 | Agents | ON → dining table(13); INSIDE → livingroom(4) | livingroom_0 | 否 |
| 25 | basket | quadrotor_0_basket | AgentTool | ON → childroom floor(3) | childroom_0 | 否 |
| 26 | bread | bread_1 | Food | 未提供 | 未推得 | 否 |
| 27 | bed | bed_0 | Furniture | ON → bedroom floor(1) | bedroom_0 | 否 |
| 28 | bed | bed_1 | Furniture | ON → childroom floor(3) | childroom_0 | 否 |
| 32 | kitchen table | kitchentable_0 | Furniture | ON → kitchen floor(7) | kitchen_0 | 否 |
| 33 | high table | high_table_bedroom | Furniture | ON → bedroom floor(1) | bedroom_0 | 否 |
| 34 | cabinet | cabinet_childroom | Furniture | ON → childroom floor(3) | childroom_0 | 否 |
| 35 | high kitchen table | high_kitchentable_kitchen | Furniture | ON → kitchen floor(7) | kitchen_0 | 否 |
| 44 | textbook | Textbook_childroom | Office_supplies | ON → bed(28) | childroom_0 | 否 |
| 45 | toy box | Toybox_childroom | Toys | ON → childroom floor(3) | childroom_0 | 否 |
| 50 | robot arm | robot_arm_bedroom | Agents | ON → high table(33); INSIDE → bedroom(0) | bedroom_0 | 否 |
| 53 | plate | plate_1 | Tableware | INSIDE → fridge(14) | kitchen_0 | 否 |
| 55 | sunglasses | sunglasses_0 | Accessories | ON → dining table(13) | livingroom_0 | 否 |

这份规划数据给的是初始关系。具体三维坐标应从选定场景读取或另行配置。
