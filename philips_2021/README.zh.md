# Philips 2021 音效设计说明

本目录用于合成 Philips 2021 风格的监护仪音效，重点是 `monitor.py` 中的床旁监护器报警和提示音。当前实现是面向仿真、交互原型和音效预览的近似合成，不包含也不再分发任何飞利浦官方音频采样。

## 设计依据

Philips 官方对 Philips Sounds 的公开说明强调，新的监护仪声音设计目标不是简单提高声压或复制传统 IEC 蜂鸣，而是围绕临床人员和患者重新设计医院声景，减轻传统报警声音的尖锐感，降低报警疲劳，同时保持医护人员对报警的辨识能力。

第三方临床研究也描述了 Philips 与 Sen Sound 合作改进报警音的方向：低、中优先级报警主要降低刺耳感，高优先级报警仍保留足够显著、能快速吸引注意的特征。该研究的补充材料提供了传统与 refined Philips alarm sounds 的音频样本，本项目使用你放置在 `source/` 下的样本做频谱和包络分析，再将结果转为可调参数。

## 总体设计理念

1. **按优先级区分，而不是按 IEC 旋律区分**
   Philips 2021 风格在这些样本中表现为稳定的单频或少量谐波事件，通过频率、重复周期、音色亮度和包络区别 high / medium / low，而不是 IEC 60601 的五音旋律结构。

2. **降低中低等级报警的听觉负担**
   `medium` 和 `low` 使用近似纯音，尾部平滑衰减后进入静音间隔。这样避免长时间可听拖尾，也避免持续占据环境声场。

3. **高等级报警保留强显著性**
   `high` 使用 960 Hz 基音和更强的 2880 Hz 三次谐波，使其更容易从背景中突出。它仍然比中低等级更尖锐、更密集，但包络保持平滑，避免硬切点击。

4. **包络从零到峰值再平滑回零**
   所有报警事件都使用平滑攻击、保持和指数/余弦组合衰减。medium 和 low 的音调尾部不占满整个重复周期，后半段是真静音；high 的尾部接近占满 1 秒周期。

5. **合成优先于采样**
   项目只保留参数化合成逻辑。这样可以复现实验、调整音色、生成不同长度和 loop 版本，同时避免依赖受版权保护的原始声音。

## 目录结构

- `monitor.py`：Philips 2021 监护仪声音合成器。
- `output.py`：快速生成本目录所有预览音频。
- `monitor/README.zh.md`：具体 monitor 音效的中文说明。
- `monitor/README.en.md`：具体 monitor 音效的英文说明。

## 快速生成

在项目根目录运行：

```powershell
python -m philips_2021.output
```

生成结果位于：

```text
output/philips/monitor
```

也可以运行项目根目录的总入口：

```powershell
python output.py
```

## 参考资料

- Philips Sounds technology: https://www.usa.philips.com/healthcare/technology/patient-monitoring-sounds
- User-Centered Redesign of Monitoring Alarms, Healthcare 2025: https://www.mdpi.com/2227-9032/13/23/3033
- 本项目本地分析样本：`source/updated_sound_high.wav`、`source/updated_sound_medium.wav`、`source/updated_sound_low.wav`
