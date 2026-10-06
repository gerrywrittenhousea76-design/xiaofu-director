# board.json 合约

顶层包含 `version`（1）、`story`、`style_id`（S01–S37）、`duration_seconds`、`aspect_ratio`、`camera_form`（cut或one_take）、`panel_count`、`characters`、`scenes`、`shots`。

人物条目：`id`、`description`。场景条目：`id`、`layout`、`light`。镜头条目：`id`、`start`、`end`、`scene_id`、`character_ids`、`decisive_frame`、`framing`、`camera`、`state_before`、`state_after`、`image_prompt`、`video_prompt`、`audio`。

时间从0开始，所有镜头连续、无重叠、无空洞，最后结束于总时长。总格数等于镜头数，每镜选择一个静止关键画面；一镜到底表示采样关键帧，镜头说明应包含连贯路径而不能安排切镜。

状态是平铺的键值对象，例如 `envelope.owner: C1`、`envelope.hand: right`、`envelope.condition: sealed`。同一场景的后镜开始状态需继承前镜结束状态。删除、增加或改变状态必须在后镜 `explained_changes` 对象里用同名键解释；时间跳跃和新场景可解释变化，但“切镜了”不是道具易主的原因。

执行 `python scripts/validate_board.py board.json` 检查结构、人物与场景引用、时间、状态交接、格数和风格编号。通过代表文档检查通过；不证明生成图片内容、镜头运动、声音或审美质量。
