# Philips 2021 Monitor 具体音效说明

本文件说明 `philips_2021/monitor.py` 中的监护仪音效如何合成，以及各类音效适合模拟的临床场景。这里的场景说明用于仿真和原型设计，不应替代真实设备配置、医院报警策略或厂商说明书。

## 报警优先级合成模型

本项目对 `source/updated_sound_high.wav`、`source/updated_sound_medium.wav`、`source/updated_sound_low.wav` 做了频谱、窄带包络和周期分析，得到以下近似模型。

### High alarm

用途：高优先级、需要立即处理的红色报警。适合模拟可能危及生命的事件，例如室颤、室速、心搏停止、极端低氧饱和度、严重心动过缓/过速、严重呼吸暂停等。具体触发条件应由监护仪配置和医院策略决定。

合成参数：

- 基音：`960 Hz`
- 强三次谐波：`2880 Hz`
- 谐波幅度：基音约 `0.82`，三次谐波 `1.0`
- 单次循环周期：`1000 ms`
- 默认完整报警：初始延迟 `500 ms`，重复 `7` 次
- 包络：约 `48 ms` 平滑上升，约 `230 ms` 保持，随后平滑衰减到周期末

输出文件：

- `philips_2021_alarm_high.wav`
- `philips_2021_alarm_high_loop_once.wav`

### Medium alarm

用途：中优先级报警，通常用于需要及时关注但未必立即危及生命的生理参数异常。例如血氧下降但未达到极端阈值、心率超限、呼吸频率异常、血压或其他监测参数越限等。

合成参数：

- 主频：`720 Hz`
- 音色：近似纯音
- 有声音调长度：`1200 ms`
- 重复周期：`4000 ms`
- 默认完整报警：初始延迟 `500 ms`，重复 `5` 次
- 包络：约 `34 ms` 平滑上升，短保持后在约 `1.1-1.2 s` 内衰减到接近零，之后为静音

输出文件：

- `philips_2021_alarm_medium.wav`
- `philips_2021_alarm_medium_loop_once.wav`

### Low alarm

用途：低优先级或提示性报警，适合模拟需要知晓但紧急程度较低的状态，例如轻度参数越限、提示性生理报警、部分低紧急度技术状态等。真实设备中低优先级、技术报警和 INOP 的分类可能因型号和配置不同而变化。

合成参数：

- 主频：`480 Hz`
- 音色：近似纯音
- 有声音调长度：`1700 ms`
- 重复周期：`6000 ms`
- 默认完整报警：初始延迟 `500 ms`，重复 `4` 次
- 包络：约 `55 ms` 平滑上升，约 `340 ms` 保持，随后在约 `1.5-1.7 s` 内衰减到接近零，之后为静音

输出文件：

- `philips_2021_alarm_low.wav`
- `philips_2021_alarm_low_loop_once.wav`

## Loop 文件说明

`*_loop_once.wav` 文件只包含一个完整循环周期，不包含初始 500 ms 延迟。

- high loop：`1.0 s`
- medium loop：`4.0 s`
- low loop：`6.0 s`

medium 和 low 的 loop 文件包含“有声音调 + 周期静音”。这样在游戏引擎、交互原型或仿真系统中循环播放时，重复间隔与完整报警周期一致。

## 辅助提示音

这些声音不是从 Philips 2021 报警样本直接测得，而是为了项目使用方便，按相同音色家族合成的辅助音。

### SpO2 pulse

方法：根据血氧饱和度映射音高，血氧越低音高越低。音色使用短、圆滑的近似纯音。

输出文件：

- `philips_2021_spo2_98_hr72.wav`
- `philips_2021_spo2_90_hr110.wav`

### QRS beep

方法：使用短促的 `720 Hz` 附近纯音，按心率间隔重复。用于模拟心电 QRS 提示音。

输出文件：

- `philips_2021_qrs_hr75.wav`

### UI prompts

方法：使用同一声学家族的短提示音，分别表示确认、错误和按键反馈。

输出文件：

- `philips_2021_prompt_ok.wav`
- `philips_2021_prompt_error.wav`
- `philips_2021_key.wav`

## 生成方法

在项目根目录运行：

```powershell
python -m philips_2021.output
```

输出目录：

```text
output/philips/monitor
```

## 参考资料

- Philips Sounds technology: https://www.usa.philips.com/healthcare/technology/patient-monitoring-sounds
- User-Centered Redesign of Monitoring Alarms, Healthcare 2025: https://www.mdpi.com/2227-9032/13/23/3033
- 本项目本地分析样本：`source/updated_sound_high.wav`、`source/updated_sound_medium.wav`、`source/updated_sound_low.wav`
