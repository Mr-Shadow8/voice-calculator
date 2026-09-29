# -*- coding: utf-8 -*-
"""
语音计算器 APK - 主程序
- 每按一个数字键,播报对应中文数字
- 按运算符,播报"加/减/乘/除"
- 按 = 号,播报"等于 X"
- 按 C 清屏,按 ⌫ 退格
依赖:Kivy + pyjnius(Android TTS)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# 设置窗口背景色(桌面调试用,APK 中不影响)
Window.clearcolor = (0.12, 0.14, 0.18, 1)


# ============== 数字转中文(用于语音播报) ==============
DIGIT_CN = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
            "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
UNIT_CN = ["", "十", "百", "千", "万", "十万", "百万", "千万", "亿"]


def _int_to_chinese(num_str):
    """整数部分字符串转中文,如 '1234' -> '一千二百三十四'"""
    num_str = num_str.lstrip("0") or "0"
    if num_str == "0":
        return "零"
    n = len(num_str)
    out = []
    for i, ch in enumerate(num_str):
        pos = n - i - 1  # 从右数第几位
        digit = DIGIT_CN[ch]
        unit = UNIT_CN[pos] if pos < len(UNIT_CN) else ""
        if ch == "0":
            # 连续 0 只读一个零,末尾的 0 不读
            if out and not out[-1].endswith("零"):
                out.append("零")
            continue
        out.append(digit + unit)
    s = "".join(out).rstrip("零")
    # 修正"一十"开头简写为"十"
    if s.startswith("一十"):
        s = "十" + s[2:]
    return s


def num_to_chinese(s):
    """
    把数字字符串转中文读法,支持负数和小数。
    例: '123' -> '一百二十三'
        '-5'  -> '负五'
        '1.5' -> '一点五'
        '0'   -> '零'
    """
    s = str(s).strip()
    if not s:
        return ""
    negative = s.startswith("-")
    if negative:
        s = s[1:]
    if "." in s:
        int_part, dec_part = s.split(".", 1)
        int_cn = _int_to_chinese(int_part) if int_part else ""
        dec_cn = "".join(DIGIT_CN[c] for c in dec_part if c in DIGIT_CN)
        result = (int_cn + "点" + dec_cn) if int_cn else ("零点" + dec_cn)
    else:
        result = _int_to_chinese(s)
    return ("负" + result) if negative else result


# ============== Android TTS 封装(桌面降级兼容) ==============
class VoiceEngine:
    """统一语音播报接口;Android 上调用原生 TTS,桌面无引擎时静默"""

    def __init__(self):
        self._tts = None
        self._ready = False
        try:
            # Android 环境通过 pyjnius 调用 android.tts.TextToSpeech
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Locale = autoclass("java.util.Locale")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")

            self._tts = TextToSpeech(
                PythonActivity.mActivity,
                None  # InitListener 简化处理
            )
            # 设置中文
            self._tts.setLanguage(Locale.CHINESE)
            self._ready = True
        except Exception:
            # 非 Android 环境或缺少 pyjnius:静默降级
            self._tts = None
            self._ready = False

    def speak(self, text):
        """非阻塞播报;队列模式 QUEUE_FLUSH 覆盖上一次"""
        if not text:
            return
        if self._ready and self._tts is not None:
            try:
                from jnius import autoclass
                # QUEUE_FLUSH = 0,覆盖上一句,避免连按时堆积
                self._tts.speak(text, 0, None, "tts_calc")
            except Exception:
                pass
        # 桌面调试:可选打印到控制台
        # print(f"[TTS] {text}")


# ============== 计算器主界面 ==============
class CalculatorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expr = ""        # 当前表达式(纯字符串,如 "12+3")
        self.voice = VoiceEngine()

    # ---- UI 构建 ----
    def build(self):
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # 显示区
        self.display = Label(
            text="0",
            font_name="DroidSans",  # 系统字体;中文走设备默认中文字体
            font_size="60sp",
            size_hint=(1, 0.25),
            halign="right",
            valign="middle",
            color=get_color_from_hex("#FFFFFF"),
            bold=True,
        )
        self.display.bind(size=self.display.setter("text_size"))
        self.display.text_size = self.display.size

        root.add_widget(self.display)

        # 按键区 4x5
        grid = GridLayout(cols=4, spacing=4, size_hint=(1, 0.75))

        buttons = [
            ("C",  "clear",   "#E0455B"),  # 红色 - 清除
            ("⌫",  "back",    "#FFA000"),  # 橙色 - 退格
            ("%",  "percent", "#5A5F6B"),  # 灰色 - 百分比(可选)
            ("÷",  "op_div",  "#FF9500"),  # 橙色 - 运算符
            ("7",  "num",     "#3A3F4B"),
            ("8",  "num",     "#3A3F4B"),
            ("9",  "num",     "#3A3F4B"),
            ("×",  "op_mul",  "#FF9500"),
            ("4",  "num",     "#3A3F4B"),
            ("5",  "num",     "#3A3F4B"),
            ("6",  "num",     "#3A3F4B"),
            ("−",  "op_sub",  "#FF9500"),
            ("1",  "num",     "#3A3F4B"),
            ("2",  "num",     "#3A3F4B"),
            ("3",  "num",     "#3A3F4B"),
            ("+",  "op_add",  "#FF9500"),
            ("±",  "sign",    "#5A5F6B"),  # 正负号切换
            ("0",  "num",     "#3A3F4B"),
            (".",  "dot",     "#3A3F4B"),
            ("=",  "equals",  "#34C759"),  # 绿色 - 等号
        ]

        for text, action, color in buttons:
            btn = Button(
                text=text,
                font_name="DroidSans",
                font_size="32sp",
                background_color=get_color_from_hex(color),
                background_normal="",
                color=get_color_from_hex("#FFFFFF"),
                bold=True,
            )
            btn.action = action
            btn.symbol = text  # 用于显示的符号
            btn.bind(on_press=self.on_btn_press)
            grid.add_widget(btn)

        root.add_widget(grid)
        return root

    # ---- 按键事件 ----
    def on_btn_press(self, btn):
        action = btn.action
        sym = btn.symbol

        # 根据动作分发
        if action == "num":
            self._add_char(sym)
            self.voice.speak(DIGIT_CN[sym])
        elif action == "dot":
            self._add_char(".")
            self.voice.speak("点")
        elif action == "op_add":
            self._add_op("+", "加")
        elif action == "op_sub":
            self._add_op("-", "减")
        elif action == "op_mul":
            self._add_op("*", "乘")
        elif action == "op_div":
            self._add_op("/", "除")
        elif action == "equals":
            self._equals()
        elif action == "clear":
            self.expr = ""
            self.display.text = "0"
            self.voice.speak("清除")
        elif action == "back":
            if self.expr:
                self.expr = self.expr[:-1]
                self.display.text = self.expr if self.expr else "0"
            self.voice.speak("退格")
        elif action == "sign":
            # 在当前数字前加/减 负号
            self._toggle_sign()
        elif action == "percent":
            self._percent()

    # ---- 表达式操作 ----
    OPS = set("+-*/")

    def _add_char(self, ch):
        # 表达式末尾如果是运算符且输入数字,正常追加
        # 防止连续两个点
        if ch == ".":
            # 找当前数字段,判断是否已有小数点
            tail = self.expr
            for c in reversed(tail):
                if c in self.OPS:
                    break
                if c == ".":
                    return  # 当前数字已有小数点,忽略
        # 表达式为空时不能以运算符开头(除了负号)
        self.expr += ch
        self.display.text = self._format_display(self.expr)

    def _add_op(self, op_symbol, speak_word):
        # 若末尾已是运算符,先替换
        if self.expr and self.expr[-1] in self.OPS:
            self.expr = self.expr[:-1] + op_symbol
        elif self.expr:  # 必须有数字才能加运算符
            self.expr += op_symbol
        else:
            # 表达式空,只允许减号(负数)
            if op_symbol == "-":
                self.expr = "-"
            else:
                return
        self.display.text = self._format_display(self.expr)
        self.voice.speak(speak_word)

    def _equals(self):
        try:
            if not self.expr:
                return
            # 安全求值:仅允许数字与运算符
            if not all(c in "0123456789+-*/." for c in self.expr):
                return
            result = eval(self.expr, {"__builtins__": {}}, {})
            # 格式化结果:整数去 .0,浮点保留最多 8 位
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            else:
                result = round(result, 8)
            self.display.text = str(result)
            # 播报结果
            self.voice.speak("等于 " + num_to_chinese(str(result)))
            self.expr = str(result)
        except ZeroDivisionError:
            self.display.text = "错误:除零"
            self.voice.speak("错误,除数不能为零")
            self.expr = ""
        except Exception:
            self.display.text = "错误"
            self.voice.speak("表达式错误")
            self.expr = ""

    def _toggle_sign(self):
        # 切换当前操作数的正负号
        if not self.expr:
            return
        # 找最后一个运算符位置
        last_op_idx = -1
        for i, c in enumerate(self.expr):
            if c in "+-*/":
                last_op_idx = i
        if last_op_idx == len(self.expr) - 1:
            return  # 末尾是运算符,无操作数
        before = self.expr[: last_op_idx + 1]
        num = self.expr[last_op_idx + 1:]
        if num.startswith("-"):
            num = num[1:]
        else:
            num = "-" + num
        self.expr = before + num
        self.display.text = self._format_display(self.expr)
        self.voice.speak("正负号")

    def _percent(self):
        # 当前操作数 / 100
        if not self.expr or self.expr[-1] in self.OPS:
            return
        try:
            val = eval(self.expr, {"__builtins__": {}}, {}) / 100
            self.expr = str(val)
            self.display.text = self._format_display(self.expr)
            self.voice.speak("百分之")
        except Exception:
            pass

    def _format_display(self, expr):
        """把 */ 转成 × ÷ 显示更友好,− 负号保留"""
        return expr.replace("*", "×").replace("/", "÷")


if __name__ == "__main__":
    CalculatorApp().run()
