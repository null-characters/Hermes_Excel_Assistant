# 嵌入式应急照明系统架构速查

## META

| 属性 | 值 |
|------|-----|
| 项目 | 带电池备份的应急照明系统固件 |
| 平台 | STM32F1/F0, MM32G001/G005/SPIN0230 |
| 架构 | 四层分层架构 (App→Mid→Bsp→Hrd) |
| 调度 | QuarkTS 协作式 RTOS |
| 更新日期 | 2026-05-13 |

---

## ARCHITECTURE

### 四层架构速查表

| 层级 | 目录路径 | 职责 | 典型模块 | 对外接口 |
|------|----------|------|----------|----------|
| App | `App/Prj/[PROJECT]/` | 应用状态机、任务调度、业务逻辑 | `app_update_prj.c` | `MID_*` 宏调用 Mid 层 |
| Mid | `Mid/` + `Mid/Prj/[PROJECT]/` | 硬件抽象、功能模块中间件 | 公共: EmerFSM, SPWM, DimCtrl...<br>项目: `mid_config.c/h` | **头文件统一在 `Mid/Inc/`** |
| Bsp | `Bsp/[mcu_family]/` + `Bsp/Prj/[PROJECT]/` | 硬件驱动、GPIO/UART/ADC/PWM/Timer/Flash/RTC | 公共: `bsp_gpio.c`, `bsp_usart.c`...<br>项目: `bsp_config.c/h`, `bsp_interrupt.c` | `BSP_*` 函数供 Mid 调用 |
| Hrd | `Hrd/[mcu_family]/` | HAL 库、启动代码、链接脚本 | STM32 HAL, MM32 HAL, `*.s`, `*.icf` | 供 Bsp 调用，不直接对外 |

### 核心架构模式

| 模式 | 说明 | 示例 |
|------|------|------|
| **基于宏的抽象** | 跨层通信通过宏定义 | `MID_LED_UPDATE() → mid_led_update() → BSP_GPIO_WRITE()` |
| **基于项目的配置** | 每个产品变体三处配置 | `App/Prj/[PROJECT]/`, `Mid/Prj/[PROJECT]/`, `Bsp/Prj/[PROJECT]/` |
| **配置数组硬件抽象** | 硬件在结构化数组中定义 | `GpioConfig gpio_configs[GPIO_NAME_MAX]` |
| **上下文结构体** | 模块间传递上下文 | `AppUpdateContext_t`, `MidLedContext_t` |

---

## MODULE_INDEX

### 应用层 (App)

| 模块名 | 文件路径 | 职责 | 关键接口 |
|--------|----------|------|----------|
| app_update_prj | `App/Prj/[PROJECT]/app_update_prj.c` | 主状态机、任务调度 | `appUpdateTask_Callback`, `pwrcalcTask_Callback` |

### 中间层 (Mid)

| 模块名 | 文件路径 | 职责 | 关键接口 |
|--------|----------|------|----------|
| EmerFSM | `Mid/EmerFSM/mid_emergency_fsm_simple.c` | 应急状态机 (NONE→SIMU→REAL→FAULT) | `mid_emergency_fsm_step()` |
| SPWM | `Mid/SPWM/mid_spwm_ctrl.c` | 正弦 PWM 控制、逆变器输出 | `SPWM_PhaseControl()` |
| DimCtrl | `Mid/DimCtrl/mid_dim_ctrl.c` | LED 亮度调光 | `mid_dim_ctrl_set()` |
| CheckBat | `Mid/CheckBat/mid_check_bat.c` | 电池电压监控、ADC→电压转换 | `mid_check_bat_voltage()` |
| CheckAc | `Mid/CheckAc/mid_check_ac.c` | 市电检测、20ms采样×20次滤波 | `mid_check_ac_status()` |
| Key | `Mid/Key/mid_key.c` | 按键检测 | `mid_key_scan()` |
| Led | `Mid/Led/mid_led.c` | LED 状态控制 | `mid_led_update()` |
| Lpf | `Mid/Lpf/mid_lpf.c` | 低通滤波 | `mid_lpf_calc()` |
| Swf | `Mid/Swf/mid_swf.c` | 滑动窗口滤波 | `mid_swf_calc()` |
| AwcPi | `Mid/AwcPi/mid_awc_pi.c` | 功率调节 PI 控制器 | `mid_awc_pi_update()` |
| BlueTooth | `Mid/BlueTooth/` | 蓝牙通信 | Bsp UART |
| Ir | `Mid/Ir/` | 红外通信 | Bsp UART/Timer |
| QuarkTS | `Mid/QuarkTS/` | 协作式 RTOS | `MID_QOS_ADD_TASK()` |

> **注**：Mid 层各模块的**头文件统一在 `Mid/Inc/`**，不在各子文件夹内。

### 板级支持层 (Bsp)

| 模块名 | 文件路径 | 职责 | 关键接口 |
|--------|----------|------|----------|
| bsp_gpio | `Bsp/[mcu_family]/bsp_gpio.c/h` | GPIO 配置和控制 | `BSP_GPIO_WRITE()`, `BSP_GPIO_READ()` |
| bsp_usart | `Bsp/[mcu_family]/bsp_usart.c/h` | UART 通信 (DMA) | `BSP_USART_SEND()`, `BSP_USART_RECV()` |
| bsp_adc | `Bsp/[mcu_family]/bsp_adc.c/h` | ADC 采样 | `BSP_ADC_GET_VALUE()` |
| bsp_half_pwm | `Bsp/[mcu_family]/bsp_half_pwm.c/h` | 半桥 PWM (逆变器) | `BSP_HALF_PWM_SET()` |
| bsp_sig_pwm | `Bsp/[mcu_family]/bsp_sig_pwm.c/h` | 单路 PWM (调光) | `BSP_SIG_PWM_SET()` |
| bsp_timer | `Bsp/[mcu_family]/bsp_timer.c/h` | 定时器/中断管理 | `BSP_TIMER_INIT()` |
| bsp_flash | `Bsp/[mcu_family]/bsp_flash.c/h` | 非易失性存储 | `BSP_FLASH_WRITE()`, `BSP_FLASH_READ()` |
| bsp_rtc | `Bsp/[mcu_family]/bsp_rtc.c/h` | 实时时钟 | `BSP_RTC_GET_TIME()` |

### 项目特定配置 (Prj)

| 层级 | 文件路径 | 职责 | 关键内容 |
|--------|----------|------|----------|
| App | `App/Prj/[PROJECT]/app_update_prj.c` | 应用逻辑、状态机 | 任务调度、业务流程 |
| Mid | `Mid/Prj/[PROJECT]/mid_config.c/h` | 功能参数配置 | 电池阈值、功率目标、滤波参数 |
| Bsp | `Bsp/Prj/[PROJECT]/bsp_config.c/h` | 硬件参数配置 | GPIO 引脚映射、外设配置 |
| Bsp | `Bsp/Prj/[PROJECT]/bsp_interrupt.c` | 中断处理 | HAL 回调、ISR 处理 |
| Bsp | `Bsp/Prj/[PROJECT]/bsp_config_name.h` | 枚举定义 | GPIO_NAME_*, ADC_NAME_* |

### 公共接口

| 配置项 | 文件路径 | 说明 |
|--------|----------|------|
| 中间层API | `Mid/Inc/mid_remap.h` | 统一宏定义 `MID_QOS_ADD_TASK`, `MID_LED_UPDATE` 等 |

---

## STATE_MACHINE

### 应急状态机

```
NONE ──(市电断)──> SIMU ──(确认停电)──> REAL ──(故障)──> FAULT
  ↑                   │                   │
  └───────────────────┴───────────────────┘
                   (市电恢复)
```

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| NONE | 市电存在，电池充电 | 默认状态 |
| SIMU | 模拟应急（测试模式） | 用户触发测试 |
| REAL | 实际停电，电池放电 | 市电断开确认 |
| FAULT | 检测到错误 | 过压/短路/电池故障 |

**状态转换依赖**：
- `ac_in_flag`：市电检测
- `bat_low_flag`：电池电压低
- `bat_state`：电池状态
- `short_load_flag`/`over_load_flag`/`no_load_protect_flag`：故障标志

### LED 状态指示

| LED 状态 | 含义 |
|----------|------|
| 绿灯常亮 | 电池满电，市电存在 |
| 红灯常亮 | 电池低电，市电存在 |
| 绿灯闪烁(1Hz) | 测试模式激活 |
| 红灯闪烁(4Hz) | 输出故障（短路/过载/空载） |
| 红灯闪烁(2Hz) | 电池故障（开路） |
| 关闭 | 低电池停电 |

---

## CALL_CHAINS

### 关键调用链路

| 场景 | 调用链路 | 层穿透 | 时序约束 |
|------|----------|--------|----------|
| LED更新 | `MID_LED_UPDATE()` → `mid_led_update()` → `BSP_GPIO_WRITE()` | App→Mid→Bsp | - |
| 市电检测 | `MID_CHECK_AC()` → `mid_check_ac()` → `BSP_GPIO_READ()` → 20次滤波 | App→Mid→Bsp | 400ms 确认 |
| 电池监控 | `MID_CHECK_BAT()` → `mid_check_bat_voltage()` → `BSP_ADC_GET_VALUE()` | App→Mid→Bsp | 1ms 采样 |
| 功率计算 | ADC采样 → Lpf滤波 → DFT基波提取 → THD校正 → 功率因数计算 | Bsp→Mid→App | 1ms→16ms 循环 |
| PWM逆变 | `TIM1_CC_IRQHandler` → `SPWM_PhaseControl()` | Bsp ISR→Mid | **31.25μs** |
| 调光控制 | `MID_DIM_CTRL_SET()` → `BSP_SIG_PWM_SET()` | App→Mid→Bsp | - |

### 关键时序路径

| 路径 | 周期 | 说明 |
|------|------|------|
| ADC → 滤波 → 功率计算 | 1ms → 16ms | 稳定的功率读数 |
| PWM ISR | 31.25μs (~32kHz) | **必须在周期内完成** |
| 看门狗喂狗 | ≤200ms | `iwdgFeedTask` |
| 市电检测 | 20ms×20次 = 400ms | 确认时间 |

---

## HARDWARE

### 必需外设

| 外设 | 用途 | 说明 |
|------|------|------|
| TIM1 | 逆变器半桥 PWM | 互补输出 |
| TIM3 | 调光 PWM / ADC 触发 | - |
| TIM2 | 红外解码 | 可选 |
| ADC1 | 多通道采样 | VBAT, VBUS, VOUT, IOUT |
| USART1/2/3 | 调试/蓝牙/协议 | DMA 传输 |
| DMA | ADC 连续转换, UART | - |
| IWDG | 独立看门狗 | 200ms 喂狗 |
| Flash | 参数存储 | 电池校准、运行时间 |

### GPIO 命名约定

| 枚举名 | 用途 |
|--------|------|
| `GPIO_NAME_KEY_TEST` | 手动测试按钮 |
| `GPIO_NAME_TEST_AC` | 模拟市电故障 |
| `GPIO_NAME_BOOST_ON` | 启用升压转换器 |
| `GPIO_NAME_RELAY_EMER` | 应急输出继电器 |
| `GPIO_NAME_INV_OVLD` | 逆变器过载检测 |
| `GPIO_NAME_BAT_CTRL` | 电池供电控制 |
| `GPIO_NAME_LAMP_GREEN/RED` | 状态 LED |

### 多 MCU 支持

| MCU 系列 | 特点 | 说明 |
|----------|------|------|
| STM32F1xx | 高性能 | 72MHz, 64K+ flash |
| STM32F0xx | 成本优化 | - |
| MM32G001/G005 | 国产替代 | - |
| MM32SPIN0230 | 国产替代 | - |

**移植步骤**：
1. HAL 库添加到 `Hrd/[mcu_family]/`
2. BSP 驱动实现到 `Bsp/[mcu_family]/`
3. 项目配置到 `Bsp/Prj/[PROJECT]/bsp_config.c`

---

## POWER_CALC

### 功率计算流程

```
ADC采样(32kHz) → Lpf滤波 → DFT基波提取 → THD校正 → 功率因数计算 → 线性回归补偿
```

### 关键公式

| 参数 | 公式/值 |
|------|---------|
| 线性回归补偿 | `p_real = 0.001738 * p_active_raw - 315.699 * pf_final + 194.442` |
| 波峰因数(阻性负载) | ≈1.41 |
| 功率因数范围 | 0.5 - 1.0 |

### 调试变量

| 变量 | 位置 | 说明 |
|------|------|------|
| `debug_test.cf_val` | `app_update_prj.c` | 波峰因数 |
| `debug_test.pf_val` | `app_update_prj.c` | 功率因数 |
| `debug_test.p_real` | `app_update_prj.c` | 实际功率(W) |

---

## BATTERY

### 电池管理

| 项目 | 说明 |
|------|------|
| 化学成分 | LiFePO4, Li-ion |
| 电压监控 | ADC + 分压电阻(470K/47K) |
| 状态检测 | `BAT_OPEN_WIRE`, `BAT_UNDER_VOLT`, `BAT_LOW_VOLT`, `BAT_BLINK_VOLT`, `BAT_FULL_VOLT` |
| 配置位置 | `Mid/Prj/[PROJECT]/mid_config.c` → `bat_volt_params[]` |

### 故障代码

| 故障代码 | 变量 | 触发条件 |
|----------|------|----------|
| 电池欠压 | `BatUnderFlag` | 电池电压过低 |
| 电池断开 | `BatOpenFlag` | 电池断开 |
| 输出过载 | `OutOverLoadFlag` | 输出功率超阈值 |
| 输出短路 | `OutShortFlag` | 输出短路 |
| 无负载 | `NoOutFlag` | 应急期间无负载 |

---

## MODIFY_GUIDE

### 场景A：新增产品变体

| 步骤 | 操作 | 目标路径 |
|------|------|----------|
| A1 | 复制现有项目文件夹 | `App/Prj/`, `Mid/Prj/`, `Bsp/Prj/` |
| A2 | 修改硬件配置 | `Bsp/Prj/[NEW]/bsp_config.c/h` |
| A3 | 调整功能参数 | `Mid/Prj/[NEW]/mid_config.c/h` |
| A4 | 实现应用逻辑 | `App/Prj/[NEW]/app_update_prj.c` |
| A5 | 如需新电池状态 | 更新 `basedef.h` 枚举 |

### 场景B：修改PWM/功率控制

| 模块 | 文件路径 | 修改内容 |
|------|----------|----------|
| SPWM逻辑 | `Mid/SPWM/mid_spwm_ctrl.c` | 正弦波生成参数 |
| 调光控制 | `Mid/DimCtrl/mid_dim_ctrl.c` | 亮度曲线 |
| PI控制器 | `Mid/AwcPi/mid_awc_pi.c` | Kp, Ki 参数 |
| 功率计算 | `App/Prj/[PROJECT]/app_update_prj.c` → `pwrcalcTask_Callback()` | 功率计算算法 |

### 场景C：调试功率测量

| 检查项 | 文件位置 | 变量/宏 |
|--------|----------|----------|
| 启用日志 | `basedef.h` | `ULOG_ENABLED` |
| 波峰因数 | `app_update_prj.c` | `debug_test.cf_val` |
| 功率因数 | `app_update_prj.c` | `debug_test.pf_val` |
| 实际功率 | `app_update_prj.c` | `debug_test.p_real` |

---

## CONSTRAINTS

### 硬约束清单

| 约束类型 | 规则 | 示例 |
|----------|------|------|
| 前缀命名 | 中间层 `MID_*` 宏 / `mid_*` 实现 | `MID_LED_UPDATE`, `mid_led_update()` |
| 前缀命名 | BSP层 `BSP_*` 宏 / `bsp_*` 实现 | `BSP_GPIO_WRITE`, `bsp_gpio_write()` |
| 配置分离 | 禁止在应用代码硬编码硬件细节 | 使用 `bsp_config.c` 配置文件 |
| 宏保护 | 特性标志控制编译 | `USE_BLUE_TOOTH`, `USE_IR_REMOTE`, `ULOG_ENABLED` |
| 枚举后缀 | 所有枚举有 `_t` 后缀 | `GPIO_Name_t`, `Bat_State_t` |
| 上下文模式 | 回调使用上下文结构体 | `AppUpdateContext_t`, `MidLedContext_t` |
| PWM时序 | ISR必须在 31.25μs 内完成 | `TIM1_CC_IRQHandler` |
| 看门狗 | 喂狗间隔 ≤200ms | `iwdgFeedTask` |

### BSP 初始化规则

> 对于 `FlyBack_Inv_103` 类项目：尽量不走 `bsp_remap` 的 GPIO/ADC 初始化宏；GPIO/ADC 结构体沿用 `GpioConfig/AdcConfig`，但初始化逻辑用 HAL 直配。

---

## BUILD_SYSTEM

### 构建配置

| 项目 | 说明 |
|------|------|
| IDE | IAR EWARM 或 Keil MDK（项目文件在此目录外） |
| 配置方式 | 纯头文件配置 (`bsp_config.h`, `mid_config.h`) |
| 条件编译 | 预处理器定义控制 |

### 构建设置

1. 定义 MCU 类型宏（如 `STM32F103C8`）
2. 设置包含路径：`App/Inc`, `Mid/Inc`, `Bsp/[mcu_family]`, `Hrd/[mcu_family]`
3. 链接目标 MCU 的 HAL 库
4. 配置项目特定的定义（电池类型、功能）

---

## AUTOMATION

### GCC + J-Link + RTT 自动化验证

当需求明确要求使用 **GCC + J-Link + RTT** 时：

| 项目 | 路径/命令 |
|------|-----------|
| 编译入口 | `devtools/build/GM480-277_VI/` |
| 产物 | `devtools/build/GM480-277_VI/output/GM480-277_VI.elf` |
| J-Link 设备 | `STM32F103C8` |
| 一键执行 | `pwsh .\devtools\automation\scripts\mcu-hil\mcu-rtt-heartbeat.ps1 -Target GM480-277_VI -DurationSec 7` |

### RTT 验收标准

- 烧录成功（`jlink-flash-gdb` 完成 `load`）
- RTT 日志包含 `[BOOT] RTT ready`
- 周期性心跳至少 2 行

---

## QUICK_REF

### 常用命令速查

```c
// 启用日志
#define ULOG_ENABLED 1  // basedef.h

// 任务注册
MID_QOS_ADD_TASK(&lpfTask, lpfTask_Callback, qMedium_Priority, 0.001f, qPeriodic, qEnabled, &appContext);

// GPIO 操作
MID_LED_UPDATE() → BSP_GPIO_WRITE(GPIO_NAME_LAMP_GREEN, state)

// ADC 读取
BSP_ADC_GET_VALUE(ADC_NAME_VBAT) → 分压换算
```

### 文件定位速查

| 需求 | 位置 |
|------|------|
| 修改硬件引脚 | `Bsp/Prj/[PROJECT]/bsp_config.c` |
| 修改电池阈值 | `Mid/Prj/[PROJECT]/mid_config.c` |
| 修改应用逻辑 | `App/Prj/[PROJECT]/app_update_prj.c` |
| 修改功率算法 | `App/Prj/[PROJECT]/app_update_prj.c` → `pwrcalcTask_Callback()` |
| 修改 SPWM | `Mid/SPWM/mid_spwm_ctrl.c` |
| 添加新模块 | `Mid/[Module]/`
