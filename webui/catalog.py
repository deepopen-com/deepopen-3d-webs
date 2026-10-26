"""示例场景目录（中文，约十条以上）。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .paths import EXAMPLES_DIR


@dataclass
class SceneExample:
    id: str
    title: str
    category: str
    image: str
    prompt: str
    negative: str
    gen_path: str
    render_path: str
    seed: int
    steps: int
    model: str
    updated_at: str


DEFAULT_NEG = "相框, 边框, 简单色块, 不一致, 人物, 人脸, 低质量, 模糊"

# 生成轨迹 / 渲染轨迹中文映射
GEN_PATH_LABELS = {
    "环顾四周": "lookaround",
    "俯视环绕": "lookdown",
    "原地旋转360": "rotate360",
}
GEN_PATH_REVERSE = {v: k for k, v in GEN_PATH_LABELS.items()}

RENDER_PATH_LABELS = {
    "来回推进": "back_and_forth",
    "经典环绕": "llff",
    "轻微晃动": "headbanging",
}
RENDER_PATH_REVERSE = {v: k for k, v in RENDER_PATH_LABELS.items()}

MODEL_LABELS = {
    "标准模型 SD1.5": "SD1.5 (default)",
    "炽热驱动 V11m": "Blazing Drive V11m",
    "写实视觉 V5.1": "Realistic Vision V5.1",
    "卡通皮克斯 V5": "RealCartoon-Pixar V5",
}
MODEL_REVERSE = {v: k for k, v in MODEL_LABELS.items()}


def _img(name: str) -> str:
    p = EXAMPLES_DIR / name
    return str(p) if p.exists() else ""


SCENES: List[SceneExample] = [
    SceneExample(
        "anime_lake", "动漫湖畔小屋", "动漫",
        _img("Image015_animelakehouse.jpg"),
        "动漫风格, 高清, 湖上小船, 湖边树木与岩石, 小屋与码头",
        DEFAULT_NEG, "俯视环绕", "来回推进", 1, 40, "标准模型 SD1.5", "2026-10-12",
    ),
    SceneExample(
        "fantasy_float", "奇幻浮空城", "奇幻",
        _img("Image003_fantasy.jpg"),
        "色彩绚丽的浮空社区城市, 云雾之上, 奇幻植物与森林, 漂浮岛屿与光球, 细节丰富",
        DEFAULT_NEG, "环顾四周", "来回推进", 30, 40, "标准模型 SD1.5", "2026-10-11",
    ),
    SceneExample(
        "modern_kitchen", "现代温馨厨房", "室内",
        _img("image020.png"),
        "高清摄影厨房, 木地板, 面向花园的小窗, 包豪斯家具, 高挑天花板, 米蓝鲑鱼色调, 温馨氛围",
        DEFAULT_NEG, "原地旋转360", "轻微晃动", 1, 40, "标准模型 SD1.5", "2026-10-10",
    ),
    SceneExample(
        "noir_room", "黑色电影房间", "风格化",
        _img("girl.jpg"),
        "昏暗凌乱房间, 黑色电影风格, 室内, 酒瓶, 外套, 窗户, 景深, 沙发, 桌子, 椅子",
        DEFAULT_NEG, "环顾四周", "来回推进", 10, 25, "炽热驱动 V11m", "2026-10-09",
    ),
    SceneExample(
        "desert_ruin", "荒漠末日废墟", "末日",
        _img("ruin.png"),
        "沙漠中的末日后城市废墟, 沙尘与残垣断壁, 电影感光影",
        DEFAULT_NEG, "环顾四周", "来回推进", 4, 25, "炽热驱动 V11m", "2026-10-08",
    ),
    SceneExample(
        "cozy_doge", "狗狗温馨客厅", "室内",
        _img("doge.png") or _img("doge.jpg"),
        "温馨舒适的客厅, 柔和灯光, 柔软沙发与地毯",
        DEFAULT_NEG, "环顾四周", "来回推进", 10, 25, "写实视觉 V5.1", "2026-10-07",
    ),
    SceneExample(
        "xmas_living", "圣诞客厅", "节日",
        _img("christmas.png"),
        "圣诞节温馨客厅, 圣诞树与彩灯, 壁炉暖光, 节日氛围",
        DEFAULT_NEG, "环顾四周", "来回推进", 3, 25, "写实视觉 V5.1", "2026-10-06",
    ),
    SceneExample(
        "elf_forest", "精灵深林", "奇幻",
        _img("elf.png") or _img("elf.jpg"),
        "宁静幽深的精灵森林, 雾气与光斑, 苔藓与古树",
        DEFAULT_NEG, "环顾四周", "来回推进", 10, 25, "卡通皮克斯 V5", "2026-10-05",
    ),
    SceneExample(
        "fruit_market", "鲜果市集", "街景",
        _img("Image005_fruitmarket.jpg"),
        "热闹的水果市场, 摊位与鲜艳果实, 阳光洒落, 生活气息",
        DEFAULT_NEG, "环顾四周", "经典环绕", 8, 30, "标准模型 SD1.5", "2026-10-04",
    ),
    SceneExample(
        "space_station", "空间站走廊", "科幻",
        _img("Image009_spacestation.jpg"),
        "科幻空间站内部走廊, 金属结构与舷窗星空, 冷暖对比灯光",
        DEFAULT_NEG, "原地旋转360", "经典环绕", 12, 35, "标准模型 SD1.5", "2026-10-03",
    ),
    SceneExample(
        "waterfall", "山谷瀑布", "自然",
        _img("Image008_waterfall.jpg"),
        "山谷瀑布, 水雾与岩石, 翠绿植被, 自然光影",
        DEFAULT_NEG, "俯视环绕", "来回推进", 7, 30, "标准模型 SD1.5", "2026-10-02",
    ),
    SceneExample(
        "modern_villa", "现代别墅外景", "建筑",
        _img("Image002_modernvilla.jpg"),
        "现代极简别墅外景, 大玻璃窗, 泳池与庭院, 黄昏暖光",
        DEFAULT_NEG, "环顾四周", "经典环绕", 5, 30, "写实视觉 V5.1", "2026-10-01",
    ),
    # 以下为仓库自带、此前未挂入图库的官方示例图
    SceneExample(
        "lego_city", "乐高城市街景", "风格化",
        _img("Image011_lego.jpg"),
        "乐高积木城市, 商店与街道, 路灯与车辆, 公园树木与湖泊, 高细节积木质感",
        DEFAULT_NEG, "环顾四周", "经典环绕", 9, 30, "卡通皮克斯 V5", "2026-10-12",
    ),
    SceneExample(
        "white_cat_street", "白猫街角小屋", "街景",
        _img("Image012_whitecat.jpg"),
        "街角白猫, 白色房屋与台阶, 路边树木, 灰色石砖路面",
        DEFAULT_NEG, "环顾四周", "来回推进", 6, 28, "写实视觉 V5.1", "2026-10-11",
    ),
    SceneExample(
        "anime_street", "动漫街区大道", "动漫",
        _img("Image014_animestreet.jpg"),
        "动漫风格长街, 房屋与树木, 明亮蓝天, 晴朗夏日, 高清四边",
        DEFAULT_NEG, "原地旋转360", "经典环绕", 11, 35, "标准模型 SD1.5", "2026-10-10",
    ),
    SceneExample(
        "anime_summer_home", "海景动漫居室", "动漫",
        _img("Image018_animesummerhome.jpg"),
        "日式动漫海景小屋, 榻榻米, 风中窗帘, 花束与客厅, 远眺海面",
        DEFAULT_NEG, "俯视环绕", "来回推进", 2, 35, "标准模型 SD1.5", "2026-10-09",
    ),
    SceneExample(
        "fruit_grocery", "木桌鲜果店", "街景",
        _img("Image031_fruit.jpg"),
        "杂货店木桌鲜果, 方砖地面, 木质屋顶, 桌上绿植, 高清生活场景",
        DEFAULT_NEG, "环顾四周", "轻微晃动", 14, 30, "标准模型 SD1.5", "2026-10-08",
    ),
    SceneExample(
        "magic_cabin", "森林魔法小屋", "奇幻",
        _img("cabin.png"),
        "宁静森林中的魔法师小屋, 神秘而安详",
        DEFAULT_NEG, "环顾四周", "来回推进", 8, 28, "炽热驱动 V11m", "2026-10-07",
    ),
    SceneExample(
        "wonder_island", "奇境小岛", "自然",
        _img("island.png"),
        "小小奇境岛屿, 梦幻风光",
        DEFAULT_NEG, "俯视环绕", "经典环绕", 15, 30, "标准模型 SD1.5", "2026-10-06",
    ),
]


def list_scenes() -> List[SceneExample]:
    return [s for s in SCENES if s.image]


def get_scene(scene_id: str) -> Optional[SceneExample]:
    for s in SCENES:
        if s.id == scene_id:
            return s
    return None


def scene_choices() -> List[str]:
    return [f"{s.title}（{s.category}）" for s in list_scenes()]


def scene_by_choice(choice: str) -> Optional[SceneExample]:
    for s in list_scenes():
        label = f"{s.title}（{s.category}）"
        if label == choice or s.title == choice:
            return s
    return None


def catalog_table_rows():
    rows = []
    for s in list_scenes():
        rows.append([
            s.title,
            s.category,
            s.model,
            s.gen_path,
            s.render_path,
            s.updated_at,
            Path(s.image).name if s.image else "-",
        ])
    return rows
