# 结构化镜头文档

需要脚本检查或交给其他制作步骤时，保存 `board.json`。顶层包含 `version: 1`、`story`、`style_id`、`duration_seconds`、`aspect_ratio`、`camera_form`、`panel_count`、`characters`、`scenes`、`shots`。视觉编号从当前47张卡选择；镜头形式是 `cut` 或 `one_take`。

人物条目有 `id` 和 `description`；场景条目有 `id`、`layout`和`light`。每个镜头有 `id`、`start`、`end`、`scene_id`、`character_ids`、`decisive_frame`、`framing`、`camera`、`state_before`、`state_after`、`image_prompt`、`video_prompt`与`audio`。

时间以秒记录，从0开始，各镜相接，最后一个结束于总时长。格数等于镜头数。关键画面写静止时刻，动态指令再写动作与机位变化。

前后状态用平铺键值记录，例如 `phone.holder: A`、`phone.hand: right`、`plate.location: table`。后镜开始继承前镜结束，变化需要在该镜的 `explained_changes` 里用同一个键解释具体动作或时间变化。

运行 `python scripts/validate_board.py board.json` 检查人物和场景引用、编号、时间、格数与状态交接。通过检查说明文档可交接，不代表画面或视频已生成。
